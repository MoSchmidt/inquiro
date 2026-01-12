import logging

import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.database_constants import PaperContentStatus, PaperSource
from app.core.config import settings
from app.core.deps import get_openai_provider
from app.repositories.paper_content_repository import PaperContentRepository
from app.repositories.paper_repository import PaperRepository
from app.schemas.paper_dto import PaperSummaryResponse
from app.utils.token_utils import ensure_fits_token_limit
from app.workers.queues.conversion_queue import ConversionQueue

logger = logging.getLogger("inquiro")


class PaperService:
    """Service for summarising research papers"""

    # GPT 5 nano has a max. content size of 400k tokens, combining input and output.
    # This represents a conservative estimate, leaving enough space for the prompt and output.
    MAX_INPUT_TOKENS = 280_000

    @staticmethod
    async def trigger_conversion(paper_id: int, session: AsyncSession) -> None:
        """
        Trigger PDF conversion for a paper if not already done/in-progress.

        This is a fire-and-forget operation - it enqueues the job and returns immediately.
        Used when viewing PDFs or adding papers to projects for preemptive conversion.
        """

        paper = await PaperRepository.get_paper_by_id(session, paper_id)
        if not paper or paper.source != PaperSource.ARXIV:
            return

        content = await PaperContentRepository.get_by_paper_id(session, paper_id)

        # Determine if we should enqueue
        should_enqueue = False
        retry_count = 0

        if content is None:
            # No content record - create pending and enqueue
            await PaperContentRepository.create_pending(session, paper_id)
            should_enqueue = True
        elif content.status == PaperContentStatus.PENDING:
            # Already pending but not queued - enqueue
            should_enqueue = True
        elif content.status == PaperContentStatus.FAILED:
            # Failed - retry if under max retries
            if content.retry_count < settings.DOCLING_MAX_RETRIES:
                should_enqueue = True
                retry_count = content.retry_count
            else:
                logger.warning(
                    "Paper %d: Max retries exceeded, not re-queueing", paper_id
                )

        if should_enqueue:
            queue = ConversionQueue.get_instance()
            # Don't re-queue if already pending in the queue
            if not queue.is_pending(paper_id):
                await queue.enqueue(paper_id, paper.paper_id_external, retry_count=retry_count)

    @staticmethod
    async def get_or_wait_for_markdown(paper_id: int, session: AsyncSession) -> str:
        """
        Get markdown content, waiting for conversion if in progress.

        Raises:
            HTTPException 504: If conversion times out
            HTTPException 500: If conversion failed
            HTTPException 404: If paper not found
        """
        paper = await PaperRepository.get_paper_by_id(session, paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

        if paper.source != PaperSource.ARXIV:
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported paper source '{paper.source}'. Only ARXIV is supported.",
            )

        content = await PaperContentRepository.get_by_paper_id(session, paper_id)

        # If no content or pending, trigger conversion
        if content is None or content.status == PaperContentStatus.PENDING:
            await PaperService.trigger_conversion(paper_id, session)
            content = await PaperContentRepository.get_by_paper_id(session, paper_id)

        # If failed but retryable, trigger conversion
        if content and content.status == PaperContentStatus.FAILED:
            if content.retry_count < settings.DOCLING_MAX_RETRIES:
                await PaperService.trigger_conversion(paper_id, session)
            else:
                raise HTTPException(
                    status_code=500,
                    detail="PDF conversion failed after multiple attempts. Please try again later.",
                )

        # Wait for conversion if in progress or just triggered
        queue = ConversionQueue.get_instance()
        if queue.is_pending(paper_id):
            success = await queue.wait_for_completion(paper_id)
            if not success:
                raise HTTPException(
                    status_code=504,
                    detail="PDF conversion timed out. Please try again later.",
                )

            # Refresh content from database
            content = await PaperContentRepository.get_by_paper_id(session, paper_id)

        # Check final status
        if content and content.status == PaperContentStatus.SUCCEEDED:
            if content.markdown is None:
                raise HTTPException(
                    status_code=500,
                    detail="Paper content marked as SUCCEEDED but markdown is empty.",
                )
            return str(content.markdown)

        raise HTTPException(
            status_code=500,
            detail="PDF conversion failed. Please try again later.",
        )

    @staticmethod
    async def summarise_paper(
        paper_id: int, query: str, session: AsyncSession
    ) -> PaperSummaryResponse:
        """
        Retrieves paper specified by id, gets its markdown content, and summarises it.
        Returns a summary of the specified paper.

        Uses pre-converted markdown from PaperContent (via Docling), waiting for
        conversion if it's still in progress.
        """
        try:
            # Get markdown content (waits for conversion if needed)
            pdf_text = await PaperService.get_or_wait_for_markdown(paper_id, session)

            # If the content is of excessive length, it's too big for a single request
            ensure_fits_token_limit(
                pdf_text,
                max_tokens=PaperService.MAX_INPUT_TOKENS,
                error_status=413,
                error_detail=(
                    "Paper is too long to be summarised at the moment. "
                    "Please try a shorter document."
                ),
            )

            openai_provider = get_openai_provider()
            summary_payload = await openai_provider.summarise_paper(pdf_text, query)
            return PaperSummaryResponse.model_validate(summary_payload)
        except HTTPException:
            # Re-raise HTTP exceptions (from get_or_wait_for_markdown)
            raise
        except Exception as exc:
            # Catch-all for unexpected issues (LLM errors, ...)
            logger.exception("Error summarising paper %s", paper_id)
            raise HTTPException(
                status_code=500, detail="An unexpected error occurred while summarising the paper."
            ) from exc

    @staticmethod
    async def get_paper_pdf(paper_id: int, session: AsyncSession) -> bytes:
        """
        Retrieves the PDF bytes for the specified paper.
        Used by the frontend PDF viewer.
        """
        paper = await PaperRepository.get_paper_by_id(session, paper_id)

        if not paper:
            logger.warning("Failed to find specified paper in DB: %s", paper_id)
            raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

        if paper.source != PaperSource.ARXIV:
            logger.warning("Unsupported paper source for PDF retrieval: %s", paper.source)
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported paper source '{paper.source}'. Only ARXIV is supported.",
            )

        try:
            return await PaperService._fetch_arxiv_pdf(arxiv_id=paper.paper_id_external)
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Failed to fetch arXiv paper %s: %s",
                paper.paper_id_external,
                exc,
                exc_info=True,
            )
            raise HTTPException(status_code=404, detail="Paper not found") from exc
        except httpx.RequestError as exc:
            logger.warning(
                "Network error while fetching arXiv paper %s: %s",
                paper.paper_id_external,
                exc,
                exc_info=True,
            )
            raise HTTPException(
                status_code=503,
                detail="Upstream arXiv service unavailable, please try again later.",
            ) from exc

    @staticmethod
    def arxiv_pdf_url(arxiv_id: str) -> str:
        """Get the Arxiv-PDF URL."""
        return f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    @staticmethod
    async def _fetch_arxiv_pdf(arxiv_id: str) -> bytes:
        """
        Fetch arXiv PDF and return its raw bytes.
        """

        url = PaperService.arxiv_pdf_url(arxiv_id)
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content

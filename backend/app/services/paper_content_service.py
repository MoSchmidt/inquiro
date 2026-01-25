"""Service for paper content operations."""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.database_constants import PaperSource, PaperContentStatus
from app.core.config import settings
from app.repositories.paper_content_repository import PaperContentRepository
from app.repositories.paper_repository import PaperRepository
from app.workers.queues.conversion_queue import ConversionQueue, ConversionJob

logger = logging.getLogger("inquiro")


class PaperContentService:
    """Service for triggering and waiting on paper content conversion."""

    # Polling configuration for wait_for_completion
    POLL_INITIAL_INTERVAL = 0.5  # seconds
    POLL_MAX_INTERVAL = 5.0  # seconds
    POLL_BACKOFF_FACTOR = 1.5

    @staticmethod
    async def trigger_conversion(paper_id: int, session: AsyncSession) -> bool:
        """
        Trigger PDF conversion for a paper if eligible.

        This is a fire-and-forget operation - it enqueues the job and returns
        immediately. Idempotent - safe to call multiple times.

        Returns True if job was enqueued, False if not needed.
        """
        # Validate paper
        paper = await PaperRepository.get_paper_by_id(session, paper_id)
        if not paper or paper.source != PaperSource.ARXIV:
            return False

        # Atomically get or create content record
        content, was_created = await PaperContentRepository.get_or_create_pending_atomic(
            session, paper_id
        )

        if content is None:
            logger.error("Failed to create content record for paper %d", paper_id)
            return False

        # Determine if we should enqueue
        should_enqueue = False
        retry_count = 0

        if was_created:
            # Just created - definitely enqueue
            should_enqueue = True
        elif content.status == PaperContentStatus.PENDING:
            # Already pending - enqueue in case it fell out of queue (server restart)
            should_enqueue = True
        elif content.status == PaperContentStatus.FAILED:
            # Check if retryable
            if content.retry_count < settings.DOCLING_MAX_RETRIES:
                should_enqueue = True
                retry_count = content.retry_count
            else:
                logger.warning("Paper %d: Max retries exceeded, not re-queueing", paper_id)
        elif content.status == PaperContentStatus.PROCESSING:
            # Check for stale claim (worker died)
            if content.claimed_at is not None:
                stale_threshold = datetime.now(timezone.utc) - timedelta(
                    seconds=PaperContentRepository.STALE_CLAIM_TIMEOUT_SECONDS
                )
                if content.claimed_at < stale_threshold:
                    should_enqueue = True
                    retry_count = content.retry_count
        # SUCCEEDED - no action needed

        if should_enqueue:
            queue = ConversionQueue.get_instance()
            job = ConversionJob(
                paper_id=paper_id,
                arxiv_id=paper.paper_id_external,
                retry_count=retry_count,
            )
            await queue.enqueue(job)
            return True

        return False

    @staticmethod
    async def wait_for_completion(
        paper_id: int,
        session: AsyncSession,
        timeout: Optional[float] = None,
    ) -> PaperContentStatus:
        """
        Wait for paper conversion to reach a terminal state.

        Uses database polling with exponential backoff.

        Args:
            paper_id: Paper to wait for
            session: Database session
            timeout: Max wait time (defaults to DOCLING_TIMEOUT_SECONDS)

        Returns:
            Final status (SUCCEEDED, FAILED, or current status on timeout)

        Raises:
            asyncio.TimeoutError if timeout exceeded
        """
        if timeout is None:
            timeout = float(settings.DOCLING_TIMEOUT_SECONDS)

        poll_interval = PaperContentService.POLL_INITIAL_INTERVAL
        elapsed = 0.0

        while elapsed < timeout:
            # Check current state
            is_complete, status = await PaperContentRepository.is_conversion_complete(
                session, paper_id
            )

            if is_complete:
                return status

            # Not terminal - wait and poll again
            sleep_time = min(poll_interval, timeout - elapsed)
            await asyncio.sleep(sleep_time)
            elapsed += sleep_time

            # Exponential backoff
            poll_interval = min(
                poll_interval * PaperContentService.POLL_BACKOFF_FACTOR,
                PaperContentService.POLL_MAX_INTERVAL,
            )

        # Timeout - get current status for error message
        content = await PaperContentRepository.get_by_paper_id(session, paper_id)
        current_status = content.status if content else "no record"
        raise asyncio.TimeoutError(
            f"Timeout waiting for paper {paper_id} conversion (status: {current_status})"
        )

    @staticmethod
    async def get_or_wait_for_markdown(paper_id: int, session: AsyncSession) -> str:
        """
        Get markdown content, triggering and waiting for conversion if needed.

        Raises:
            HTTPException 404: Paper not found
            HTTPException 422: Unsupported paper source
            HTTPException 500: Conversion failed
            HTTPException 504: Conversion timed out
        """
        # Validate paper
        paper = await PaperRepository.get_paper_by_id(session, paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

        if paper.source != PaperSource.ARXIV:
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported paper source '{paper.source}'. Only ARXIV is supported.",
            )

        # Check current state
        content = await PaperContentRepository.get_by_paper_id(session, paper_id)

        # If already succeeded, return immediately
        if content and content.status == PaperContentStatus.SUCCEEDED:
            if content.markdown:
                return str(content.markdown)
            raise HTTPException(
                status_code=500,
                detail="Paper content marked as SUCCEEDED but markdown is empty.",
            )

        # If permanently failed, raise error
        if content and content.status == PaperContentStatus.FAILED:
            if content.retry_count >= settings.DOCLING_MAX_RETRIES:
                raise HTTPException(
                    status_code=500,
                    detail="PDF conversion failed after multiple attempts. Please try again later.",
                )

        # Trigger conversion (idempotent - safe to call even if already processing)
        await PaperContentService.trigger_conversion(paper_id, session)

        # Wait for completion
        try:
            final_status = await PaperContentService.wait_for_completion(paper_id, session)
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail="PDF conversion timed out. Please try again later.",
            )

        # Check final result
        if final_status == PaperContentStatus.SUCCEEDED:
            # Refresh content
            content = await PaperContentRepository.get_by_paper_id(session, paper_id)
            if content and content.markdown:
                return str(content.markdown)
            raise HTTPException(
                status_code=500,
                detail="Paper content marked as SUCCEEDED but markdown is empty.",
            )

        raise HTTPException(
            status_code=500,
            detail="PDF conversion failed. Please try again later.",
        )

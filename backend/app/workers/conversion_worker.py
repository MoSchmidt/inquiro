"""Background worker for processing PDF conversion jobs."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import select, update

from app.constants.database_constants import PaperContentStatus
from app.core.config import settings
from app.core.database import async_session_local
from app.models.paper_content import PaperContent
from app.services.docling_service import DoclingConverter
from app.services.paper_service import PaperService

if TYPE_CHECKING:
    from app.workers.queues.conversion_queue import ConversionJob, ConversionQueue

logger = logging.getLogger("inquiro")


async def conversion_worker(queue: ConversionQueue, worker_id: int) -> None:
    """
    Background worker that processes PDF conversion jobs.

    Each worker:
    1. Gets a job from the queue
    2. Applies any delay (for retry backoff)
    3. Claims the job atomically in the database
    4. Fetches the PDF and converts to markdown
    5. Updates the database with results or handles failures
    """
    converter = DoclingConverter()

    while queue.running:
        try:
            # Get next job (with timeout to check running status periodically)
            try:
                job = await asyncio.wait_for(queue._queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            logger.info("Worker %d: Processing paper %d", worker_id, job.paper_id)

            # Apply delay for retries (exponential backoff)
            if job.delay_seconds > 0:
                logger.info(
                    "Worker %d: Waiting %.1fs before retry for paper %d",
                    worker_id,
                    job.delay_seconds,
                    job.paper_id,
                )
                await asyncio.sleep(job.delay_seconds)

            try:
                async with async_session_local() as session:
                    # Try to claim the job atomically
                    claimed = await _try_claim_job(session, job.paper_id)
                    if not claimed:
                        logger.info(
                            "Worker %d: Paper %d already being processed, skipping",
                            worker_id,
                            job.paper_id,
                        )
                        continue

                    pdf_url = PaperService.arxiv_pdf_url(job.arxiv_id)

                    # Convert to markdown (CPU-bound, run in executor)
                    loop = asyncio.get_event_loop()
                    markdown = await loop.run_in_executor(
                        None, converter.convert_pdf_to_markdown, pdf_url
                    )

                    # Update database with successful result
                    await _mark_succeeded(session, job.paper_id, markdown)
                    logger.info("Worker %d: Completed paper %d", worker_id, job.paper_id)

            except Exception as e:
                logger.error(
                    "Worker %d: Failed paper %d: %s", worker_id, job.paper_id, e, exc_info=True
                )
                await _handle_failure(queue, job, str(e))

            finally:
                queue.signal_completion(job.paper_id)
                queue._queue.task_done()

        except asyncio.CancelledError:
            logger.info("Worker %d: Shutting down", worker_id)
            break
        except Exception as e:
            logger.error("Worker %d: Unexpected error: %s", worker_id, e, exc_info=True)


async def _try_claim_job(session, paper_id: int) -> bool:
    """
    Atomically try to claim a conversion job.

    Uses SELECT ... FOR UPDATE SKIP LOCKED to prevent race conditions.

    Returns:
        True if claimed successfully, False if already processing/completed
    """
    # Try to get existing record with lock
    stmt = (
        select(PaperContent)
        .where(PaperContent.paper_id == paper_id)
        .with_for_update(skip_locked=True)
    )
    result = await session.execute(stmt)
    content = result.scalar_one_or_none()

    if content is None:
        # Create new PaperContent record in PROCESSING state
        content = PaperContent(
            paper_id=paper_id,
            status=PaperContentStatus.PROCESSING,
            started_at=datetime.now(timezone.utc),
        )
        session.add(content)
        await session.commit()
        return True

    # Check if already being processed or completed
    if content.status in (PaperContentStatus.PROCESSING, PaperContentStatus.SUCCEEDED):
        return False

    # Status is PENDING or FAILED - claim it
    content.status = PaperContentStatus.PROCESSING
    content.started_at = datetime.now(timezone.utc)
    await session.commit()
    return True


async def _mark_succeeded(session, paper_id: int, markdown: str) -> None:
    """Update PaperContent with successful conversion result."""
    stmt = (
        update(PaperContent)
        .where(PaperContent.paper_id == paper_id)
        .values(
            status=PaperContentStatus.SUCCEEDED,
            markdown=markdown,
            finished_at=datetime.now(timezone.utc),
        )
    )
    await session.execute(stmt)
    await session.commit()


async def _handle_failure(queue: ConversionQueue, job: ConversionJob, error: str) -> None:
    """
    Handle a failed conversion attempt.

    Implements exponential backoff retry logic:
    - If under max retries: increment count and re-queue with delay
    - If max retries exceeded: mark as permanently failed
    """
    new_retry_count = job.retry_count + 1

    async with async_session_local() as session:
        if new_retry_count < settings.DOCLING_MAX_RETRIES:
            # Calculate exponential backoff delay
            delay = settings.DOCLING_RETRY_BASE_DELAY * (2 ** (new_retry_count - 1))

            # Update retry count but keep status as PENDING for retry
            stmt = (
                update(PaperContent)
                .where(PaperContent.paper_id == job.paper_id)
                .values(
                    status=PaperContentStatus.PENDING,
                    retry_count=new_retry_count,
                    finished_at=None,
                )
            )
            await session.execute(stmt)
            await session.commit()

            # Re-queue with delay
            await queue.enqueue(
                paper_id=job.paper_id,
                arxiv_id=job.arxiv_id,
                retry_count=new_retry_count,
                delay_seconds=delay,
            )

            logger.info(
                "Paper %d: Retry %d/%d scheduled in %ds",
                job.paper_id,
                new_retry_count,
                settings.DOCLING_MAX_RETRIES,
                delay,
            )
        else:
            # Max retries exceeded - mark as permanently failed
            stmt = (
                update(PaperContent)
                .where(PaperContent.paper_id == job.paper_id)
                .values(
                    status=PaperContentStatus.FAILED,
                    retry_count=new_retry_count,
                    finished_at=datetime.now(timezone.utc),
                )
            )
            await session.execute(stmt)
            await session.commit()

            logger.error(
                "Paper %d: Max retries (%d) exceeded, marked as FAILED",
                job.paper_id,
                settings.DOCLING_MAX_RETRIES,
            )

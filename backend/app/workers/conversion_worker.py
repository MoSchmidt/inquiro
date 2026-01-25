"""Background worker for processing PDF conversion jobs."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from app.constants.database_constants import PaperContentStatus
from app.core.config import settings
from app.core.database import async_session_local
from app.repositories.paper_content_repository import PaperContentRepository
from app.services.docling_service import DoclingConverter
from app.services.paper_service import PaperService

if TYPE_CHECKING:
    from app.workers.queues.conversion_queue import ConversionJob, ConversionQueue

logger = logging.getLogger("inquiro")


async def conversion_worker(queue: ConversionQueue, worker_id: str) -> None:
    """
    Background worker that processes PDF conversion jobs.

    Each worker:
    1. Gets a job from the queue via dequeue()
    2. Applies any delay (for retry backoff)
    3. Claims the job atomically in the database
    4. Fetches the PDF and converts to markdown
    5. Updates the database with results or handles failures
    """
    converter = DoclingConverter()

    logger.info("Worker %s: Starting", worker_id)

    while queue.running:
        job = None
        try:
            # Get next job (with timeout to check running status periodically)
            job = await queue.dequeue(timeout=1.0)

            if job is None:
                continue

            # Check for shutdown before processing
            if queue.shutdown_requested:
                # Re-queue for another worker or next startup
                await queue.enqueue(job)
                logger.info(
                    "Worker %s: Shutdown requested, re-queued job %s",
                    worker_id,
                    job.job_id,
                )
                break

            await _process_job(queue, job, worker_id, converter)

        except asyncio.CancelledError:
            logger.info("Worker %s: Cancelled", worker_id)
            # Re-queue current job if we have one
            if job is not None:
                try:
                    await queue.enqueue(job)
                    logger.info(
                        "Worker %s: Re-queued job %s after cancellation",
                        worker_id,
                        job.job_id,
                    )
                except Exception:  # pylint: disable=broad-exception-caught
                    pass
            raise
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Worker %s: Unexpected error: %s", worker_id, e, exc_info=True)

    logger.info("Worker %s: Stopped", worker_id)


async def _process_job(
        queue: ConversionQueue,
        job: ConversionJob,
        worker_id: str,
        converter: DoclingConverter,
) -> None:
    """Process a single conversion job."""
    logger.info(
        "Worker %s: Processing job %s (paper %d, retry %d)",
        worker_id,
        job.job_id,
        job.paper_id,
        job.retry_count,
    )

    try:
        # Apply delay for retries (exponential backoff)
        if job.delay_seconds > 0:
            logger.info(
                "Worker %s: Waiting %.1fs before retry",
                worker_id,
                job.delay_seconds,
            )
            await asyncio.sleep(job.delay_seconds)

        async with async_session_local() as session:
            # Try to claim the job atomically
            claimed, content = await PaperContentRepository.try_claim_for_processing(
                session, job.paper_id, worker_id
            )

            if not claimed:
                if content is None:
                    logger.warning(
                        "Worker %s: Paper %d has no content record, skipping",
                        worker_id,
                        job.paper_id,
                    )
                elif content.status == PaperContentStatus.SUCCEEDED:
                    logger.info(
                        "Worker %s: Paper %d already succeeded, skipping",
                        worker_id,
                        job.paper_id,
                    )
                elif content.status == PaperContentStatus.PROCESSING:
                    logger.info(
                        "Worker %s: Paper %d claimed by %s, skipping",
                        worker_id,
                        job.paper_id,
                        content.worker_id,
                    )
                else:
                    logger.info(
                        "Worker %s: Paper %d in status %s, skipping",
                        worker_id,
                        job.paper_id,
                        content.status,
                    )
                return

            # Get PDF URL and convert
            pdf_url = PaperService.arxiv_pdf_url(job.arxiv_id)

            # Convert to markdown (CPU-bound, run in executor)
            loop = asyncio.get_event_loop()
            markdown = await loop.run_in_executor(
                None, converter.convert_pdf_to_markdown, pdf_url
            )

            # Update database with successful result
            success = await PaperContentRepository.mark_succeeded(
                session, job.paper_id, worker_id, markdown
            )

            if success:
                logger.info("Worker %s: Completed paper %d", worker_id, job.paper_id)
            else:
                logger.warning(
                    "Worker %s: Failed to mark paper %d as succeeded (lost ownership?)",
                    worker_id,
                    job.paper_id,
                )

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "Worker %s: Failed paper %d: %s",
            worker_id,
            job.paper_id,
            e,
            exc_info=True,
        )
        await _handle_failure(queue, job, worker_id, str(e))

    finally:
        queue.mark_done()


async def _handle_failure(
        queue: ConversionQueue,
        job: ConversionJob,
        worker_id: str,
        error: str,
) -> None:
    """
    Handle a failed conversion attempt.

    Implements exponential backoff retry logic:
    - If under max retries: increment count and re-queue with delay
    - If max retries exceeded: mark as permanently failed
    """
    # pylint: disable=import-outside-toplevel
    from app.workers.queues.conversion_queue import ConversionJob as CJob

    new_retry_count = job.retry_count + 1
    max_retries = settings.DOCLING_MAX_RETRIES

    async with async_session_local() as session:
        if new_retry_count < max_retries:
            # Mark for retry (sets status back to PENDING)
            await PaperContentRepository.mark_failed(
                session, job.paper_id, worker_id, error, permanent=False
            )

            # Calculate exponential backoff delay
            delay = settings.DOCLING_RETRY_BASE_DELAY * (2 ** (new_retry_count - 1))

            # Re-queue with delay
            retry_job = CJob(
                paper_id=job.paper_id,
                arxiv_id=job.arxiv_id,
                retry_count=new_retry_count,
                delay_seconds=delay,
            )
            await queue.enqueue(retry_job)

            logger.info(
                "Paper %d: Retry %d/%d scheduled in %ds",
                job.paper_id,
                new_retry_count,
                max_retries,
                delay,
            )
        else:
            # Max retries exceeded - mark as permanently failed
            await PaperContentRepository.mark_failed(
                session, job.paper_id, worker_id, error, permanent=True
            )

            logger.error(
                "Paper %d: Max retries (%d) exceeded, marked as FAILED",
                job.paper_id,
                max_retries,
            )

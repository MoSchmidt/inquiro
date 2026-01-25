"""Queue management for PDF to markdown conversion jobs - dispatch only."""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from typing import List, Optional

from app.core.config import settings

logger = logging.getLogger("inquiro")


@dataclass
class ConversionJob:
    """Represents a PDF conversion job in the queue."""

    paper_id: int
    arxiv_id: str
    retry_count: int = 0
    delay_seconds: float = 0.0
    job_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])


class ConversionQueue:
    """
    Manages PDF conversion job dispatch to background workers.

    This is a dispatch-only queue - job state is tracked in the database,
    not in-memory. The queue handles:
    - Job dispatch to workers via asyncio.Queue
    - Worker lifecycle management (start/stop)
    - Graceful shutdown with job re-queuing

    Uses singleton pattern - access via get_instance().
    """

    _instance: Optional[ConversionQueue] = None

    def __init__(self, num_workers: int = 2) -> None:
        self._queue: asyncio.Queue[ConversionJob] = asyncio.Queue()
        self._workers: List[asyncio.Task] = []
        self._num_workers = num_workers
        self._running = False
        self._shutdown_event = asyncio.Event()

    @classmethod
    def get_instance(cls) -> ConversionQueue:
        """Get or create the singleton queue instance."""
        if cls._instance is None:
            cls._instance = cls(num_workers=settings.DOCLING_WORKERS)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (for testing)."""
        cls._instance = None

    async def enqueue(self, job: ConversionJob) -> None:
        """
        Add a job to the dispatch queue.

        This is a fire-and-forget operation - the job is queued for
        processing by background workers.
        """
        await self._queue.put(job)
        logger.info(
            "Enqueued job %s for paper %d (retry=%d, delay=%.1fs)",
            job.job_id,
            job.paper_id,
            job.retry_count,
            job.delay_seconds,
        )

    async def dequeue(self, timeout: float = 1.0) -> Optional[ConversionJob]:
        """
        Get next job from queue with timeout.

        Returns None if timeout expires or shutdown is requested.
        Workers should call this in a loop, checking shutdown_requested.
        """
        try:
            job = await asyncio.wait_for(self._queue.get(), timeout=timeout)
            return job
        except asyncio.TimeoutError:
            return None

    def mark_done(self) -> None:
        """Signal that a dequeued job has been processed."""
        self._queue.task_done()

    async def start_workers(self) -> None:
        """Start the background worker tasks."""
        if self._running:
            return

        # Import here to avoid circular imports
        # pylint: disable=import-outside-toplevel
        from app.workers.conversion_worker import conversion_worker

        self._running = True
        self._shutdown_event.clear()

        for i in range(self._num_workers):
            worker_id = f"worker-{i}"
            task = asyncio.create_task(
                conversion_worker(self, worker_id), name=f"conversion-{worker_id}"
            )
            self._workers.append(task)

        logger.info("Started %d Docling conversion workers", self._num_workers)

    async def stop_workers(self, graceful_timeout: float = 30.0) -> None:
        """
        Stop all background worker tasks.

        Signals shutdown and waits up to graceful_timeout for workers to finish.
        Workers that don't finish in time are force-cancelled.
        """
        if not self._running:
            return

        self._running = False
        self._shutdown_event.set()

        # Wait for graceful completion
        if self._workers:
            _, pending = await asyncio.wait(
                self._workers,
                timeout=graceful_timeout,
                return_when=asyncio.ALL_COMPLETED,
            )

            # Force cancel any remaining
            for task in pending:
                task.cancel()

            if pending:
                await asyncio.gather(*pending, return_exceptions=True)
                logger.warning("Force-cancelled %d workers after timeout", len(pending))

        self._workers.clear()
        logger.info("Stopped Docling conversion workers")

    @property
    def running(self) -> bool:
        """Check if workers are running."""
        return self._running

    @property
    def shutdown_requested(self) -> bool:
        """Check if shutdown has been requested."""
        return self._shutdown_event.is_set()

    @property
    def queue_size(self) -> int:
        """Get the current queue size."""
        return self._queue.qsize()

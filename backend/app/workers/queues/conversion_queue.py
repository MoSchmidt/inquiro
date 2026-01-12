"""Queue management for PDF to markdown conversion jobs."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from app.core.config import settings

logger = logging.getLogger("inquiro")


@dataclass
class ConversionJob:
    """Represents a PDF conversion job in the queue."""

    paper_id: int
    arxiv_id: str
    retry_count: int = 0
    delay_seconds: float = 0.0


class ConversionQueue:
    """
    Manages the queue of PDF conversion jobs and background workers.

    Uses asyncio.Queue for job dispatch and asyncio.Event for completion signaling.
    This is a singleton - use get_instance() to access.
    """

    _instance: Optional[ConversionQueue] = None

    def __init__(self, num_workers: int = 2) -> None:
        self._queue: asyncio.Queue[ConversionJob] = asyncio.Queue()
        self._completion_events: Dict[int, asyncio.Event] = {}
        self._workers: List[asyncio.Task] = []
        self._num_workers = num_workers
        self._running = False

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

    async def enqueue(
        self, paper_id: int, arxiv_id: str, retry_count: int = 0, delay_seconds: float = 0.0
    ) -> None:
        """
        Add a paper to the conversion queue.

        Args:
            paper_id: Database ID of the paper
            arxiv_id: External arXiv ID for fetching the PDF
            retry_count: Current retry attempt number
            delay_seconds: Delay before processing (for exponential backoff)
        """
        job = ConversionJob(
            paper_id=paper_id,
            arxiv_id=arxiv_id,
            retry_count=retry_count,
            delay_seconds=delay_seconds,
        )
        await self._queue.put(job)

        # Initialize completion event if not exists
        if paper_id not in self._completion_events:
            self._completion_events[paper_id] = asyncio.Event()

        logger.info(
            "Enqueued paper %s for conversion (retry=%d, delay=%.1fs)",
            paper_id,
            retry_count,
            delay_seconds,
        )

    async def wait_for_completion(self, paper_id: int, timeout: Optional[float] = None) -> bool:
        """
        Wait for a paper's conversion to complete.

        Args:
            paper_id: The paper ID to wait for
            timeout: Max wait time in seconds (defaults to DOCLING_TIMEOUT_SECONDS)

        Returns:
            True if conversion completed (check DB for success/failure status)
        """
        if timeout is None:
            timeout = float(settings.DOCLING_TIMEOUT_SECONDS)

        event = self._completion_events.get(paper_id)
        if event is None:
            # No pending conversion for this paper
            return True

        try:
            await asyncio.wait_for(event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            logger.warning("Timeout waiting for paper %s conversion", paper_id)
            return False

    def signal_completion(self, paper_id: int) -> None:
        """Signal that conversion is complete for a paper."""
        event = self._completion_events.pop(paper_id, None)
        if event:
            event.set()

    def is_pending(self, paper_id: int) -> bool:
        """Check if a paper has a pending completion event."""
        return paper_id in self._completion_events

    async def start_workers(self) -> None:
        """Start the background worker tasks."""
        if self._running:
            return

        # Import here to avoid circular imports
        from app.workers.conversion_worker import conversion_worker

        self._running = True
        for i in range(self._num_workers):
            task = asyncio.create_task(conversion_worker(self, i))
            self._workers.append(task)

        logger.info("Started %d Docling conversion workers", self._num_workers)

    async def stop_workers(self) -> None:
        """Stop all background worker tasks."""
        if not self._running:
            return

        self._running = False

        # Cancel all worker tasks
        for task in self._workers:
            task.cancel()

        # Wait for cancellation
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)

        self._workers.clear()
        logger.info("Stopped Docling conversion workers")

    @property
    def running(self) -> bool:
        """Check if workers are running."""
        return self._running

    @property
    def queue_size(self) -> int:
        """Get the current queue size."""
        return self._queue.qsize()

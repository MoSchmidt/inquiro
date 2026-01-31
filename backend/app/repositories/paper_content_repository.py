from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple

from sqlalchemy import select, update, and_, or_
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.database_constants import PaperContentStatus
from app.core.config import settings
from app.models.paper_content import PaperContent


class PaperContentRepository:
    """Repository for paper content database operations."""

    # Timeout for reclaiming stale PROCESSING jobs (worker died)
    STALE_CLAIM_TIMEOUT_SECONDS = 600  # 10 minutes

    @staticmethod
    async def get_by_paper_id(session: AsyncSession, paper_id: int) -> Optional[PaperContent]:
        """Returns paper content for the specified paper, or None if not found."""
        stmt = (
            select(PaperContent)
            .where(PaperContent.paper_id == paper_id)
            .execution_options(populate_existing=True)
        )
        result = await session.scalars(stmt)
        return result.first()

    @staticmethod
    async def get_or_create_pending_atomic(
            session: AsyncSession, paper_id: int
    ) -> Tuple[Optional[PaperContent], bool]:
        """
        Atomically get or create a PENDING paper content record.

        Uses INSERT ... ON CONFLICT DO NOTHING for true atomicity - no race conditions.
        Returns (content, was_created).
        """
        insert_stmt = (
            pg_insert(PaperContent)
            .values(paper_id=paper_id, status=PaperContentStatus.PENDING)
            .on_conflict_do_nothing(index_elements=["paper_id"])
        )

        result = await session.execute(insert_stmt)
        await session.commit()

        # Fetch the record (either ours or existing)
        content = await PaperContentRepository.get_by_paper_id(session, paper_id)

        # Determine if we created it (inserted row count > 0)
        was_created = result.rowcount > 0

        return content, was_created

    @staticmethod
    async def try_claim_for_processing(
            session: AsyncSession, paper_id: int, worker_id: str
    ) -> Tuple[bool, Optional[PaperContent]]:
        """
        Atomically try to claim a job for processing.

        Uses optimistic locking via status check in UPDATE WHERE clause.
        Only claims if status is PENDING, FAILED (and retryable), or stale PROCESSING.

        Returns (claimed, content) where:
        - claimed=True, content=record: Successfully claimed
        - claimed=False, content=record: Already processing/succeeded
        - claimed=False, content=None: Record doesn't exist
        """
        now = datetime.now(timezone.utc)
        stale_threshold = now - timedelta(
            seconds=PaperContentRepository.STALE_CLAIM_TIMEOUT_SECONDS
        )

        # Atomic update - only succeeds if conditions are met
        update_stmt = (
            update(PaperContent)
            .where(
                and_(
                    PaperContent.paper_id == paper_id,
                    or_(
                        # Claim PENDING jobs
                        PaperContent.status == PaperContentStatus.PENDING,
                        # Claim FAILED jobs only if still retryable
                        and_(
                            PaperContent.status == PaperContentStatus.FAILED,
                            PaperContent.retry_count < settings.DOCLING_MAX_RETRIES,
                        ),
                        # Reclaim stale PROCESSING jobs (worker died)
                        and_(
                            PaperContent.status == PaperContentStatus.PROCESSING,
                            PaperContent.claimed_at < stale_threshold,
                        ),
                    ),
                )
            )
            .values(
                status=PaperContentStatus.PROCESSING,
                worker_id=worker_id,
                claimed_at=now,
                started_at=now,
            )
            .returning(PaperContent.paper_content_id)
        )

        result = await session.execute(update_stmt)
        await session.commit()

        updated_id = result.scalar_one_or_none()

        if updated_id is not None:
            # Successfully claimed - fetch full record
            content = await PaperContentRepository.get_by_paper_id(session, paper_id)
            return True, content

        # Didn't claim - check why
        content = await PaperContentRepository.get_by_paper_id(session, paper_id)
        return False, content

    @staticmethod
    async def mark_succeeded(
            session: AsyncSession, paper_id: int, worker_id: str, markdown: str
    ) -> bool:
        """
        Mark job as succeeded. Only updates if this worker owns the job.

        Returns True if update succeeded.
        """
        stmt = (
            update(PaperContent)
            .where(
                and_(
                    PaperContent.paper_id == paper_id,
                    PaperContent.worker_id == worker_id,
                    PaperContent.status == PaperContentStatus.PROCESSING,
                )
            )
            .values(
                status=PaperContentStatus.SUCCEEDED,
                markdown=markdown,
                finished_at=datetime.now(timezone.utc),
                error_message=None,
            )
            .returning(PaperContent.paper_content_id)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def mark_failed(
            session: AsyncSession,
            paper_id: int,
            worker_id: str,
            error_message: str,
            permanent: bool = False,
    ) -> bool:
        """
        Mark job as failed. Only updates if this worker owns the job.

        If permanent=False, sets status to PENDING for retry.
        If permanent=True, sets status to FAILED.
        """
        new_status = PaperContentStatus.FAILED if permanent else PaperContentStatus.PENDING

        stmt = (
            update(PaperContent)
            .where(
                and_(
                    PaperContent.paper_id == paper_id,
                    PaperContent.worker_id == worker_id,
                    PaperContent.status == PaperContentStatus.PROCESSING,
                )
            )
            .values(
                status=new_status,
                finished_at=datetime.now(timezone.utc) if permanent else None,
                error_message=error_message,
                retry_count=PaperContent.retry_count + 1,
                worker_id=None,  # Release ownership
                claimed_at=None,
            )
            .returning(PaperContent.paper_content_id)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def is_conversion_complete(
            session: AsyncSession, paper_id: int
    ) -> Tuple[bool, Optional[PaperContentStatus]]:
        """
        Check if paper content conversion is complete (terminal state).

        Returns (is_complete, status) where is_complete is True if:
        - Status is SUCCEEDED, or
        - Status is FAILED and retries exhausted
        """
        content = await PaperContentRepository.get_by_paper_id(session, paper_id)
        if content is None:
            return False, None

        if content.status == PaperContentStatus.SUCCEEDED:
            return True, content.status

        if content.status == PaperContentStatus.FAILED:
            if content.retry_count >= settings.DOCLING_MAX_RETRIES:
                return True, content.status

        return False, content.status

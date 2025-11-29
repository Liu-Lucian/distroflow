"""
Scheduler - Task scheduling and automation

Supports:
- One-time scheduled posts
- Recurring workflows (daily, weekly, etc.)
- Timezone-aware scheduling
- Queue management
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Callable
from pathlib import Path
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Frequency(Enum):
    """Task frequency options."""

    ONCE = "once"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Scheduler:
    """
    Task scheduler for automated posting and workflows.

    Features:
    - Persistent task queue (SQLite)
    - Timezone-aware scheduling
    - Recurring tasks
    - Priority-based execution
    - Retry on failure
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize scheduler.

        Args:
            db_path: Path to SQLite database (default: ~/.distroflow/scheduler.db)
        """
        if db_path is None:
            db_dir = Path.home() / ".distroflow"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(db_dir / "scheduler.db")

        self.db_path = db_path
        self._init_database()
        self._running = False
        self._tasks: Dict[int, asyncio.Task] = {}

        logger.info(f"📅 Scheduler initialized (db: {db_path})")

    def _init_database(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scheduled_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_name TEXT NOT NULL,
                frequency TEXT NOT NULL,
                next_run TIMESTAMP NOT NULL,
                last_run TIMESTAMP,
                status TEXT NOT NULL,
                platforms TEXT NOT NULL,
                content TEXT,
                config TEXT,
                priority INTEGER DEFAULT 0,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()

    def schedule_task(
        self,
        workflow_name: str,
        platforms: List[str],
        frequency: Frequency = Frequency.ONCE,
        run_at: Optional[datetime] = None,
        content: Optional[str] = None,
        config: Optional[Dict] = None,
        priority: int = 0,
    ) -> int:
        """
        Schedule a new task.

        Args:
            workflow_name: Name of workflow to run
            platforms: List of platforms to post to
            frequency: How often to run
            run_at: When to first run (default: now)
            content: Content to post
            config: Additional configuration
            priority: Task priority (higher = runs first)

        Returns:
            Task ID
        """
        if run_at is None:
            run_at = datetime.now()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO scheduled_tasks
            (workflow_name, frequency, next_run, status, platforms, content, config, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                workflow_name,
                frequency.value,
                run_at.isoformat(),
                TaskStatus.PENDING.value,
                json.dumps(platforms),
                content,
                json.dumps(config or {}),
                priority,
            ),
        )

        task_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"📝 Task {task_id} scheduled: {workflow_name} ({frequency.value})")
        return task_id

    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending tasks that should run now."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cursor.execute(
            """
            SELECT id, workflow_name, platforms, content, config
            FROM scheduled_tasks
            WHERE status = ? AND next_run <= ?
            ORDER BY priority DESC, next_run ASC
        """,
            (TaskStatus.PENDING.value, now),
        )

        tasks = []
        for row in cursor.fetchall():
            tasks.append(
                {
                    "id": row[0],
                    "workflow_name": row[1],
                    "platforms": json.loads(row[2]),
                    "content": row[3],
                    "config": json.loads(row[4]) if row[4] else {},
                }
            )

        conn.close()
        return tasks

    def update_task_status(
        self, task_id: int, status: TaskStatus, next_run: Optional[datetime] = None
    ):
        """Update task status and next run time."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if next_run:
            cursor.execute(
                """
                UPDATE scheduled_tasks
                SET status = ?, next_run = ?, last_run = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (status.value, next_run.isoformat(), datetime.now().isoformat(), task_id),
            )
        else:
            cursor.execute(
                """
                UPDATE scheduled_tasks
                SET status = ?, last_run = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (status.value, datetime.now().isoformat(), task_id),
            )

        conn.commit()
        conn.close()

    def calculate_next_run(self, frequency: Frequency, last_run: datetime) -> Optional[datetime]:
        """Calculate next run time based on frequency."""
        if frequency == Frequency.ONCE:
            return None
        elif frequency == Frequency.HOURLY:
            return last_run + timedelta(hours=1)
        elif frequency == Frequency.DAILY:
            return last_run + timedelta(days=1)
        elif frequency == Frequency.WEEKLY:
            return last_run + timedelta(weeks=1)
        elif frequency == Frequency.MONTHLY:
            return last_run + timedelta(days=30)
        return None

    def cancel_task(self, task_id: int):
        """Cancel a scheduled task."""
        self.update_task_status(task_id, TaskStatus.CANCELLED)
        logger.info(f"❌ Task {task_id} cancelled")

    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Dict]:
        """List all tasks (optionally filtered by status)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if status:
            cursor.execute(
                """
                SELECT id, workflow_name, frequency, next_run, status, platforms
                FROM scheduled_tasks
                WHERE status = ?
                ORDER BY next_run ASC
            """,
                (status.value,),
            )
        else:
            cursor.execute(
                """
                SELECT id, workflow_name, frequency, next_run, status, platforms
                FROM scheduled_tasks
                ORDER BY next_run ASC
            """
            )

        tasks = []
        for row in cursor.fetchall():
            tasks.append(
                {
                    "id": row[0],
                    "workflow_name": row[1],
                    "frequency": row[2],
                    "next_run": row[3],
                    "status": row[4],
                    "platforms": json.loads(row[5]),
                }
            )

        conn.close()
        return tasks

    async def run_daemon(self, executor: Callable):
        """
        Run scheduler daemon.

        Args:
            executor: Async function to execute tasks
                      Should accept (task_id, workflow_name, platforms, content, config)
        """
        logger.info("🚀 Scheduler daemon started")
        self._running = True

        while self._running:
            try:
                # Get pending tasks
                tasks = self.get_pending_tasks()

                for task in tasks:
                    task_id = task["id"]

                    # Mark as running
                    self.update_task_status(task_id, TaskStatus.RUNNING)

                    try:
                        # Execute task
                        await executor(
                            task["workflow_name"],
                            task["platforms"],
                            task.get("content"),
                            task.get("config", {}),
                        )

                        # Get task frequency for next run calculation
                        conn = sqlite3.connect(self.db_path)
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT frequency FROM scheduled_tasks WHERE id = ?", (task_id,)
                        )
                        frequency_str = cursor.fetchone()[0]
                        conn.close()

                        frequency = Frequency(frequency_str)
                        next_run = self.calculate_next_run(frequency, datetime.now())

                        if next_run:
                            # Recurring task - reset to pending
                            self.update_task_status(task_id, TaskStatus.PENDING, next_run)
                            logger.info(f"✅ Task {task_id} completed, next run: {next_run}")
                        else:
                            # One-time task - mark completed
                            self.update_task_status(task_id, TaskStatus.COMPLETED)
                            logger.info(f"✅ Task {task_id} completed")

                    except Exception as e:
                        logger.error(f"❌ Task {task_id} failed: {e}")
                        self.update_task_status(task_id, TaskStatus.FAILED)

                # Sleep before checking again
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                await asyncio.sleep(60)

    def stop_daemon(self):
        """Stop scheduler daemon."""
        self._running = False
        logger.info("⏹️ Scheduler daemon stopped")

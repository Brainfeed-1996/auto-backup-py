import hashlib
import time
import threading
import logging
from typing import Optional, Callable
from datetime import datetime
from backup.manager import BackupManager

logger = logging.getLogger(__name__)

class IntegrityVerifier:
    """Verify backup integrity using SHA-256 checksums."""
    
    @staticmethod
    def get_hash(file_path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return ""

    @staticmethod
    def verify_integrity(backup_file: str, expected_hash: str) -> bool:
        """Verify backup matches expected hash."""
        actual_hash = IntegrityVerifier.get_hash(backup_file)
        return actual_hash == expected_hash


class BackupScheduler:
    """Schedule and manage automatic backups."""
    
    def __init__(self, manager: BackupManager, interval_hours: float = 24,
                 on_backup_complete: Optional[Callable] = None,
                 on_error: Optional[Callable] = None):
        self.manager = manager
        self.interval_seconds = interval_hours * 3600
        self.on_backup_complete = on_backup_complete
        self.on_error = on_error
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_backup_time: Optional[datetime] = None

    def start(self):
        """Start the scheduler in a background thread."""
        if self._thread and self._thread.is_alive():
            logger.warning("Scheduler already running")
            return
        
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info(f"Backup scheduler started (interval: {self.interval_seconds}s)")

    def stop(self):
        """Stop the scheduler."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Backup scheduler stopped")

    def run_now(self):
        """Trigger backup immediately."""
        self._perform_backup()

    def _run_loop(self):
        """Main scheduler loop."""
        while not self._stop_event.is_set():
            try:
                self._perform_backup()
            except Exception as e:
                logger.error(f"Backup failed: {e}")
                if self.on_error:
                    self.on_error(e)
            
            # Wait for next interval or until stopped
            self._stop_event.wait(timeout=self.interval_seconds)

    def _perform_backup(self):
        """Execute backup and notify callbacks."""
        logger.info("Scheduled backup starting...")
        
        try:
            result = self.manager.create_snapshot()
            self._last_backup_time = datetime.now()
            
            # Verify integrity
            backup_file = f"{self.manager.backup_dir}/snapshot_{result['timestamp']}.tar.xz.enc"
            if self.manager.verify_backup(backup_file):
                logger.info(f"Integrity verified: {result['final_hash']}")
            
            if self.on_backup_complete:
                self.on_backup_complete(result)
                
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise

    def get_status(self) -> dict:
        """Get scheduler status."""
        return {
            "running": self._thread.is_alive() if self._thread else False,
            "last_backup": self._last_backup_time.isoformat() if self._last_backup_time else None,
            "interval_hours": self.interval_seconds / 3600,
            "pending": not self._stop_event.is_set()
        }


def schedule_backup(manager: BackupManager, interval_hours: float = 24,
                   on_complete=None, on_error=None) -> BackupScheduler:
    """
    Convenience function to start a backup scheduler.
    
    Args:
        manager: BackupManager instance
        interval_hours: Hours between backups
        on_complete: Callback on successful backup
        on_error: Callback on backup error
    
    Returns:
        BackupScheduler instance (call .start() if not auto-started)
    """
    scheduler = BackupScheduler(
        manager=manager,
        interval_hours=interval_hours,
        on_backup_complete=on_complete,
        on_error=on_error
    )
    scheduler.start()
    return scheduler

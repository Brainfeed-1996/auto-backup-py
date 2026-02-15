"""Auto-Backup Professional Package.

A robust, encrypted backup solution with automated lifecycle management.

Modules:
    manager: Core backup management and operations
    scheduler: Scheduled backups and integrity verification
"""

from .manager import BackupManager
from .scheduler import BackupScheduler, IntegrityVerifier, schedule_backup

__all__ = [
    'BackupManager',
    'BackupScheduler', 
    'IntegrityVerifier',
    'schedule_backup'
]

__version__ = '2.0.0'

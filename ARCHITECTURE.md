# Architecture - Auto-Backup Professional

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Auto-Backup Professional                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────────┐  │
│  │   Source    │───▶│  BackupMgr   │───▶│   Encrypted        │  │
│  │   Directory │    │              │    │   Storage (.enc)   │  │
│  └─────────────┘    └──────────────┘    └────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│                    ┌──────────────┐                             │
│                    │   Scheduler   │                             │
│                    │  (Threaded)   │                             │
│                    └──────────────┘                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### BackupManager (`backup/manager.py`)

**Responsibilities:**
- Create compressed archives (tar.xz)
- Encrypt archives using Fernet/AES-128
- Manage backup rotation policies

**Key Methods:**
```python
class BackupManager:
    def __init__(source_dir, backup_dir, secret_key=None)
    def create_snapshot() -> str
    def _encrypt_file(path)
    def _rotate_backups(keep)
```

### Scheduler (`backup/scheduler.py`)

**Responsibilities:**
- Run backups on configurable intervals
- Verify backup integrity
- Daemonize backup process

### Data Flow

1. **Source Phase**: Read from source directory
2. **Compression Phase**: Create LZMA-compressed tar archive
3. **Encryption Phase**: Apply AES-128 encryption
4. **Storage Phase**: Write `.enc` file
5. **Rotation Phase**: Remove old backups exceeding retention
6. **Verification Phase**: Calculate SHA-256 hash

## Security Architecture

```
Source Data ──▶ LZMA Compression ──▶ AES-128 Encryption ──▶ Storage
                  (90% reduction)    (Fernet wrapper)
```

## File Structure

```
auto-backup-py/
├── backup.py              # Entry point
├── backup/
│   ├── __init__.py
│   ├── manager.py         # Core backup logic
│   └── scheduler.py       # Scheduling & verification
├── README.md
├── ARCHITECTURE.md
├── FEATURES.md
└── USAGE.md
```

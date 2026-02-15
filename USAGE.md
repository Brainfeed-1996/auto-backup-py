# Usage Guide - Auto-Backup Professional

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup
```bash
git clone https://github.com/Brainfeed-1996/auto-backup-py.git
cd auto-backup-py
pip install cryptography
```

## Basic Usage

### Create Single Backup

```python
from backup.manager import BackupManager

# Initialize with source and backup directories
manager = BackupManager(
    source_dir="./data",
    backup_dir="./backups"
)

# Create encrypted, compressed snapshot
manager.create_snapshot()
```

### With Custom Encryption Key

```python
from cryptography.fernet import Fernet

# Generate or load your key
key = b'your-32-byte-key-here'
manager = BackupManager(
    source_dir="./data",
    backup_dir="./backups",
    secret_key=key
)
```

## Scheduled Backups

### Run Every 24 Hours

```python
from backup.scheduler import schedule_backup

schedule_backup(manager, interval_hours=24)
```

### Custom Retention Policy

```python
# Keep only last 3 backups
manager._rotate_backups(keep=3)
```

## Verify Backups

```python
from backup.scheduler import IntegrityVerifier

# Calculate hash
hash_value = IntegrityVerifier.get_hash("backup.snapshot_xxx.tar.xz.enc")
print(f"SHA256: {hash_value}")
```

## Command Line Interface

```bash
# Run backup
python backup.py

# Help
python backup.py --help
```

## Configuration File

Create `config.yaml`:

```yaml
source_dir: ./data
backup_dir: ./backups
interval_hours: 24
retention_count: 5
encryption:
  enabled: true
  algorithm: AES-128
compression:
  algorithm: LZMA
  level: 6
```

## Troubleshooting

### "Permission Denied"
- Check write permissions on backup directory
- Ensure source directory exists

### "Encryption Failed"
- Verify Fernet key format (32 bytes, base64-encoded)
- Check disk space

### "Compression Error"
- Reduce compression level for large files
- Check available memory

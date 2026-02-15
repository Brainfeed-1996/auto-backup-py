# Auto-Backup Professional

A robust, encrypted backup solution with automated lifecycle management.

## 🔒 Overview

Auto-Backup Professional provides enterprise-grade backup capabilities with AES-128 encryption, LZMA compression, and intelligent rotation policies.

## 🚀 Quick Start

```bash
pip install cryptography
python backup.py
```

## 📦 Installation

```bash
git clone https://github.com/Brainfeed-1996/auto-backup-py.git
cd auto-backup-py
pip install -r requirements.txt
```

## 🔧 Configuration

Create a `config.json` file:

```json
{
    "source_dir": "./data",
    "backup_dir": "./backups",
    "interval_hours": 24,
    "retention_count": 5,
    "encryption_enabled": true,
    "compression_level": 6
}
```

## 📖 Usage

### Basic Backup

```python
from backup.manager import BackupManager

manager = BackupManager("./data", "./backups")
manager.create_snapshot()
```

### Scheduled Backup

```python
from backup.scheduler import schedule_backup

schedule_backup(manager, interval_hours=12)
```

### Verify Integrity

```python
from backup.scheduler import IntegrityVerifier

hash_value = IntegrityVerifier.get_hash("backup.snapshot_xxx.tar.xz.enc")
print(f"SHA256: {hash_value}")
```

## 🔐 Security

- **Encryption**: AES-128 via Fernet (symmetric)
- **Compression**: LZMA/XZ for maximum ratio
- **Integrity**: SHA-256 checksums

## 📝 License

MIT License

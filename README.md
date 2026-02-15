# Auto-Backup Professional v2.0

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A robust, encrypted backup solution with automated lifecycle management.

## 🔒 Overview

Auto-Backup Professional provides enterprise-grade backup capabilities with:

- **AES-128 Encryption** via Fernet (symmetric encryption)
- **LZMA Compression** for maximum compression ratio
- **SHA-256 Integrity Verification** 
- **Automatic Retention Policies**
- **Versioned Snapshots**

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
    "compression_enabled": true,
    "compression_level": 6,
    "verify_integrity": true
}
```

## 📖 Usage

### Basic Backup

```python
from backup.manager import BackupManager

manager = BackupManager("./data", "./backups")
manifest = manager.create_snapshot()
print(f"Created: {manifest['name']}")
```

### Scheduled Backup

```python
import schedule
import time

def backup_job():
    manager.create_snapshot()

schedule.every(24).hours.do(backup_job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Restore Backup

```python
manager = BackupManager("./data", "./backups")
restored_path = manager.restore_snapshot("backup_20240215_120000")
print(f"Restored to: {restored_path}")
```

### Verify Integrity

```python
manager = BackupManager("./data", "./backups")
if manager.verify_integrity("backup_20240215_120000"):
    print("✓ Integrity verified")
```

### Cleanup Old Snapshots

```python
manager = BackupManager("./data", "./backups")
manager.cleanup_old_snapshots()
```

## 📊 Features

| Feature | Description |
|---------|-------------|
| Encryption | AES-128-CBC via Fernet |
| Compression | LZMA/XZ algorithm |
| Integrity | SHA-256 checksums |
| Retention | Configurable count-based |
| Versioning | Timestamped snapshots |

## 🔐 Security

- **Encryption**: Fernet uses AES-128-CBC with PKCS7 padding and HMAC-SHA256 for authentication
- **Key Management**: Keys stored in `.encryption_key` file in backup directory
- **Integrity**: Every snapshot includes SHA-256 hash for verification

## 📁 Project Structure

```
auto-backup-py/
├── backup.py           # Main backup manager
├── config.json         # Configuration file
├── requirements.txt    # Dependencies
├── data/              # Source data directory
├── backups/           # Backup storage directory
└── README.md
```

## 🛠️ Dependencies

```
cryptography>=3.0
```

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

## 👤 Author

**Olivier Robert-Duboille**  
GitHub: https://github.com/Brainfeed-1996

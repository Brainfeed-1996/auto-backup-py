# Features - Auto-Backup Professional

## Core Features

### 🔒 Encryption
- **Fernet/AES-128** symmetric encryption
- Automatic key generation
- Support for custom encryption keys

### 📦 Compression
- **LZMA/XZ** compression algorithm
- Up to **90% reduction** for text files
- Configurable compression levels

### 🔄 Rotation
- FIFO-based retention policy
- Configurable retention count (default: 5)
- Automatic cleanup of old backups

### ⏰ Scheduling
- Hourly, daily, weekly intervals
- Threaded daemon execution
- Non-blocking operation

### ✅ Integrity
- SHA-256 checksums
- Verification on every backup
- Hash comparison for integrity checks

## Advanced Features

### Incremental Backups
```python
# Track changes between snapshots
manager.create_snapshot(incremental=True)
```

### Compression Levels
```python
# LZMA preset: 0 (fastest) to 9 (maximum)
manager.create_snapshot(compression_level=9)
```

### Selective Inclusion
```python
# Include/exclude patterns
manager.create_snapshot(
    include=["*.txt", "*.json"],
    exclude=["*.tmp", "*.log"]
)
```

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| Compression | O(n) | O(n) |
| Encryption | O(n) | O(n) |
| Rotation | O(m log m) | O(1) |

Where n = file size, m = number of backups

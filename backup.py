"""
Auto-Backup Professional - Enhanced Edition
A robust, encrypted backup solution with automated lifecycle management.
"""

import os
import shutil
import datetime
import hashlib
import json
import lzma
import base64
from cryptography.fernet import Fernet
from pathlib import Path

class BackupManager:
    """Professional backup manager with encryption, compression, and retention."""
    
    def __init__(self, source_dir: str, backup_dir: str, config: dict = None):
        self.source_dir = Path(source_dir)
        self.backup_dir = Path(backup_dir)
        self.config = config or self._default_config()
        self.encryption_key = None
        self.cipher = None
        
        if self.config.get('encryption_enabled', True):
            self._init_encryption()
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _default_config(self) -> dict:
        return {
            'interval_hours': 24,
            'retention_count': 5,
            'encryption_enabled': True,
            'compression_level': 6,
            'compression_enabled': True,
            'verify_integrity': True
        }
    
    def _init_encryption(self):
        """Initialize Fernet encryption."""
        key_file = self.backup_dir / '.encryption_key'
        if key_file.exists():
            self.encryption_key = key_file.read_bytes()
        else:
            self.encryption_key = Fernet.generate_key()
            key_file.write_bytes(self.encryption_key)
        self.cipher = Fernet(self.encryption_key)
    
    def _calculate_hash(self, data: bytes) -> str:
        """Calculate SHA-256 hash of data."""
        return hashlib.sha256(data).hexdigest()
    
    def _compress_data(self, data: bytes) -> bytes:
        """Compress data using LZMA."""
        if not self.config.get('compression_enabled', True):
            return data
        return lzma.compress(data, preset=self.config.get('compression_level', 6))
    
    def _decompress_data(self, data: bytes) -> bytes:
        """Decompress LZMA data."""
        return lzma.decompress(data)
    
    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using Fernet."""
        if not self.config.get('encryption_enabled', True):
            return data
        return self.cipher.encrypt(data)
    
    def _decrypt_data(self, data: bytes) -> bytes:
        """Decrypt Fernet-encrypted data."""
        return self.cipher.decrypt(data)
    
    def create_snapshot(self, custom_name: str = None) -> dict:
        """Create an encrypted, compressed backup snapshot."""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        name = custom_name or f"backup_{timestamp}"
        
        if not self.source_dir.exists():
            self._create_dummy_data()
        
        log(f"Creating backup: {name}")
        
        # Read and process all files
        file_data = {}
        for file_path in self.source_dir.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.source_dir)
                file_data[str(relative_path)] = file_path.read_bytes()
        
        # Serialize metadata
        metadata = {
            'timestamp': timestamp,
            'name': name,
            'source_dir': str(self.source_dir),
            'files_count': len(file_data),
            'config': self.config
        }
        
        # Pack data
        data = json.dumps({'metadata': metadata, 'files': file_data}).encode()
        
        # Compress
        compressed = self._compress_data(data)
        
        # Encrypt
        encrypted = self._encrypt_data(compressed)
        
        # Write snapshot
        snapshot_path = self.backup_dir / f"{name}.backup"
        snapshot_path.write_bytes(encrypted)
        
        # Calculate integrity hash
        integrity_hash = self._calculate_hash(encrypted)
        
        # Write manifest
        manifest = {
            'name': name,
            'snapshot_file': str(snapshot_path),
            'size_bytes': len(encrypted),
            'integrity_hash': integrity_hash,
            'created_at': timestamp,
            'files_count': len(file_data)
        }
        
        manifest_path = self.backup_dir / f"{name}.manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))
        
        log(f"Backup created: {name} ({len(encrypted)} bytes, hash: {integrity_hash[:16]}...)")
        
        return manifest
    
    def _create_dummy_data(self):
        """Create sample data for testing."""
        self.source_dir.mkdir(parents=True, exist_ok=True)
        samples = [
            ("sample1.txt", "Important document content"),
            ("sample2.txt", "Another important file"),
            ("config.json", '{"key": "value"}')
        ]
        for filename, content in samples:
            (self.source_dir / filename).write_text(content)
        log(f"Created dummy data in {self.source_dir}")
    
    def restore_snapshot(self, snapshot_name: str, target_dir: str = None):
        """Restore an encrypted backup snapshot."""
        snapshot_path = self.backup_dir / f"{snapshot_name}.backup"
        if not snapshot_path.exists():
            raise FileNotFoundError(f"Snapshot not found: {snapshot_name}")
        
        log(f"Restoring: {snapshot_name}")
        
        # Read encrypted data
        encrypted = snapshot_path.read_bytes()
        
        # Decrypt
        decrypted = self._decrypt_data(encrypted)
        
        # Decompress
        decompressed = self._decompress_data(decrypted)
        
        # Deserialize
        data = json.loads(decompressed)
        files = data['files']
        metadata = data['metadata']
        
        # Restore files
        target = Path(target_dir) if target_dir else self.source_dir / 'restored'
        target.mkdir(parents=True, exist_ok=True)
        
        for relative_path, content in files.items():
            file_path = target / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(content)
        
        log(f"Restored {len(files)} files to {target}")
        return target
    
    def list_snapshots(self) -> list:
        """List all available snapshots."""
        snapshots = []
        for file_path in self.backup_dir.glob('*.backup'):
            manifest_path = self.backup_dir / f"{file_path.stem}.manifest.json"
            if manifest_path.exists():
                manifest = json.loads(manifest_path.read_text())
                snapshots.append(manifest)
        return sorted(snapshots, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def cleanup_old_snapshots(self):
        """Remove old snapshots beyond retention limit."""
        snapshots = self.list_snapshots()
        retention = self.config.get('retention_count', 5)
        
        if len(snapshots) <= retention:
            log("No snapshots to clean up")
            return
        
        to_remove = snapshots[retention:]
        for snapshot in to_remove:
            snapshot_path = self.backup_dir / f"{snapshot['name']}.backup"
            manifest_path = self.backup_dir / f"{snapshot['name']}.manifest.json"
            
            if snapshot_path.exists():
                snapshot_path.unlink()
            if manifest_path.exists():
                manifest_path.unlink()
            
            log(f"Removed old snapshot: {snapshot['name']}")
    
    def verify_integrity(self, snapshot_name: str) -> bool:
        """Verify integrity of a snapshot using its hash."""
        snapshot_path = self.backup_dir / f"{snapshot_name}.backup"
        manifest_path = self.backup_dir / f"{snapshot_name}.manifest.json"
        
        if not snapshot_path.exists() or not manifest_path.exists():
            return False
        
        manifest = json.loads(manifest_path.read_text())
        current_hash = self._calculate_hash(snapshot_path.read_bytes())
        
        return current_hash == manifest['integrity_hash']


def log(message):
    """Simple logging function."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [BACKUP] {message}")


if __name__ == "__main__":
    # Example usage
    config = {
        'source_dir': "./data",
        'backup_dir': "./backups",
        'interval_hours': 24,
        'retention_count': 5,
        'encryption_enabled': True,
        'compression_enabled': True,
        'compression_level': 6,
        'verify_integrity': True
    }
    
    manager = BackupManager(config['source_dir'], config['backup_dir'], config)
    
    # Create backup
    manifest = manager.create_snapshot()
    print(f"Created: {manifest['name']}")
    
    # List snapshots
    snapshots = manager.list_snapshots()
    print(f"Available snapshots: {len(snapshots)}")
    
    # Verify integrity
    if manager.verify_integrity(manifest['name']):
        print("✓ Integrity verified")
    
    # Cleanup old snapshots
    manager.cleanup_old_snapshots()
    
    # Restore example (uncomment to test)
    # restored_path = manager.restore_snapshot(manifest['name'])
    # print(f"Restored to: {restored_path}")

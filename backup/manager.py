import os
import tarfile
import lzma
import shutil
import json
import hashlib
from datetime import datetime
from cryptography.fernet import Fernet
from typing import List, Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BackupManager:
    def __init__(self, source_dir: str, backup_dir: str, secret_key: Optional[bytes] = None, 
                 compression_level: int = 6, retention_count: int = 5):
        self.source_dir = source_dir
        self.backup_dir = backup_dir
        self.compression_level = compression_level
        self.retention_count = retention_count
        self.key = secret_key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.backup_manifest: Dict[str, Dict[str, Any]] = {}
        
        os.makedirs(backup_dir, exist_ok=True)
        self._load_manifest()

    def _load_manifest(self):
        manifest_path = os.path.join(self.backup_dir, "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                self.backup_manifest = json.load(f)

    def _save_manifest(self):
        manifest_path = os.path.join(self.backup_dir, "manifest.json")
        with open(manifest_path, 'w') as f:
            json.dump(self.backup_manifest, f, indent=2)

    def create_snapshot(self, include_patterns: Optional[List[str]] = None, 
                        exclude_patterns: Optional[List[str]] = None,
                        incremental: bool = False) -> Dict[str, Any]:
        """Create an encrypted, compressed backup snapshot."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"snapshot_{timestamp}.tar.xz"
        archive_path = os.path.join(self.backup_dir, archive_name)
        
        logger.info(f"Creating compressed snapshot: {archive_name}")
        
        # Create tar archive with optional filtering
        with tarfile.open(archive_path, f"w:xz", compresslevel=self.compression_level) as tar:
            self._add_to_archive(tar, self.source_dir, include_patterns, exclude_patterns)
        
        # Calculate original hash
        original_hash = self._calculate_hash(archive_path)
        
        # Encrypt the archive
        encrypted_path = self._encrypt_file(archive_path)
        
        # Get final hash and size
        final_hash = self._calculate_hash(encrypted_path)
        file_size = os.path.getsize(encrypted_path)
        
        # Update manifest
        backup_info = {
            "timestamp": timestamp,
            "original_size": os.path.getsize(archive_path),
            "encrypted_size": file_size,
            "original_hash": original_hash,
            "final_hash": final_hash,
            "incremental": incremental,
            "compression_level": self.compression_level
        }
        self.backup_manifest[archive_name] = backup_info
        self._save_manifest()
        
        # Rotation
        self._rotate_backups(self.retention_count)
        
        logger.info(f"Backup complete: {file_size} bytes, SHA256: {final_hash}")
        return backup_info

    def _add_to_archive(self, tar, path, include: Optional[List[str]] = None, 
                       exclude: Optional[List[str]] = None):
        """Add files to tar archive with pattern filtering."""
        for root, dirs, files in os.walk(path):
            # Filter directories
            dirs[:] = [d for d in dirs if not self._should_exclude(d, exclude)]
            
            for file in files:
                if include and not self._should_include(file, include):
                    continue
                if exclude and self._should_exclude(file, exclude):
                    continue
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, os.path.dirname(self.source_dir))
                tar.add(full_path, arcname=arcname)

    def _should_include(self, filename: str, patterns: List[str]) -> bool:
        return any(pattern in filename for pattern in patterns)

    def _should_exclude(self, filename: str, patterns: Optional[List[str]]) -> bool:
        if not patterns:
            return False
        return any(pattern in filename for pattern in patterns)

    def _encrypt_file(self, path: str) -> str:
        """Encrypt file using Fernet/AES-128."""
        logger.info(f"Encrypting archive with AES-128...")
        with open(path, "rb") as f:
            data = f.read()
        encrypted_data = self.cipher.encrypt(data)
        encrypted_path = path + ".enc"
        with open(encrypted_path, "wb") as f:
            f.write(encrypted_data)
        os.remove(path)
        return encrypted_path

    def decrypt_backup(self, backup_file: str, output_dir: str) -> str:
        """Decrypt a backup file."""
        logger.info(f"Decrypting backup: {backup_file}")
        with open(backup_file, "rb") as f:
            encrypted_data = f.read()
        decrypted_data = self.cipher.decrypt(encrypted_data)
        
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "restored.tar.xz")
        with open(output_path, "wb") as f:
            f.write(decrypted_data)
        
        # Extract
        with tarfile.open(output_path, "r:xz") as tar:
            tar.extractall(output_dir)
        
        logger.info(f"Restored to: {output_dir}")
        return output_dir

    def _calculate_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def verify_backup(self, backup_file: str) -> bool:
        """Verify backup integrity against manifest."""
        if not backup_file.endswith(".enc"):
            backup_file += ".enc"
        
        current_hash = self._calculate_hash(backup_file)
        
        # Find in manifest
        for name, info in self.backup_manifest.items():
            if name.replace(".tar.xz", "") in backup_file:
                return current_hash == info.get("final_hash")
        return False

    def _rotate_backups(self, keep: int):
        """Remove old backups exceeding retention count."""
        backups = sorted([f for f in os.listdir(self.backup_dir) if f.endswith(".enc")])
        if len(backups) > keep:
            for old_backup in backups[:-keep]:
                logger.info(f"Rotating old backup: {old_backup}")
                os.remove(os.path.join(self.backup_dir, old_backup))
                # Remove from manifest
                key_to_remove = old_backup.replace(".enc", "")
                if key_to_remove in self.backup_manifest:
                    del self.backup_manifest[key_to_remove]
            self._save_manifest()

    def list_backups(self) -> List[Dict[str, Any]]:
        """List all backups with their metadata."""
        return [{"name": k, **v} for k, v in self.backup_manifest.items()]

    def cleanup(self):
        """Cleanup temporary files and rotate old backups."""
        self._rotate_backups(self.retention_count)
        logger.info("Cleanup completed")

if __name__ == "__main__":
    # Example usage
    # manager = BackupManager("./src", "./backups")
    # manager.create_snapshot()
    pass
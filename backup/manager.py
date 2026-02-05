import os
import tarfile
import lzma
import shutil
from datetime import datetime
from cryptography.fernet import Fernet

class BackupManager:
    def __init__(self, source_dir, backup_dir, secret_key=None):
        self.source_dir = source_dir
        self.backup_dir = backup_dir
        self.key = secret_key or Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def create_snapshot(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"snapshot_{timestamp}.tar.xz"
        archive_path = os.path.join(self.backup_dir, archive_name)
        
        print(f"[*] Creating compressed snapshot: {archive_name}")
        with tarfile.open(archive_path, "w:xz") as tar:
            tar.add(self.source_dir, arcname=os.path.basename(self.source_dir))
        
        self._encrypt_file(archive_path)
        self._rotate_backups(keep=5)
        return archive_path

    def _encrypt_file(self, path):
        print(f"[*] Encrypting archive with AES-128 (Fernet)...")
        with open(path, "rb") as f:
            data = f.read()
        encrypted_data = self.cipher.encrypt(data)
        with open(path + ".enc", "wb") as f:
            f.write(encrypted_data)
        os.remove(path)

    def _rotate_backups(self, keep):
        backups = sorted([f for f in os.listdir(self.backup_dir) if f.endswith(".enc")])
        if len(backups) > keep:
            for old_backup in backups[:-keep]:
                print(f"[-] Rotating old backup: {old_backup}")
                os.remove(os.path.join(self.backup_dir, old_backup))

if __name__ == "__main__":
    # Example usage
    # manager = BackupManager("./src", "./backups")
    # manager.create_snapshot()
    pass
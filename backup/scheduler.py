import hashlib
import time
import threading

class IntegrityVerifier:
    @staticmethod
    def get_hash(file_path):
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

def schedule_backup(manager, interval_hours=24):
    def run():
        while True:
            print("[*] Scheduled backup starting...")
            path = manager.create_snapshot()
            file_hash = IntegrityVerifier.get_hash(path)
            print(f"[+] Backup complete. SHA256: {file_hash}")
            time.sleep(interval_hours * 3600)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
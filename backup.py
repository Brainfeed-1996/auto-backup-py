import os
import shutil
import datetime
import time

SOURCE_DIR = "./data"
BACKUP_DIR = "./backups"

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def perform_backup():
    if not os.path.exists(SOURCE_DIR):
        log(f"Source directory {SOURCE_DIR} does not exist. Creating dummy data.")
        os.makedirs(SOURCE_DIR)
        with open(os.path.join(SOURCE_DIR, "file1.txt"), "w") as f:
            f.write("Important data content")

    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    backup_name = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    target_path = os.path.join(BACKUP_DIR, backup_name)

    log(f"Starting backup from {SOURCE_DIR} to {target_path}...")
    try:
        shutil.copytree(SOURCE_DIR, target_path)
        log("Backup completed successfully.")
    except Exception as e:
        log(f"Backup failed: {str(e)}")

if __name__ == "__main__":
    log("Auto Backup Tool Initialized")
    perform_backup()

# rw.py  -- safe encryptor (learning/demo only)
import os
import shutil
from cryptography.fernet import Fernet, InvalidToken

KEYFILE = "seckey.key"
BACKUP_DIR = "backups"

# Files to skip
SKIP = {
    "rw.py",           # this script
    "decrypt.py",      # your decrypt script (if present)
    "decrypt_dashboard.py",
    "complete_dashboard.py",
    KEYFILE,
    "generate_key.py"
}
try:
    SKIP.add(os.path.basename(__file__))
except Exception:
    pass

# Ensure backup folder exists
os.makedirs(BACKUP_DIR, exist_ok=True)

# If a key exists, reuse it so you can decrypt later.
if os.path.exists(KEYFILE):
    with open(KEYFILE, "rb") as k:
        key = k.read()
    print("Using existing key from", KEYFILE)
else:
    key = Fernet.generate_key()
    with open(KEYFILE, "wb") as k:
        k.write(key)
    print("Generated new key and saved to", KEYFILE)
# Do NOT print the key in real use. This is OK for local testing only.
# print("Key (keep secret!):", key)

fernet = Fernet(key)

# collect target files
files = [f for f in os.listdir() if os.path.isfile(f) and f not in SKIP]

if not files:
    print("No files to encrypt (skipping scripts and key files).")
else:
    for file in files:
        print("\nProcessing:", file)
        try:
            with open(file, "rb") as fh:
                data = fh.read()
        except Exception as e:
            print("  ❌ Could not read file:", e)
            continue

        # If file already appears to be encrypted with the same key, skip it.
        try:
            _ = fernet.decrypt(data)   # if this succeeds, file already encrypted with this key
            print("  ⛔ Skipped: file already encrypted with this key.")
            continue
        except InvalidToken:
            # file is not decrypted by this key -> safe to encrypt
            pass
        except Exception as e:
            print("  ❌ Unexpected error when testing file:", e)
            continue

        # backup original
        backup_path = os.path.join(BACKUP_DIR, file)
        if not os.path.exists(backup_path):
            try:
                shutil.copy2(file, backup_path)
                print("  ✅ Backup saved to", backup_path)
            except Exception as e:
                print("  ❌ Could not backup, skipping to avoid data loss:", e)
                continue
        else:
            print("  ℹ️ Backup already exists:", backup_path)

        # encrypt and overwrite
        try:
            encrypted = fernet.encrypt(data)
            with open(file, "wb") as fh:
                fh.write(encrypted)
            print("  ✅ Encrypted:", file)
        except Exception as e:
            print("  ❌ Failed to write encrypted file:", e)
            # try to restore from backup
            try:
                shutil.copy2(backup_path, file)
                print("  ↩️ Restored original from backup.")
            except Exception as e2:
                print("  ⚠️ Failed to restore backup:", e2)

print("\nDone.")
print("Backups are in the", BACKUP_DIR, "folder. Keep", KEYFILE, "safe to decrypt.")

# decrypt_dashboard.py
import os
import shutil
import time
import streamlit as st
from cryptography.fernet import Fernet, InvalidToken

st.set_page_config(page_title="Decrypt Dashboard", layout="wide")

KEYFILE = "seckey.key"
BACKUP_DIR = "backups"
SKIP_DEFAULT = {"decrypt_dashboard.py", "rw.py", "decrypt.py", "decypt.py", "complete_dashboard.py", KEYFILE, "generate_key.py"}

st.title("🔐 Decrypt Dashboard — Safe File Decryption")

#st.warning("Use this only for learning/testing. Make backups and do not run on critical system files.")

# Sidebar: options
st.sidebar.header("Settings")
custom_skip = st.sidebar.text_area("Additional filenames to skip", value="")
if custom_skip.strip():
    try:
        user_skips = {s.strip() for s in custom_skip.split(",") if s.strip()}
    except Exception:
        user_skips = set()
else:
    user_skips = set()

SKIP = SKIP_DEFAULT.union(user_skips)
try:
    SKIP.add(os.path.basename(__file__))
except Exception:
    pass

# show key status
st.sidebar.subheader("Key status")
if not os.path.exists(KEYFILE):
    st.sidebar.error(f"Keyfile '{KEYFILE}' not found in folder.")
else:
    b = open(KEYFILE,"rb").read()
    st.sidebar.success(f"Keyfile found — length: {len(b)} bytes")
    with st.sidebar.expander("Show key repr (hidden by default)"):
        st.code(repr(b))

# list files
files = [f for f in os.listdir() if os.path.isfile(f) and f not in SKIP]
st.subheader("Files in folder")
if files:
    st.write(f"Found {len(files)} candidate files (skipping scripts & key):")
    # multi-select list
    to_decrypt = st.multiselect("Select files to decrypt", options=files, default=files)
else:
    st.info("No candidate files found in folder.")

# passphrase input
st.subheader("Decryption")
secret_phrase_input = st.text_input("Enter passphrase", type="password")
use_custom_phrase = st.checkbox("Use custom passphrase", value=False)
if use_custom_phrase:
    passphrase = secret_phrase_input
else:
    passphrase = secret_phrase_input  # still takes what user wrote; default expected 'ravi'

# show a button to start
start = st.button("🔓 Decrypt selected files")

# log area
if "log" not in st.session_state:
    st.session_state.log = []
def log(msg):
    st.session_state.log.append(msg)
    # keep only last 500 lines
    if len(st.session_state.log) > 500:
        st.session_state.log = st.session_state.log[-500:]

st.sidebar.markdown("### Logs")
st.sidebar.text_area("log", value="\n".join(st.session_state.log[-50:]), height=300)

# helper: validate key
def load_and_validate_key():
    if not os.path.exists(KEYFILE):
        return None, "Keyfile not found"
    b = open(KEYFILE, "rb").read()
    try:
        fernet = Fernet(b)
        return fernet, None
    except Exception as e:
        return None, f"Invalid Fernet key: {e}"

# actual action
if start:
    # simple passphrase check (case-sensitive)
    if not passphrase:
        st.error("Enter passphrase first.")
    else:
        # expected passphrase — change if you want; by default 'ravi'
        expected = "ravi"
        if passphrase != expected:
            st.error("Wrong passphrase. Decryption aborted.")
            log("User entered wrong passphrase.")
        else:
            # validate key
            fernet, err = load_and_validate_key()
            if err:
                st.error(err)
                log(err)
            else:
                # ensure backup dir
                os.makedirs(BACKUP_DIR, exist_ok=True)
                total = len(to_decrypt)
                progress = st.progress(0)
                status_col, info_col = st.columns([3,1])
                count = 0
                for idx, filename in enumerate(to_decrypt):
                    status_col.write(f"🔁 Processing: **{filename}**")
                    try:
                        with open(filename, "rb") as fh:
                            ciphertext = fh.read()
                    except Exception as e:
                        msg = f"❌ Could not read {filename}: {e}"
                        log(msg); status_col.error(msg); 
                        continue

                    # try decrypt in memory
                    try:
                        plaintext = fernet.decrypt(ciphertext)
                    except InvalidToken:
                        msg = f"❌ INVALID TOKEN for {filename} (file not encrypted with this key)"
                        log(msg); status_col.error(msg); continue
                    except Exception as e:
                        msg = f"❌ Error decrypting {filename}: {e}"
                        log(msg); status_col.error(msg); continue

                    # backup
                    backup_path = os.path.join(BACKUP_DIR, filename)
                    try:
                        if not os.path.exists(backup_path):
                            shutil.copy2(filename, backup_path)
                            log(f"Backup created: {backup_path}")
                            status_col.info("Backup created")
                        else:
                            status_col.info("Backup already exists")
                    except Exception as e:
                        msg = f"⚠️ Could not backup {filename}: {e}"
                        log(msg); status_col.error(msg); continue

                    # write decrypted
                    try:
                        with open(filename, "wb") as fh:
                            fh.write(plaintext)
                        msg = f"✅ Decrypted: {filename}"
                        log(msg); status_col.success(msg)
                    except Exception as e:
                        # try restore
                        try:
                            shutil.copy2(backup_path, filename)
                            restore_msg = f"Restored original for {filename} from backup due to write error."
                            log(restore_msg); status_col.warning(restore_msg)
                        except Exception as e2:
                            log(f"Failed to write and restore for {filename}: {e2}")
                            status_col.error(f"Critical failure for {filename}: {e2}")
                        continue

                    count += 1
                    progress.progress(int((idx+1)/max(1,total)*100))
                    time.sleep(0.1)

                st.success(f"Done. {count}/{total} files decrypted successfully.")
                st.balloons()
                # refresh log display
                st.sidebar.text_area("log", value="\n".join(st.session_state.log[-200:]), height=300)

import paramiko
import sqlite3
import io

# VM Details
VM_IP = "93.127.215.185"
VM_USERNAME = "root"
VM_PASSWORD = "Koirala@123"
REMOTE_DB_PATH = "/root/project-onboarding-forms-main2/real_estate_onboarding.db"

def get_remote_db():
    try:
        # Establish SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(VM_IP, username=VM_USERNAME, password=VM_PASSWORD)

        # Open an SFTP session
        sftp = ssh.open_sftp()
        with sftp.file(REMOTE_DB_PATH, 'rb') as remote_db_file:
            db_bytes = remote_db_file.read()
        
        # Close SFTP and SSH
        sftp.close()
        ssh.close()
        
        # Load the DB into a memory-based SQLite database
        memory_db = sqlite3.connect(":memory:")
        memory_db.executescript(io.StringIO(db_bytes.decode()).getvalue())
        
        return memory_db
    except Exception as e:
        print(f"Error: {e}")
        return None

# Usage Example
conn = get_remote_db()
if conn:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in the database:", tables)
    conn.close()

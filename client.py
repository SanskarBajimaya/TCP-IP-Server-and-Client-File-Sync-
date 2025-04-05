import socket
import os
import sys
import time

HOST = '127.0.0.1'
PORT = 65432
SYNC_DIR = 'client_files'


def get_file_timestamp(filepath):
    """Get last modified time of a file."""
    return os.path.getmtime(filepath) if os.path.exists(filepath) else 0


def upload_file(filename):
    """Upload file to server if local version is newer."""
    filepath = os.path.join(SYNC_DIR, filename)
    if not os.path.exists(filepath):
        print(f"File not found: {filename}")
        return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return

        # Send local timestamp for conflict check
        s.sendall(f"UPLOAD|{filename}|{get_file_timestamp(filepath)}".encode())

        # Read server response (OK/CONFLICT)
        print(f"Preparing to upload: {filename}")
        print(f"Local timestamp: {time.ctime(get_file_timestamp(filepath))}")

        # Existing logic remains the same...
        response = s.recv(1024).decode()

        if response == "OK":
            with open(filepath, 'rb') as f:
                s.sendfile(f)
            print(f"File uploaded successfully: {filename}")
        elif response.startswith("CONFLICT"):
            print(f"Conflict detected: {response}")
        else:
            print(f"Unexpected response: {response}")


def download_file(filename):
    """Download file from server if server version is newer."""
    filepath = os.path.join(SYNC_DIR, filename)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return

        # Send local timestamp for comparison
        s.sendall(f"DOWNLOAD|{filename}|{get_file_timestamp(filepath)}".encode())

        print(f"Preparing to download: {filename}")
        print(f"Local timestamp: {time.ctime(get_file_timestamp(filepath))}")

        response = s.recv(1024).decode()

        if response.startswith("OK"):
            print(f"Server timestamp: {time.ctime(float(response.split('|')[1]))}")  # Server timestamp from response
            with open(filepath, 'wb') as f:
                while True:
                    data = s.recv(1024)
                    if not data:
                        break
                    f.write(data)
            print(f"File downloaded successfully: {filename}")
        elif response == "SKIP":
            print(f"File is already up-to-date: {filename}")
        else:
            print(f"Unexpected response: {response}")


def sync_all():
    """Sync all files in the directory."""
    for filename in os.listdir(SYNC_DIR):
        upload_file(filename)
        download_file(filename)


if __name__ == "__main__":
    os.makedirs(SYNC_DIR, exist_ok=True)

    # Check if command-line arguments are provided
    if len(sys.argv) < 3:
        print("Usage: python3 client.py <action> <filename>")
        sys.exit(1)

    action = sys.argv[1].lower()  # First argument: action (upload/download)
    filename = sys.argv[2]  # Second argument: filename

    if action == "upload":
        upload_file(filename)
    elif action == "download":
        download_file(filename)
    else:
        print("Invalid action. Use 'upload' or 'download'.")

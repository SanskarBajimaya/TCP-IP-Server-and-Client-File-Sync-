import socket
import os
import sys  # To handle command-line arguments

HOST = '127.0.0.1'  # Server IP
PORT = 65432  # Server port
SYNC_DIR = 'client_files'  # Local directory to sync

def upload_file(filename):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        filepath = os.path.join(SYNC_DIR, filename)
        if os.path.exists(filepath):
            s.sendall(f"UPLOAD|{filename}".encode())
            with open(filepath, 'rb') as f:
                s.sendfile(f)
            print(f"Uploaded: {filename}")
        else:
            print("File not found")

def download_file(filename):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(f"DOWNLOAD|{filename}".encode())
        response = s.recv(1024).decode()
        if response.startswith("OK"):
            filepath = os.path.join(SYNC_DIR, filename)
            with open(filepath, 'wb') as f:
                while True:
                    data = s.recv(1024)
                    if not data:
                        break
                    f.write(data)
            print(f"Downloaded: {filename}")
        else:
            print(response)  # Error message

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

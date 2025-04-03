import socket
import os

# Server configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 65432       # Port to listen on
SYNC_DIR = 'server_files'  # Directory to store synced files

def start_server():
    # Create sync directory if it doesn't exist
    os.makedirs(SYNC_DIR, exist_ok=True)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                data = conn.recv(1024).decode()
                if not data:
                    continue

                # Handle client commands (UPLOAD/DOWNLOAD)
                if data.startswith("UPLOAD"):
                    filename = data.split('|')[1]
                    filepath = os.path.join(SYNC_DIR, filename)
                    with open(filepath, 'wb') as f:
                        while True:
                            chunk = conn.recv(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                    print(f"Received file: {filename}")

                elif data.startswith("DOWNLOAD"):
                    filename = data.split('|')[1]
                    filepath = os.path.join(SYNC_DIR, filename)
                    if os.path.exists(filepath):
                        conn.sendall(f"OK|{filename}".encode())
                        with open(filepath, 'rb') as f:
                            conn.sendfile(f)
                    else:
                        conn.sendall(b"ERROR|File not found")

if __name__ == "__main__":
    start_server()
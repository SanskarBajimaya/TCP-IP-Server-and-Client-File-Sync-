import socket
import os
import time

HOST = '0.0.0.0'
PORT = 65432
SYNC_DIR = 'server_files'


def get_file_timestamp(filepath):
    return os.path.getmtime(filepath) if os.path.exists(filepath) else 0


def start_server():
    os.makedirs(SYNC_DIR, exist_ok=True)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, PORT))
            s.listen()
            print(f"Server listening on {HOST}:{PORT}")
        except Exception as e:
            print(f"Error starting server: {e}")
            return

        try:
            while True:
                try:
                    conn, addr = s.accept()
                    print(f"Connected by {addr}")
                except Exception as e:
                    print(f"Error accepting connection: {e}")
                    continue

                with conn:
                    try:
                        data = conn.recv(1024).decode()
                        if not data:
                            continue

                        parts = data.split('|')
                        if len(parts) < 3:
                            conn.sendall(b"ERROR|Malformed request")
                            print("Malformed data received. Ignoring request.")
                            continue

                        command = parts[0]
                        filename = parts[1]
                        filepath = os.path.join(SYNC_DIR, filename)
                        client_timestamp = float(parts[2])
                        server_timestamp = get_file_timestamp(filepath)

                        if command == "UPLOAD":
                            client_timestamp = float(parts[2])
                            server_timestamp = get_file_timestamp(filepath)

                            print(f"UPLOAD request: {filename}")
                            print(f"Client timestamp: {time.ctime(client_timestamp)}")
                            print(
                                f"Server timestamp: {time.ctime(server_timestamp)}" if server_timestamp else "File does not exist on the server.")

                            if client_timestamp > server_timestamp:
                                conn.sendall(b"OK")
                                temp_filepath = filepath + ".temp"
                                with open(temp_filepath, 'wb') as f:
                                    while True:
                                        chunk = conn.recv(1024)
                                        if not chunk:
                                            break
                                        f.write(chunk)
                                os.rename(temp_filepath, filepath)
                                print(f"File uploaded and updated: {filename}")
                            else:
                                conn.sendall(f"CONFLICT|Server has newer version".encode())

                        if command == "DOWNLOAD":
                            client_timestamp = float(parts[2])
                            server_timestamp = get_file_timestamp(filepath)
                            print(f"DOWNLOAD request: {filename}")
                            print(f"Client timestamp: {time.ctime(client_timestamp)}")
                            print(
                                f"Server timestamp: {time.ctime(server_timestamp)}" if server_timestamp else "File does not exist on the server.")
                            if os.path.exists(filepath) and server_timestamp > client_timestamp:
                                conn.sendall(f"OK|{filename}".encode())
                                with open(filepath, 'rb') as f:
                                    conn.sendfile(f)
                                print(f"File sent to client: {filename}")
                            else:
                                conn.sendall(b"SKIP")  # No newer version


                        else:
                            conn.sendall(b"ERROR|Unsupported command")
                            print(f"Unsupported command received: {command}")

                    except Exception as e:
                        print(f"Error handling client request: {e}")
        except KeyboardInterrupt:
            print("\nServer shutting down gracefully.")
            s.close()
            exit(0)


if __name__ == "__main__":
    start_server()

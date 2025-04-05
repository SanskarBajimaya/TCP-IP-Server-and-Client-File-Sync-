import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from client import upload_file  # Removed download_file as it is not used


class SyncHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            timestamp = time.ctime(os.path.getmtime(event.src_path))
            print(f"Modified file detected: {filename} at {timestamp}")
            try:
                upload_file(filename)  # Auto-upload modified file
            except Exception as e:
                print(f"Error uploading file {filename}: {e}")

    def on_created(self, event):
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            timestamp = time.ctime(os.path.getmtime(event.src_path))
            print(f"New file detected: {filename} at {timestamp}")
            try:
                upload_file(filename)  # Auto-upload new file
            except Exception as e:
                print(f"Error uploading file {filename}: {e}")


def start_watching(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    event_handler = SyncHandler()
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()
    print(f"Watching: {directory}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping observer...")
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    start_watching('client_files')

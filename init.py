import msg
import subprocess
import threading

def start_search_api_server():
    msg.info("Starting search API server workers....")
    subprocess.call(["python3", "worker.py"])

search_server_thread = threading.Thread(target=start_search_api_server)
search_server_thread.start()
msg.info("Done")
search_server_thread.join()
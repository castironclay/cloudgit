import base64
import http.server
import random
import socket
import socketserver
import string
import urllib.parse
from pathlib import Path

import yaml
from libtmux import Server
from loguru import logger
from rich import print
from tinydb import TinyDB

from githubmesh import Workflow

url = None


def read_creds_file():
    with open("keys.yaml", "r") as creds_file:
        all_creds = yaml.safe_load(creds_file)

    return all_creds


def check_listening(port: int) -> None:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex(("127.0.0.1", port))

        if result == 0:
            print("socket is open")
            return False

        else:
            return True
        s.close()

    except Exception as e:
        logger.error(e)


def listener(port: int, db: TinyDB) -> str:
    try:

        class Server(socketserver.TCPServer):
            # Avoid "address already used" error when frequently restarting the script
            allow_reuse_address = True

        class Handler(http.server.BaseHTTPRequestHandler):
            def __init__(self, *args, db=None, **kwargs):
                super().__init__(*args, **kwargs)
                self.db = db

            def do_GET(self):
                parsed_path = urllib.parse.urlparse(self.path)
                query_params = urllib.parse.parse_qs(parsed_path.query)
                global url
                try:
                    url = query_params.get("url")[0]
                    self.send_response(200, "OK")
                    self.end_headers()
                    self.wfile.write("URL Received!".encode("utf-8"))

                except TypeError:
                    self.send_response(200, "OK")
                    self.end_headers()
                    self.wfile.write("URL Missing!".encode("utf-8"))

                try:
                    config = query_params.get("config")[0]
                    decoded_bytes = base64.b64decode(config)
                    decoded_string = decoded_bytes.decode("utf-8")
                    table = db.table("deployments")
                    table.insert({"test": config})
                    print("\n")

                    print(decoded_string)
                    print("\n")
                    self.send_response(200, "OK")
                    self.end_headers()
                    self.wfile.write("config Received!".encode("utf-8"))

                except TypeError:
                    self.send_response(200, "OK")
                    self.end_headers()
                    self.wfile.write("URL Missing!".encode("utf-8"))

            # Override log_message to suppress logging
            def log_message(self, format, *args):
                # Do nothing, or you could log to a file if needed
                pass

        with Server(("", port), Handler) as httpd:
            while not url:
                httpd.handle_request()
            httpd.server_close()

        return url
    except Exception as e:
        logger.error(e)


def start_server(random_port: int, db: TinyDB) -> str:
    try:
        cf_url = None
        if check_listening(random_port):
            while not url:
                print(f"Starting listener on port {random_port}")
                cf_url = listener(random_port, db)

        return cf_url
    except Exception as e:
        logger.error(f"Error occured: {e}")


def local_cfd(server: Server, random_port: int, log_file_name: str) -> str:
    Path(f"/tmp/{log_file_name}.log").touch()
    session = server.new_session(
        session_name="local_cfd", kill_session=True, attach=False
    )
    window = session.new_window(attach=True, window_name="local_cfd")
    pane1 = window.active_pane
    pane1.send_keys(
        f"/usr/local/bin/cloudflared tunnel --logfile /tmp/{log_file_name}.log --url 127.0.0.1:{random_port}"
    )

    local_cfd_url = None
    while not local_cfd_url:
        with open(f"/tmp/{log_file_name}.log", "r") as cf_log:
            lines = cf_log.readlines()
            for line in lines:
                if ".trycloudflare.com" in line:
                    local_cfd_url = line.split("|")[1].strip()
                    break

    return local_cfd_url


def tmp_file_name() -> str:
    length = 10
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return "".join(random.choices(chars, k=length))


def main(key: str, account: str, repo: str, db: TinyDB):
    work = Workflow(key, account, repo)
    try:
        print("Starting local listener...")
        server = Server()
        random_port = random.randint(20000, 60000)
        random_file_name = tmp_file_name()
        local_cfd_url = local_cfd(server, random_port, random_file_name)
        print("Starting workflow...")
        work.start_workflow(local_cfd_url)
        work.check_running()
        print("Workflow started!")
        cf_url = start_server(random_port, db)
        print("Waiting for remote url...")
        print(
            f"wstunnel client -L 'udp://127.0.0.1:51820:127.0.0.1:51820?timeout_sec=0' wss://{cf_url[8:]}"
        )
        print("Killing local listener")
        server.kill()

    except Exception as e:
        logger.error(f"Error occured: {e}")
        logger.error("Cancelling workflow")
        work.cancel_workflow()
        server.kill()

import threading
import socket
import paramiko
import time
import os
from sftpserver.stub_sftp import StubServer, StubSFTPServer, SFTPServerInterface

class DirHandler(StubSFTPServer):
    def __init__(self, *args, **kwargs):
        super(DirHandler, self).__init__(*args, **kwargs)
        # pull ROOT ref from "Server" handler I am instantiated with
        self.ROOT = args[0]._ROOT

class SFTPThread(threading.Thread):
    def __init__(self, conn, host_key, stub_server):
        threading.Thread.__init__(self)
        self._conn = conn
        self._host_key = host_key
        self._stub_server = stub_server

    def run(self):
        try:
            transport = paramiko.Transport(self._conn)
            transport.add_server_key(self._host_key)
            transport.set_subsystem_handler(
                'sftp', paramiko.SFTPServer, DirHandler)

            transport.start_server(server=self._stub_server)
            channel = transport.accept()
            while transport.is_active():
                time.sleep(1)
        finally:
            self._conn.close()


class SFTPServer():
    def __init__(self, host_name, port, key, root_dir):
        self.host_name = host_name
        self.port = port
        self.keyfile = key
        self.backlog = 0
        self.timeout_sec = 0.5
        self.running = False
        self.log_level = 'INFO'
        self.stub_server = StubServer()
        self.stub_server._ROOT = root_dir

    def _listen_loop(self):
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                conn.settimeout(self.timeout_sec)
                sftp_thread = SFTPThread(conn, self.host_key, self.stub_server)
                sftp_thread.setDaemon(True)
                sftp_thread.start()
            except:
                # ignore timeouts
                pass

    def start(self):
        paramiko.common.logging.basicConfig(
            level=getattr(paramiko.common, self.log_level))
        self.host_key = paramiko.RSAKey.from_private_key_file(self.keyfile)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.server_socket.bind((self.host_name, self.port))
        self.server_socket.listen(self.backlog)
        self.server_socket.settimeout(self.timeout_sec)
        self.listen_thread = threading.Thread(target=self._listen_loop)
        self.running = True
        self.listen_thread.start()

    def stop(self):
        self.running = False
        self.server_socket.close()
        self.listen_thread.join()
        self.server_socket.close()


if __name__ == '__main__':
    sftp_server = SFTPServer(host_name='localhost',
                             port=1234, key='tests/lr_sftp_test.key', root_dir = os.getcwd())
    sftp_server.start()

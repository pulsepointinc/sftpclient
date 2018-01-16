from .context import SFTPClientConfig, SFTPServer
import socket
import tempfile
import os
import shutil

class SFTPServerScaffolding(object):
    def _find_free_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost',0))
        s.listen(1)
        port = s.getsockname()[1]
        s.close()
        return port

    def __init__(self):
        self.root_dir = tempfile.mkdtemp()

    def add_file(self, file_name, content):
        abs_file_path = os.path.join(self.root_dir, file_name)
        abs_dir_path = os.path.dirname(abs_file_path)
        if not os.path.exists(abs_dir_path):
            os.makedirs(abs_dir_path)
        with open(abs_file_path, 'w') as file_handle:
            file_handle.write(content)


    def setUp(self):
        port = self._find_free_port()
        self.sftp_server = SFTPServer(host_name='localhost', port = port, key = 'tests/lr_sftp_test.key', root_dir = self.root_dir)
        self.sftp_server.start()
        self.sftp_client_config = SFTPClientConfig(host = 'localhost', port = port)
        return self

    def tearDown(self):
        self.sftp_server.stop()
        # extra precaution from chuckleheads setting self.root_dir to '/'
        if len(self.root_dir) > 5:
            shutil.rmtree(self.root_dir)
        return self
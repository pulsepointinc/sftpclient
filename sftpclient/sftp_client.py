'''
SFTP client configuration object
'''
class SFTPClientConfig(object):
    def __init__(self, host = '', port = 22, username = '', password = ''):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
    def set_host(self, host):
        self.host = host
        return self
    def get_host(self):
        return self.host
    def set_port(self, port):
        self.port = port
        return self
    def get_port(self):
        return self.port
    def set_username(self, username):
        self.username = username
        return self
    def get_username(self):
        return self.username
    def set_password(self, password):
        self.password = password
        return self
    def get_password(self):
        return self.password
    
class SFTPClient(object):
    def __init__(self, config):
        assert isinstance(config, SFTPClientConfig)
        self.config = config

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        pass

    def close(self):
        pass

    def ls(self, dir, recursive = False):
        pass
    
    def get(self, path, callback):
        pass
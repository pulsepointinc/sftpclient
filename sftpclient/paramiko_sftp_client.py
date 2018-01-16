from .sftp_client import SFTPClient
import paramiko, stat

'''
Quicker transport for paramiko
'''
class FastTransport(paramiko.Transport):
    def __init__(self, sock):
        super(FastTransport, self).__init__(sock)
        self.window_size = 2147483647
        self.packetizer.REKEY_BYTES = pow(2, 40)
        self.packetizer.REKEY_PACKETS = pow(2, 40)

'''
A paramiko SFTPClient implementation
'''
class ParamikoSFTPClient(SFTPClient):
    def __init__(self, *args, **kwargs):
        super(ParamikoSFTPClient, self).__init__(*args, **kwargs)
        
    def connect(self):
        transport = FastTransport((self.config.get_host(), self.config.get_port()))
        transport.start_client()
        transport.auth_password(self.config.get_username(), self.config.get_password())
        self.client = paramiko.SFTPClient.from_transport(transport)
        return self
   
    def get(self, remote_filename, write_fn):
        sftp_file = self.client.open(remote_filename)
        byte_buffer = bytearray(8192)
        # read chunks of file
        bytes_read = sftp_file.readinto(byte_buffer)
        while bytes_read > 0:
            # write chunks to pipe
            write_fn(byte_buffer, bytes_read)
            # read chunks of file
            bytes_read = sftp_file.readinto(byte_buffer)
    
    def ls(self, remotepath, recursive = False):
        if recursive == False:
            return self.client.listdir(remotepath)
        else:
            files = []
            for attrs in self.client.listdir_attr(remotepath):
                kind = stat.S_IFMT(attrs.st_mode)
                if kind == stat.S_IFDIR:
                    for child_fname in self.ls(remotepath + '/' + attrs.filename, True):
                        files.append(attrs.filename + '/' + child_fname)
                else:
                    files.append(attrs.filename)
            return files

    def close(self):
        self.client.close()
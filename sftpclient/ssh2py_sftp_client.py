import logging
import socket
import stat
import time

from ssh2.error_codes import LIBSSH2_ERROR_EAGAIN
from ssh2.session import Session

from .sftp_client import SFTPClient

logger = logging.getLogger('ssh2py_sftp_client')

class SFTPConn():
    def __init__(self):
        self.timeoutMs = 10000
        pass

    def connect(self, host, port, username, password):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        try:
            ssh_session = Session()
            try:
                ssh_session.set_timeout(self.timeoutMs)
                ssh_session.handshake(sock)
                ssh_session.userauth_password(username, password)
                self._sftp_session = ssh_session.sftp_init()
                # set non_blocking_mode
                ssh_session.set_blocking(False)
                self._socket = sock
                self._ssh_session = ssh_session
            except:
                self._close_session(ssh_session)
                raise
        except:
            self._close_socket(sock)
            raise

        return self

    def connect_with_retries(self, host, port, username, password, max_retries):
        retries = 0
        while retries <= max_retries:
            try:
                self.connect(host, port, username, password)
                return self
            except:
                logger.error("Error while connecting to sftp. Will retry.")
                retries += 1
                time.sleep(1)
                if retries > max_retries:
                    raise

    def sftp(self):
        return self._sftp_session

    def _close_session(self, session):
        try:
            session.disconnect()
        except:
            pass

    def _close_socket(self, socket):
        try:
            socket.shutdown()
        except:
            pass
        try:
            socket.close()
        except:
            pass

    def close(self):
        if hasattr(self, '_sftp_session'):
            del (self._sftp_session)
        if hasattr(self, '_ssh_session'):
            self._ssh_session.set_blocking(True)
            self._close_session(self._ssh_session)
            del (self._ssh_session)
        if hasattr(self, '_socket'):
            self._close_socket(self._socket)
            del (self._socket)


class SSH2PySFTPClient(SFTPClient):
    def __init__(self, *args, **kwargs):
        super(SSH2PySFTPClient, self).__init__(*args, **kwargs)
        self._conn = None
        self._retry_attempts = 10

    def connect(self):
        if self._conn == None:
            self._conn = SFTPConn().connect_with_retries(self.config.get_host(), self.config.get_port(), self.config.get_username(),
                                            self.config.get_password(), self._retry_attempts)
        return self

    def close(self):
        if self._conn != None:
            self._conn.close()
            del (self._conn)
            self._conn = None
        return self

    def _opendir_fh(self, dir):
        attempts = 0
        while attempts < self._retry_attempts:
            fh = self._conn.sftp().opendir(dir)
            if fh != None:
                return fh
            attempts = attempts + 1
            time.sleep(1)
        raise ValueError('Could not obtain remote directory handle')

    def _open_path(self, path):
        attempts = 0
        while attempts < self._retry_attempts:
            fh = self._conn.sftp().open(path, 0x00000001, 0)
            if fh != None:
                return fh
            attempts = attempts + 1
            logger.error("Error while opening sftp file handle. Will retry")
            time.sleep(1)
        raise ValueError('Could not obtain remote file handle')

    def ls(self, dir, recursive=False):
        ret = []
        fh = self._opendir_fh(dir)
        try:
            for size, buf, attrs in fh.readdir():
                if size == LIBSSH2_ERROR_EAGAIN:
                    continue
                if recursive == False:
                    ret.append(buf)
                else:
                    kind = stat.S_IFMT(attrs.permissions)
                    if kind == stat.S_IFDIR:
                        for child_fname in self.ls(dir + '/' + buf, True):
                            ret.append(buf + '/' + child_fname)
                    else:
                        ret.append(buf)

        finally:
            fh.close()
        return ret

    def get(self, path, target):
        fh = self._open_path(path)
        try:
            size, data = fh.read()
            while size == LIBSSH2_ERROR_EAGAIN:
                size, data = fh.read()
            target(data, size)
            for size, data in fh:
                if size != LIBSSH2_ERROR_EAGAIN:
                    target(data, size)
        finally:
            fh.close()

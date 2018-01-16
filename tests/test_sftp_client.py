from .context import ParamikoSFTPClient, SSH2PySFTPClient, SFTPServerScaffolding, SFTPClientConfig

import unittest, socket, random, string

# make up some constant random content shared among all tests
rando_content = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in xrange(1024 * 1024 * 2))

'''
Tests for SFTPClient implementations
'''
class SFTPClientTestBase(object):
    
    def setUp(self):
        self.sftp_scaffolding = SFTPServerScaffolding().setUp()
        self.big_file_content = rando_content
        self.big_file_filename = 'a_file'
        self.sftp_scaffolding.add_file(self.big_file_filename, self.big_file_content)
        # add some directories
        self.sftp_scaffolding.add_file('dir1/a', 'a')
        self.sftp_scaffolding.add_file('dir1/dir2/b', 'b')
        self.sftp_scaffolding.add_file('dir1/dir2/c', 'c')
        

    def tearDown(self):
        self.sftp_scaffolding.tearDown()
        self.sftp_client.close()

    def test_ls(self):
        with self.sftp_client as sftp:
            files = sftp.ls('/')
            assert self.big_file_filename in files
            assert 'dir1' in files
            assert 'dir1/dir2' not in files

    def test_recursive_ls(self):
        with self.sftp_client as sftp:
            files = sftp.ls('/', recursive = True)
            assert self.big_file_filename in files
            assert 'dir1/a' in files
            assert 'dir1/dir2/b' in files
            assert 'dir1/dir2/c' in files
        
        
    def test_get(self):
        class Writer:
            def __init__(self):
                self.written = 0
                self.content = ''
            def write_fn(self, buf, lent):
                self.written = self.written + lent
                self.content = self.content + buf[0:lent]

        w = Writer()
        with self.sftp_client as sftp:
            self.sftp_client.get('/'+self.big_file_filename, w.write_fn)
            assert w.written == len(self.big_file_content)
            assert w.content == self.big_file_content

class ParamikoSFTPClientTest(SFTPClientTestBase, unittest.TestCase):
    def setUp(self):
        super(ParamikoSFTPClientTest, self).setUp()
        self.sftp_client = ParamikoSFTPClient(self.sftp_scaffolding.sftp_client_config)

class SSH2PySFTPClientTest(SFTPClientTestBase, unittest.TestCase):
    def setUp(self):
        super(SSH2PySFTPClientTest, self).setUp()
        self.sftp_client = SSH2PySFTPClient(self.sftp_scaffolding.sftp_client_config)

if __name__ == '__main__':
    unittest.main()
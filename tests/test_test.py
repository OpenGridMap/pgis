import unittest
import tempfile
import os
from app import GisApp

class SimpleTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, GisApp.config['DATABASE'] = tempfile.mkstemp()
        GisApp.config['TESTING'] = True
        self.app = GisApp.test_client()
        #app.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(GisApp.config['DATABASE'])

    def test_assert(self):
        assert '' == ''

if __name__ == '__main__':
    unittest.main()
import unittest

import os
import tempfile
import shutil

import bonesis
import bonesis.aeon

class TestAEONImport(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)


    def test_import_with_constant(self):
        """
        Source: https://github.com/bnediction/bonesis/issues/6
        """
        fpath = os.path.join(self.test_dir, "test1.aeon")
        with open(fpath, "w") as fp:
            fp.write("""#name:aeon_test
$A:A & T
A -> A
T -> A
A ->? B
$T:true
""")

        dom = bonesis.aeon.AEONDomain.from_aeon_file(fpath)
        bo = bonesis.BoNesis(dom)
        self.assertEqual(bo.boolean_networks().count(), 3)

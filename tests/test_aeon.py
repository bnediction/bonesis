import unittest

import os
import tempfile
import shutil

import bonesis
import bonesis.aeon

import biodivine_aeon as ba

class TestAEONImport(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)


    def test_import_with_constant(self):
        """
        Source: https://github.com/bnediction/bonesis/issues/6
        """
        network = ba.BooleanNetwork.from_aeon(
        """
            #name:aeon_test
            $A:A & T
            A -> A
            T -> A
            A ->? B
            $T:true
        """)

        dom = bonesis.aeon.AEONDomain(network)
        bo = bonesis.BoNesis(dom)
        self.assertEqual(bo.boolean_networks().count(), 3)

    def test_regulation_properties_1(self):
        network_a = ba.BooleanNetwork.from_aeon(
        """
            A -> X
            B -? X
            $A: true
            $B: false
        """)

        # There should be 4 interpretations of the $X function.
        dom = bonesis.aeon.AEONDomain(network_a)
        bo = bonesis.BoNesis(dom)
        self.assertEqual(bo.boolean_networks().count(), 4)

    def test_regulation_properties_2(self):
        network_a = ba.BooleanNetwork.from_aeon(
        """
            A -?? X
            B -|? X
            $A: true
            $B: false
        """)

        # There should be 9 interpretations of the $X function.
        dom = bonesis.aeon.AEONDomain(network_a)
        bo = bonesis.BoNesis(dom)           
        self.assertEqual(bo.boolean_networks().count(), 9)

    def test_partial_function_1(self):
        network_a = ba.BooleanNetwork.from_aeon(
        """
            A -> X
            B -|? X
            $X: A & f(B)
            $A: true
            $B: false
        """)

        # There should be 2 interpretations of the $X function.
        dom = bonesis.aeon.AEONDomain(network_a)
        bo = bonesis.BoNesis(dom)
        print(bo.boolean_networks().count())
        bns = bo.boolean_networks(limit=10)
        for bn in bns:
            print(bn)
        self.assertEqual(bo.boolean_networks().count(), 2)

    def test_partial_function_2(self):
        network_a = ba.BooleanNetwork.from_aeon(
        """
            A -> X
            B -|? X
            $X: A & f(B)
            $A: true
            $B: false
        """)

        # There should be 0 interpretations of the $X function.
        dom = bonesis.aeon.AEONDomain(network_a)
        bo = bonesis.BoNesis(dom)
        print(bo.boolean_networks().count())
        bns = bo.boolean_networks(limit=10)
        for bn in bns:
            print(bn)
        self.assertEqual(bo.boolean_networks().count(), 0)
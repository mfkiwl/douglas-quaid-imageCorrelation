# -*- coding: utf-8 -*-

import logging
import unittest


class TestClusterMatcher(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        self.logger = logging.getLogger()
        # self.conf = .Default_configuration()

    def test_absolute_truth_and_meaning(self):
        self.assertTrue(True)

    '''
    def test_get_proximity_graph():
        pass

    def test_results_list_to_graph():
        pass
    '''

if __name__ == '__main__':
    unittest.main()

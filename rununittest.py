"""
The purpose of this is to see the coverage of the unit tests, so they can be
added to accordingly. It uses unittest to do this as well as coverage script
from nedbatchelder.com/code/coverage
"""

from unittest import TestSuite, TestLoader, TextTestRunner

#import all the stuff we expect users to use    
from rbnworld import *


if __name__ == "__main__":
    #because we want coverage, we do not want to auto-discover tests!
    suite = TestSuite()
    loader = TestLoader()
    
    TextTestRunner(verbosity=2).run(suite)

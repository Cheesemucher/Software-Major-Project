#!/usr/bin/env python3
"""
Test runner for the floor planning application
"""

import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def run_all_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test modules
    suite.addTests(loader.discover('tests/unit'))
    suite.addTests(loader.discover('tests/integration'))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_unit_tests():
    """Run only unit tests"""
    loader = unittest.TestLoader()
    suite = loader.discover('tests/unit')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def run_integration_tests():
    """Run only integration tests"""
    loader = unittest.TestLoader()
    suite = loader.discover('tests/integration')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run tests for floor planning app')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    
    args = parser.parse_args()
    
    if args.unit:
        success = run_unit_tests()
    elif args.integration:
        success = run_integration_tests()
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
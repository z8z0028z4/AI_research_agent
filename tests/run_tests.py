#!/usr/bin/env python3
"""
Test Runner for AI Research Agent
================================

A simple script to run all tests or specific test categories.
"""

import os
import sys
import subprocess
import importlib.util
from typing import List, Dict

# Add the parent directory to the path so tests can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestRunner:
    def __init__(self):
        self.test_files = self._discover_test_files()
        self.test_categories = {
            'core': ['test_fixes.py', 'test_fixed_rag_core.py', 'test_improved_rag_core.py', 'test_model_config.py'],
            'gpt5': ['test_gpt5_parameters.py', 'test_gpt5_response.py', 'test_gpt5_reasoning_simple.py', 
                    'test_gpt5_improved_handling.py', 'test_gpt5_incomplete_handling.py'],
            'workflow': ['test_full_proposal_workflow.py', 'test_proposal_workflow.py', 'test_simple_proposal.py'],
            'settings': ['test_dynamic_params.py', 'test_frontend_settings.py', 'test_model_specific_params.py', 'test_settings_persistence.py'],
            'debug': ['test_reasoning_mode_debug.py']
        }
    
    def _discover_test_files(self) -> List[str]:
        """Discover all test files in the current directory."""
        test_files = []
        for file in os.listdir('.'):
            if file.startswith('test_') and file.endswith('.py'):
                test_files.append(file)
        return sorted(test_files)
    
    def run_single_test(self, test_file: str) -> bool:
        """Run a single test file."""
        print(f"\n🧪 Running: {test_file}")
        print("=" * 50)
        
        try:
            # Import and run the test module
            spec = importlib.util.spec_from_file_location("test_module", test_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for main execution block
            if hasattr(module, '__name__') and module.__name__ == '__main__':
                print(f"✅ {test_file} completed successfully")
                return True
            else:
                print(f"⚠️ {test_file} has no main execution block")
                return False
                
        except Exception as e:
            print(f"❌ {test_file} failed: {str(e)}")
            return False
    
    def run_category(self, category: str) -> Dict[str, bool]:
        """Run all tests in a specific category."""
        if category not in self.test_categories:
            print(f"❌ Unknown category: {category}")
            print(f"Available categories: {list(self.test_categories.keys())}")
            return {}
        
        print(f"\n📂 Running {category} tests...")
        results = {}
        
        for test_file in self.test_categories[category]:
            if test_file in self.test_files:
                results[test_file] = self.run_single_test(test_file)
            else:
                print(f"⚠️ Test file not found: {test_file}")
                results[test_file] = False
        
        return results
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all test files."""
        print("\n🚀 Running all tests...")
        results = {}
        
        for test_file in self.test_files:
            results[test_file] = self.run_single_test(test_file)
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print a summary of test results."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        print(f"Total tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success rate: {(passed/total)*100:.1f}%")
        
        if passed < total:
            print("\n❌ Failed tests:")
            for test_file, result in results.items():
                if not result:
                    print(f"  - {test_file}")
        
        print("=" * 60)

def main():
    """Main function to handle command line arguments."""
    runner = TestRunner()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'all':
            results = runner.run_all_tests()
            runner.print_summary(results)
        
        elif command in runner.test_categories:
            results = runner.run_category(command)
            runner.print_summary(results)
        
        elif command == 'list':
            print("\n📋 Available test categories:")
            for category, files in runner.test_categories.items():
                print(f"\n{category.upper()}:")
                for file in files:
                    status = "✅" if file in runner.test_files else "❌"
                    print(f"  {status} {file}")
        
        elif command == 'help':
            print("""
🧪 Test Runner Usage:
====================

python run_tests.py [command]

Commands:
  all     - Run all tests
  core    - Run core functionality tests
  gpt5    - Run GPT-5 specific tests
  workflow - Run workflow tests
  settings - Run settings and configuration tests
  debug   - Run debug and development tests
  list    - List all test categories and files
  help    - Show this help message

Examples:
  python run_tests.py all
  python run_tests.py gpt5
  python run_tests.py core
            """)
        
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python run_tests.py help' for usage information")
    
    else:
        # Default: run all tests
        results = runner.run_all_tests()
        runner.print_summary(results)

if __name__ == "__main__":
    main() 
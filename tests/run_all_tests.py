#!/usr/bin/env python3
"""
Test runner script for the chatbot application.
This script runs all the test scripts in the tests directory.
"""

import os
import sys
import argparse
import subprocess
import time
import signal
from datetime import datetime

# Test scripts to run
TEST_SCRIPTS = [
    # API Tests
    "test_api.py",
    "test_chatbot.py",
    
    # Functional Tests
    "test_comprehensive.py",
    "test_conversation_scenarios.py",
    
    # Storage Tests
    "test_csv_storage.py",
    
    # Performance Tests
    "test_performance.py"
]

def run_test(script_name, verbose=False):
    """Run a single test script"""
    print(f"\n{'='*80}")
    print(f"Running {script_name}")
    print(f"{'='*80}")
    
    # Set environment variable for testing mode
    env = os.environ.copy()
    env["TESTING"] = "True"
    
    # Run the test script
    cmd = [sys.executable, f"tests/{script_name}"]
    
    try:
        if verbose:
            # Run with output displayed
            process = subprocess.run(cmd, env=env, check=True)
        else:
            # Run with output captured
            process = subprocess.run(
                cmd, 
                env=env, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                check=True
            )
        
        print(f"✅ {script_name} completed successfully")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"❌ {script_name} failed with exit code {e.returncode}")
        
        if not verbose and e.stdout:
            print("\nStandard output:")
            print(e.stdout)
        
        if not verbose and e.stderr:
            print("\nStandard error:")
            print(e.stderr)
        
        return False

def check_server_running():
    """Check if the server is running"""
    import socket
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(("localhost", 8000))
        s.close()
        return True
    except:
        return False

def start_server():
    """Start the server for testing"""
    print("Starting server for testing...")
    
    # Set environment variable for testing mode
    env = os.environ.copy()
    env["TESTING"] = "True"
    
    # Start the server
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "localhost", "--port", "8000"]
    
    try:
        # Start the server as a subprocess
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if os.name != 'nt' else None
        )
        
        # Wait for the server to start
        max_attempts = 30
        for attempt in range(max_attempts):
            if check_server_running():
                print(f"Server started successfully after {attempt + 1} attempts")
                # Give the server a moment to fully initialize
                time.sleep(2)
                return process
            
            # Check if process is still running
            if process.poll() is not None:
                print(f"Server process exited with code {process.returncode}")
                stderr = process.stderr.read().decode('utf-8')
                print(f"Server stderr: {stderr}")
                return None
                
            print(f"Waiting for server to start (attempt {attempt + 1}/{max_attempts})...")
            time.sleep(1)
        
        # If we get here, the server didn't start
        print("Failed to start server after maximum attempts")
        stop_server(process)
        return None
    
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        return None

def stop_server(process):
    """Stop the server"""
    if process:
        print("Stopping server...")
        try:
            if os.name != 'nt':
                # Send the signal to the process group on Unix
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                # On Windows
                process.terminate()
            
            # Wait for the process to terminate
            for _ in range(5):
                if process.poll() is not None:
                    break
                time.sleep(1)
            
            # Force kill if still running
            if process.poll() is None:
                if os.name != 'nt':
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                else:
                    process.kill()
            
            process.wait()
            print("Server stopped")
        except Exception as e:
            print(f"Error stopping server: {str(e)}")

def run_all_tests(args):
    """Run all test scripts"""
    start_time = time.time()
    results = {}
    
    print(f"\n{'='*80}")
    print(f"Starting test run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    # Check if server is already running
    server_running = check_server_running()
    server_process = None
    
    if not server_running and not args.no_server:
        server_process = start_server()
        if not server_process:
            print("Cannot run tests without a server")
            return False
    elif server_running and not args.no_server:
        print("Server is already running. Using existing server.")
    
    try:
        # Run each test script
        for script in TEST_SCRIPTS:
            if args.test and script not in args.test:
                continue
            
            results[script] = run_test(script, args.verbose)
        
        # Print summary
        print(f"\n{'='*80}")
        print("Test Run Summary")
        print(f"{'='*80}")
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for script, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {script}")
        
        print(f"\nPassed: {passed}/{total} ({passed/total*100:.1f}%)")
        print(f"Total time: {time.time() - start_time:.2f} seconds")
        
        if passed == total:
            print("\n🎉 All tests passed successfully! 🎉")
            return True
        else:
            print(f"\n⚠️ {total-passed} tests failed. Please check the output above for details.")
            return False
    
    finally:
        # Stop the server if we started it
        if server_process:
            stop_server(server_process)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run tests for the chatbot application")
    parser.add_argument("--test", "-t", action="append", help="Specific test script to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show test output")
    parser.add_argument("--no-server", "-n", action="store_true", help="Don't start the server")
    args = parser.parse_args()
    
    success = run_all_tests(args)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
import os
import sys
import time
import subprocess
from pathlib import Path

def get_python_files(directory):
    return {str(p) for p in Path(directory).rglob("*.py") if ".venv" not in str(p)}

def get_files_mtimes(files):
    return {f: os.stat(f).st_mtime for f in files}

def main():
    directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    process = None
    
    def start_process():
        nonlocal process
        if process:
            process.terminate()
            process.wait()
        
        main_script = os.path.join(directory, "main.py")
        process = subprocess.Popen(
            [sys.executable, main_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        return process

    python_files = get_python_files(directory)
    mtimes = get_files_mtimes(python_files)
    process = start_process()
    
    print("Watching for file changes... Press Ctrl+C to stop")
    
    try:
        while True:
            # Check for process output
            if process.poll() is not None:
                print("Process ended, restarting...")
                process = start_process()
                
            while line := process.stdout.readline():
                print(line, end="")
            while line := process.stderr.readline():
                print(line, end="", file=sys.stderr)
                
            # Check for file changes
            new_mtimes = get_files_mtimes(python_files)
            if new_mtimes != mtimes:
                changed = [f for f in python_files if new_mtimes[f] != mtimes[f]]
                print(f"\nDetected changes in: {', '.join(changed)}")
                print("Restarting process...")
                mtimes = new_mtimes
                process = start_process()
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        if process:
            process.terminate()
        print("\nStopping...")

if __name__ == "__main__":
    main()

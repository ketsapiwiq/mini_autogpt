"""File operation commands."""
from typing import Dict, Any, Optional
import os
import json
import subprocess
from . import Command
from utils.log import log, debug

class ReadFileCommand(Command):
    """Read the contents of a file."""
    
    def get_args(self) -> Dict[str, str]:
        return {
            "filepath": "Path to the file to read"
        }
        
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return "filepath" in args and os.path.exists(args["filepath"])
        
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        filepath = args["filepath"]
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            return {"status": "success", "content": content}
        except Exception as e:
            error = f"Failed to read file {filepath}: {str(e)}"
            log(error)
            return {"status": "error", "error": error}

class LookupFilesCommand(Command):
    """Find files matching a pattern."""
    
    def get_args(self) -> Dict[str, str]:
        return {
            "pattern": "Pattern to search for (e.g. *.py)",
            "directory": "Directory to search in (optional, defaults to current)"
        }
        
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return "pattern" in args
        
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        pattern = args["pattern"]
        directory = args.get("directory", ".")
        try:
            cmd = ["find", directory, "-name", pattern]
            result = subprocess.run(cmd, capture_output=True, text=True)
            files = result.stdout.strip().split('\n')
            files = [f for f in files if f]  # Remove empty strings
            return {"status": "success", "files": files}
        except Exception as e:
            error = f"Failed to lookup files: {str(e)}"
            log(error)
            return {"status": "error", "error": error}

class LookupTermCommand(Command):
    """Search for a term in files."""
    
    def get_args(self) -> Dict[str, str]:
        return {
            "term": "Term to search for",
            "directory": "Directory to search in (optional, defaults to current)",
            "file_pattern": "File pattern to search in (optional, e.g. *.py)"
        }
        
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return "term" in args
        
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        term = args["term"]
        directory = args.get("directory", ".")
        file_pattern = args.get("file_pattern", "*")
        try:
            cmd = ["grep", "-r", "-n", term]
            if file_pattern != "*":
                cmd.extend(["--include", file_pattern])
            cmd.append(directory)
            result = subprocess.run(cmd, capture_output=True, text=True)
            matches = result.stdout.strip().split('\n')
            matches = [m for m in matches if m]  # Remove empty strings
            return {"status": "success", "matches": matches}
        except Exception as e:
            error = f"Failed to lookup term: {str(e)}"
            log(error)
            return {"status": "error", "error": error}

class ExecDockerCommand(Command):
    """Execute a Docker command."""
    
    def get_args(self) -> Dict[str, str]:
        return {
            "command": "Docker command to execute",
            "args": "Additional arguments (optional)"
        }
        
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return "command" in args
        
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        command = args["command"]
        docker_args = args.get("args", [])
        try:
            cmd = ["docker", command] + (docker_args if isinstance(docker_args, list) else [docker_args])
            result = subprocess.run(cmd, capture_output=True, text=True)
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            error = f"Failed to execute docker command: {str(e)}"
            log(error)
            return {"status": "error", "error": error}

class GitStashCommand(Command):
    """Stash current changes."""
    
    def get_args(self) -> Optional[Dict[str, str]]:
        return None  # No arguments needed
        
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return True  # No arguments to validate
        
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = subprocess.run(["git", "stash"], capture_output=True, text=True)
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            error = f"Failed to stash changes: {str(e)}"
            log(error)
            return {"status": "error", "error": error}

class GitCommitCurrentCommand(Command):
    """Commit current changes."""
    
    def get_args(self) -> Dict[str, str]:
        return {
            "message": "Commit message"
        }
        
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return "message" in args
        
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        message = args["message"]
        try:
            # First add all changes
            add_result = subprocess.run(["git", "add", "."], capture_output=True, text=True)
            if add_result.returncode != 0:
                return {"status": "error", "error": f"Failed to add changes: {add_result.stderr}"}
            
            # Then commit
            commit_result = subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True)
            return {
                "status": "success" if commit_result.returncode == 0 else "error",
                "output": commit_result.stdout,
                "error": commit_result.stderr if commit_result.returncode != 0 else None
            }
        except Exception as e:
            error = f"Failed to commit changes: {str(e)}"
            log(error)
            return {"status": "error", "error": error}

class GitSwitchBranchCommand(Command):
    """Switch to or create a git branch."""
    
    def get_args(self) -> Dict[str, str]:
        return {
            "branch": "Branch name",
            "create_if_needed": "Create branch if it doesn't exist (optional, defaults to True)"
        }
        
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return "branch" in args
        
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        branch = args["branch"]
        create_if_needed = args.get("create_if_needed", True)
        
        try:
            if create_if_needed:
                # Check if branch exists
                check_result = subprocess.run(["git", "show-ref", "--verify", f"refs/heads/{branch}"], 
                                           capture_output=True, text=True)
                if check_result.returncode != 0:
                    # Branch doesn't exist, create it
                    create_result = subprocess.run(["git", "checkout", "-b", branch], 
                                                capture_output=True, text=True)
                    return {
                        "status": "success" if create_result.returncode == 0 else "error",
                        "output": create_result.stdout,
                        "error": create_result.stderr if create_result.returncode != 0 else None
                    }
            
            # Switch to existing branch
            switch_result = subprocess.run(["git", "checkout", branch], capture_output=True, text=True)
            return {
                "status": "success" if switch_result.returncode == 0 else "error",
                "output": switch_result.stdout,
                "error": switch_result.stderr if switch_result.returncode != 0 else None
            }
        except Exception as e:
            error = f"Failed to switch branch: {str(e)}"
            log(error)
            return {"status": "error", "error": error}

class CreateFileCommand(Command):
    """Create a new file with the specified content."""
    
    def get_args(self) -> Dict[str, str]:
        return {
            "filepath": "Path to the file to create",
            "content": "Content to write to the file"
        }
        
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return "filepath" in args and "content" in args
        
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        filepath = args["filepath"]
        content = args["content"]
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(content)
            return {"status": "success", "filepath": filepath}
        except Exception as e:
            error = f"Failed to create file {filepath}: {str(e)}"
            log(error)
            return {"status": "error", "error": error}

class ApplyDiffToFileCommand(Command):
    """Apply a diff to an existing file."""
    
    def get_args(self) -> Dict[str, str]:
        return {
            "filepath": "Path to the file to modify",
            "diff": "The diff to apply (unified diff format)"
        }
        
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return "filepath" in args and "diff" in args and os.path.exists(args["filepath"])
        
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        filepath = args["filepath"]
        diff = args["diff"]
        try:
            # Create a temporary file with the diff
            temp_diff_file = filepath + ".diff"
            with open(temp_diff_file, 'w') as f:
                f.write(diff)
            
            # Apply the patch
            result = subprocess.run(
                ["patch", filepath, temp_diff_file],
                capture_output=True,
                text=True
            )
            
            # Clean up
            os.remove(temp_diff_file)
            
            if result.returncode == 0:
                return {"status": "success", "message": result.stdout}
            else:
                error = f"Failed to apply diff: {result.stderr}"
                log(error)
                return {"status": "error", "error": error}
                
        except Exception as e:
            error = f"Failed to apply diff to {filepath}: {str(e)}"
            log(error)
            return {"status": "error", "error": error}

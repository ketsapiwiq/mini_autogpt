"""File operation commands."""
from typing import Dict, Any, Optional
from . import Command
from .prompt_builder import BasicPromptTemplate
import os
import json
from utils.log import log
import subprocess

class ReadFileCommand(Command):
    """Command to read the contents of a file."""
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return isinstance(args.get("filepath"), str)
    
    def get_args(self) -> Dict[str, str]:
        return {
            "filepath": "Path to the file to read"
        }
    
    def get_prompt_template(self) -> Optional[BasicPromptTemplate]:
        """Get prompt template for file content analysis."""
        template = """You are analyzing the contents of a file. Follow these guidelines:

File Information:
- Path: {filepath}
- Type: {file_type}
- Size: {file_size}
- Last Modified: {last_modified}

File Contents:
{content}

Analysis Tasks:
1. Identify the main purpose and structure of the file
2. Extract key information and patterns
3. Note any potential issues or improvements
4. Consider the file's role in the larger system
5. Suggest any necessary modifications

Consider:
1. Is the file well-organized and properly formatted?
2. Are there any security or performance concerns?
3. Does it follow best practices for its file type?
4. Are there any missing dependencies or requirements?
5. Could the file be optimized or improved?"""
        return BasicPromptTemplate(template)
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        filepath = args["filepath"]
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Get file metadata
            stats = os.stat(filepath)
            file_info = {
                "filepath": filepath,
                "file_type": os.path.splitext(filepath)[1],
                "file_size": stats.st_size,
                "last_modified": stats.st_mtime,
                "content": content
            }
            
            return {
                "status": "success",
                "content": content,
                "prompt": self.get_formatted_prompt(file_info)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

class LookupFilesCommand(Command):
    """Command to find files matching a pattern."""
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return isinstance(args.get("pattern"), str)
    
    def get_args(self) -> Dict[str, str]:
        return {
            "pattern": "Pattern to search for (e.g. *.py)",
            "directory": "Directory to search in (optional, defaults to current)"
        }
    
    def get_prompt_template(self) -> Optional[BasicPromptTemplate]:
        """Get prompt template for file search analysis."""
        template = """You are analyzing the results of a file search. Follow these guidelines:

Search Parameters:
- Pattern: {pattern}
- Directory: {directory}
- Depth: {depth}

Search Results:
{results}

Analysis Tasks:
1. Categorize the found files by type and purpose
2. Identify patterns in file organization
3. Note any potential issues in file structure
4. Consider relationships between files
5. Suggest improvements to file organization

Consider:
1. Is the file organization logical and clear?
2. Are there any missing or redundant files?
3. Does the structure follow project conventions?
4. Are there any security or maintenance concerns?
5. Could the file organization be improved?"""
        return BasicPromptTemplate(template)
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        pattern = args["pattern"]
        directory = args.get("directory", ".")
        
        try:
            import glob
            matches = glob.glob(os.path.join(directory, pattern), recursive=True)
            
            search_info = {
                "pattern": pattern,
                "directory": directory,
                "depth": pattern.count(os.path.sep) + 1,
                "results": "\n".join(matches)
            }
            
            return {
                "status": "success",
                "matches": matches,
                "prompt": self.get_formatted_prompt(search_info)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

class LookupTermCommand(Command):
    """Command to search for a term in files."""
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return isinstance(args.get("term"), str)
    
    def get_args(self) -> Dict[str, str]:
        return {
            "term": "Term to search for",
            "directory": "Directory to search in (optional, defaults to current)",
            "file_pattern": "File pattern to search in (optional, e.g. *.py)"
        }
    
    def get_prompt_template(self) -> Optional[BasicPromptTemplate]:
        """Get prompt template for term search analysis."""
        template = """You are analyzing the results of a term search across files. Follow these guidelines:

Search Parameters:
- Term: {term}
- Directory: {directory}
- File Pattern: {file_pattern}

Search Results:
{results}

Analysis Tasks:
1. Analyze the context of each term occurrence
2. Identify patterns in term usage
3. Note any potential issues or inconsistencies
4. Consider the implications of term usage
5. Suggest improvements or alternatives

Consider:
1. Is the term used consistently?
2. Are there any potential naming conflicts?
3. Could the term usage be improved?
4. Are there any security or maintenance concerns?
5. Should any occurrences be refactored?"""
        return BasicPromptTemplate(template)
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        term = args["term"]
        directory = args.get("directory", ".")
        file_pattern = args.get("file_pattern", "*")
        
        try:
            import glob
            matches = []
            for filepath in glob.glob(os.path.join(directory, file_pattern), recursive=True):
                if os.path.isfile(filepath):
                    with open(filepath, 'r') as f:
                        for i, line in enumerate(f, 1):
                            if term in line:
                                matches.append(f"{filepath}:{i}: {line.strip()}")
            
            search_info = {
                "term": term,
                "directory": directory,
                "file_pattern": file_pattern,
                "results": "\n".join(matches)
            }
            
            return {
                "status": "success",
                "matches": matches,
                "prompt": self.get_formatted_prompt(search_info)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

class ExecDockerCommand(Command):
    """Execute a Docker command."""
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return isinstance(args.get("command"), str)
    
    def get_args(self) -> Dict[str, str]:
        return {
            "command": "Docker command to execute",
            "args": "Additional arguments (optional)"
        }
    
    def get_prompt_template(self) -> Optional[BasicPromptTemplate]:
        """Get prompt template for Docker command execution."""
        template = """You are preparing to execute a Docker command. Follow these guidelines:

Command Information:
- Base Command: {command}
- Arguments: {args}
- Context: {context}

Environment Analysis:
1. Container State: {container_state}
2. Network Configuration: {network_config}
3. Volume Mounts: {volume_mounts}
4. Resource Limits: {resource_limits}

Security Considerations:
- Privilege Level: {privilege_level}
- Port Exposures: {port_exposures}
- Volume Access: {volume_access}
- Network Access: {network_access}

Execution Guidelines:
1. Verify command safety and permissions
2. Check resource requirements
3. Validate network and volume configurations
4. Consider impact on other containers
5. Plan for proper error handling

Consider:
1. Is this command safe to execute?
2. Are resource requirements appropriate?
3. Are security configurations correct?
4. Is error handling adequate?
5. Are there potential side effects?"""
        return BasicPromptTemplate(template)
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        command = args["command"]
        extra_args = args.get("args", [])
        
        try:
            import subprocess
            cmd = ["docker", command]
            if extra_args:
                if isinstance(extra_args, str):
                    cmd.extend(extra_args.split())
                else:
                    cmd.extend(extra_args)
            
            # Get container and environment info for prompt
            env_info = {
                "command": command,
                "args": extra_args,
                "context": self._get_docker_context(),
                "container_state": self._get_container_state(),
                "network_config": self._get_network_config(),
                "volume_mounts": self._get_volume_mounts(),
                "resource_limits": self._get_resource_limits(),
                "privilege_level": self._get_privilege_level(),
                "port_exposures": self._get_port_exposures(),
                "volume_access": self._get_volume_access(),
                "network_access": self._get_network_access()
            }
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": result.stdout,
                "error": result.stderr,
                "prompt": self.get_formatted_prompt(env_info)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _get_docker_context(self) -> str:
        """Get current Docker context."""
        try:
            result = subprocess.run(["docker", "context", "show"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_container_state(self) -> str:
        """Get container state information."""
        try:
            result = subprocess.run(["docker", "ps", "-a"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_network_config(self) -> str:
        """Get network configuration."""
        try:
            result = subprocess.run(["docker", "network", "ls"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_volume_mounts(self) -> str:
        """Get volume mount information."""
        try:
            result = subprocess.run(["docker", "volume", "ls"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_resource_limits(self) -> str:
        """Get resource limit information."""
        try:
            result = subprocess.run(["docker", "info"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_privilege_level(self) -> str:
        """Get privilege level information."""
        return "standard"  # Default to standard privileges
    
    def _get_port_exposures(self) -> str:
        """Get port exposure information."""
        try:
            result = subprocess.run(["docker", "ps", "--format", "{{.Ports}}"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_volume_access(self) -> str:
        """Get volume access information."""
        try:
            result = subprocess.run(["docker", "volume", "inspect"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_network_access(self) -> str:
        """Get network access information."""
        try:
            result = subprocess.run(["docker", "network", "inspect", "bridge"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"

class GitStashCommand(Command):
    """Stash current changes."""
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return True  # No required args
    
    def get_args(self) -> Optional[Dict[str, str]]:
        return None
    
    def get_prompt_template(self) -> Optional[BasicPromptTemplate]:
        """Get prompt template for Git stash operations."""
        template = """You are preparing to stash Git changes. Follow these guidelines:

Repository State:
- Current Branch: {current_branch}
- Modified Files: {modified_files}
- Staged Changes: {staged_changes}
- Untracked Files: {untracked_files}

Stash Analysis:
1. Changes to be Stashed
2. Impact on Working Directory
3. Potential Conflicts
4. Recovery Options

Operation Guidelines:
1. Verify changes to be stashed
2. Check for partial stash needs
3. Consider stash message
4. Plan for later retrieval
5. Prepare for conflicts

Consider:
1. Should all changes be stashed?
2. Is a stash message needed?
3. Are there sensitive files to exclude?
4. Is the working directory clean?
5. Are there potential merge conflicts?"""
        return BasicPromptTemplate(template)
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        try:
            import subprocess
            
            # Get repository state for prompt
            repo_info = {
                "current_branch": self._get_current_branch(),
                "modified_files": self._get_modified_files(),
                "staged_changes": self._get_staged_changes(),
                "untracked_files": self._get_untracked_files()
            }
            
            result = subprocess.run(["git", "stash"], capture_output=True, text=True)
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": result.stdout,
                "error": result.stderr,
                "prompt": self.get_formatted_prompt(repo_info)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _get_current_branch(self) -> str:
        """Get current Git branch."""
        try:
            result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_modified_files(self) -> str:
        """Get list of modified files."""
        try:
            result = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_staged_changes(self) -> str:
        """Get list of staged changes."""
        try:
            result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_untracked_files(self) -> str:
        """Get list of untracked files."""
        try:
            result = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"

class GitCommitCommand(Command):
    """Commit current changes."""
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return isinstance(args.get("message"), str)
    
    def get_args(self) -> Dict[str, str]:
        return {
            "message": "Commit message"
        }
    
    def get_prompt_template(self) -> Optional[BasicPromptTemplate]:
        """Get prompt template for Git commit operations."""
        template = """You are preparing to commit changes to Git. Follow these guidelines:

Repository State:
- Current Branch: {current_branch}
- Modified Files: {modified_files}
- Staged Changes: {staged_changes}
- Untracked Files: {untracked_files}

Commit Analysis:
1. Changes to be Committed
2. Commit Message Format
3. Related Issues/Tasks
4. Breaking Changes
5. Documentation Updates

Message Guidelines:
1. Use conventional commit format
2. Include scope if applicable
3. Provide clear description
4. Reference related issues
5. Note breaking changes

Consider:
1. Is the commit message clear and descriptive?
2. Are all necessary changes included?
3. Should this be multiple commits?
4. Are tests and docs updated?
5. Are there breaking changes?"""
        return BasicPromptTemplate(template)
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        message = args["message"]
        
        try:
            import subprocess
            
            # Get repository state for prompt
            repo_info = {
                "current_branch": self._get_current_branch(),
                "modified_files": self._get_modified_files(),
                "staged_changes": self._get_staged_changes(),
                "untracked_files": self._get_untracked_files()
            }
            
            result = subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True)
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": result.stdout,
                "error": result.stderr,
                "prompt": self.get_formatted_prompt(repo_info)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _get_current_branch(self) -> str:
        """Get current Git branch."""
        try:
            result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_modified_files(self) -> str:
        """Get list of modified files."""
        try:
            result = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_staged_changes(self) -> str:
        """Get list of staged changes."""
        try:
            result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_untracked_files(self) -> str:
        """Get list of untracked files."""
        try:
            result = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"

class GitSwitchBranchCommand(Command):
    """Switch to or create a git branch."""
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return isinstance(args.get("branch"), str)
    
    def get_args(self) -> Dict[str, str]:
        return {
            "branch": "Branch name",
            "create_if_needed": "Create branch if it doesn't exist (optional, defaults to True)"
        }
    
    def get_prompt_template(self) -> Optional[BasicPromptTemplate]:
        """Get prompt template for Git branch switching."""
        template = """You are preparing to switch Git branches. Follow these guidelines:

Branch Information:
- Target Branch: {branch}
- Current Branch: {current_branch}
- Create If Needed: {create_if_needed}

Repository State:
- Modified Files: {modified_files}
- Staged Changes: {staged_changes}
- Untracked Files: {untracked_files}

Switch Analysis:
1. Current Branch State
2. Target Branch Status
3. Potential Conflicts
4. Required Actions
5. Recovery Options

Operation Guidelines:
1. Verify working directory state
2. Check for uncommitted changes
3. Consider stashing changes
4. Plan conflict resolution
5. Prepare for branch creation

Consider:
1. Is the working directory clean?
2. Are there uncommitted changes?
3. Will there be merge conflicts?
4. Should changes be stashed first?
5. Is branch creation needed?"""
        return BasicPromptTemplate(template)
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        branch = args["branch"]
        create = args.get("create_if_needed", True)
        
        try:
            import subprocess
            
            # Get repository state for prompt
            repo_info = {
                "branch": branch,
                "current_branch": self._get_current_branch(),
                "create_if_needed": create,
                "modified_files": self._get_modified_files(),
                "staged_changes": self._get_staged_changes(),
                "untracked_files": self._get_untracked_files()
            }
            
            cmd = ["git", "checkout"]
            if create:
                cmd.append("-B")
            cmd.append(branch)
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return {
                "status": "success" if result.returncode == 0 else "error",
                "output": result.stdout,
                "error": result.stderr,
                "prompt": self.get_formatted_prompt(repo_info)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _get_current_branch(self) -> str:
        """Get current Git branch."""
        try:
            result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_modified_files(self) -> str:
        """Get list of modified files."""
        try:
            result = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_staged_changes(self) -> str:
        """Get list of staged changes."""
        try:
            result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_untracked_files(self) -> str:
        """Get list of untracked files."""
        try:
            result = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"

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

# Register commands
from .registry import CommandRegistry
CommandRegistry.register("read_file", ReadFileCommand)
CommandRegistry.register("lookup_files", LookupFilesCommand)
CommandRegistry.register("lookup_term", LookupTermCommand)
CommandRegistry.register("exec_docker", ExecDockerCommand)
CommandRegistry.register("git_stash", GitStashCommand)
CommandRegistry.register("git_commit_current", GitCommitCommand)
CommandRegistry.register("git_switch_branch", GitSwitchBranchCommand)

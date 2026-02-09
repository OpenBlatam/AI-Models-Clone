#!/usr/bin/env python3
"""
Utility functions for deployment scripts
"""

import logging
import subprocess
from typing import Tuple, Optional
from pathlib import Path


logger = logging.getLogger(__name__)


def run_command(
    command: list[str],
    cwd: Optional[str] = None,
    timeout: Optional[int] = None,
    env: Optional[dict] = None,
    capture_output: bool = True
) -> Tuple[bool, str, str]:
    """
    Run a shell command and return success status and output
    
    Args:
        command: Command to run as list of strings
        cwd: Working directory
        timeout: Command timeout in seconds
        env: Environment variables
        capture_output: Whether to capture stdout/stderr
        
    Returns:
        Tuple of (success: bool, stdout: str, stderr: str)
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            timeout=timeout,
            env=env,
            capture_output=capture_output,
            text=True
        )
        
        return (
            result.returncode == 0,
            result.stdout if capture_output else '',
            result.stderr if capture_output else ''
        )
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out: {' '.join(command)}")
        return False, '', 'Command timed out'
    except Exception as e:
        logger.error(f"Error running command: {e}")
        return False, '', str(e)


def ensure_directory(path: str) -> bool:
    """Ensure directory exists, create if it doesn't"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False


def ensure_file_executable(file_path: str) -> bool:
    """Ensure file exists and is executable"""
    path = Path(file_path)
    if not path.exists():
        logger.error(f"File does not exist: {file_path}")
        return False
    
    # Make executable
    path.chmod(0o755)
    return True


def get_git_commit_hash(repo_path: str, branch: str = 'HEAD') -> Optional[str]:
    """Get git commit hash for a branch"""
    success, stdout, _ = run_command(
        ['git', 'rev-parse', branch],
        cwd=repo_path
    )
    
    if success:
        return stdout.strip()
    return None


def check_git_updates(repo_path: str, branch: str = 'main') -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Check if there are updates available in the remote repository
    
    Returns:
        Tuple of (has_updates: bool, local_commit: str, remote_commit: str)
    """
    # Fetch latest changes
    run_command(['git', 'fetch', 'origin', branch], cwd=repo_path)
    
    # Get local and remote commit hashes
    local_commit = get_git_commit_hash(repo_path, 'HEAD')
    remote_commit = get_git_commit_hash(repo_path, f'origin/{branch}')
    
    if not local_commit or not remote_commit:
        return False, local_commit, remote_commit
    
    has_updates = local_commit != remote_commit
    return has_updates, local_commit, remote_commit

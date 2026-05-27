import os
from pathlib import Path

PROTECTED_PATHS = [
    Path.home() / ".ssh",
    Path.home() / ".gnupg",
    Path.home() / ".kube",
    Path.home() / ".aws",
    Path.home() / ".azure",
    Path.home() / ".gcp"
]

PROTECTED_FILENAMES = [
    ".env",
    "wallet.dat",
    "credentials.json",
    "config.json" # general cloud config
]

def canonicalize_path(target_path: str) -> Path:
    """Resolves symlinks and normalizes the path."""
    return Path(target_path).resolve()

def is_path_safe(target_path: str) -> bool:
    """
    Validates a target path against:
    - Path traversal (by canonicalizing)
    - Symlink escape (by resolving)
    - Protected directories and files
    """
    try:
        resolved_path = canonicalize_path(target_path)
    except Exception:
        # If it can't be resolved, it's unsafe or invalid
        return False

    # Check protected filenames
    if resolved_path.name in PROTECTED_FILENAMES:
        return False
        
    # Check if the path is inside any protected directory
    for protected in PROTECTED_PATHS:
        try:
            # If resolved_path is relative to a protected path, it's unsafe
            resolved_path.relative_to(protected)
            return False
        except ValueError:
            pass # Not relative to this protected path
            
        if resolved_path == protected:
            return False

    return True

def validate_operation(operation: dict) -> bool:
    """Validates entire operation including risk tier."""
    risk_tier = operation.get("risk_level", "safe")
    if risk_tier not in ["safe", "balanced", "aggressive"]:
        raise ValueError(f"Invalid risk tier: {risk_tier}")

    targets = operation.get("targets", [])
    for target in targets:
        path_to_check = None
        if isinstance(target, dict):
            path_to_check = target.get("path")
        elif isinstance(target, str):
            path_to_check = target
            
        if path_to_check:
            if not is_path_safe(path_to_check):
                raise PermissionError(f"Target path {path_to_check} is protected or unsafe.")
            
    return True


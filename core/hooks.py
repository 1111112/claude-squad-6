"""
Claude Squad 6 - Minimal Hooks Runner
Executes quality checks with auto-fix capabilities
"""
import asyncio
import subprocess
from typing import Dict, List, Any
from pathlib import Path

class HooksRunner:
    """Minimal hooks execution engine"""
    
    def __init__(self, config_path: str = "hooks.yaml"):
        self.config_path = config_path
        self.hooks = {
            "pre-commit": [
                {"cmd": "black --check .", "fix": "black .", "name": "Black formatter"},
                {"cmd": "ruff check .", "fix": "ruff check --fix .", "name": "Ruff linter"}
            ],
            "pre-push": [
                {"cmd": "pytest", "name": "Run tests"},
                {"cmd": "pytest --cov=. --cov-report=term-missing", "name": "Coverage check"}
            ]
        }
    
    async def run_hooks(self, hook_type: str) -> Dict[str, Any]:
        """Run hooks for given type with auto-fix"""
        if hook_type not in self.hooks:
            return {"success": True, "message": f"No hooks defined for {hook_type}"}
        
        results = {"success": True, "issues": [], "fixed": 0}
        
        for hook in self.hooks[hook_type]:
            try:
                # Run the check command
                result = subprocess.run(hook["cmd"], shell=True, capture_output=True, text=True)
                
                if result.returncode != 0:
                    # Try auto-fix if available
                    if "fix" in hook and hook_type == "pre-commit":
                        fix_result = subprocess.run(hook["fix"], shell=True, capture_output=True, text=True)
                        if fix_result.returncode == 0:
                            results["fixed"] += 1
                        else:
                            results["success"] = False
                            results["issues"].append(f"{hook['name']}: {result.stderr}")
                    else:
                        results["success"] = False
                        results["issues"].append(f"{hook['name']}: {result.stderr}")
                        
            except Exception as e:
                results["success"] = False
                results["issues"].append(f"{hook['name']}: {str(e)}")
        
        return results
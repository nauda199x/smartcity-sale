"""The only production build entry point; ordered and deterministic."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

for script in ("build_flat_public_routes.py", "build_project_profiles.py", "validate_project_profiles.py", "build_homepage.py", "validate_homepage.py", "build_static_sale_landings.py", "build_legacy_redirects.py", "apply_design_system.py"):
    subprocess.run([sys.executable, str(ROOT / "tools" / script)], cwd=ROOT, check=True)

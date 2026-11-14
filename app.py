"""
Root Entrypoint for EduCluster ML Dashboard
Delegates directly to educluster-ml/app.py
"""

import os
import sys
from pathlib import Path

# Add educluster-ml to sys.path
root_dir = Path(__file__).resolve().parent
educluster_dir = root_dir / "educluster-ml"
if str(educluster_dir) not in sys.path:
    sys.path.insert(0, str(educluster_dir))
if str(educluster_dir / "src") not in sys.path:
    sys.path.insert(0, str(educluster_dir / "src"))

# Execute the main dashboard
app_path = educluster_dir / "app.py"
with open(app_path, "r", encoding="utf-8") as f:
    code = compile(f.read(), str(app_path), "exec")
    exec(code, {"__name__": "__main__", "__file__": str(app_path)})


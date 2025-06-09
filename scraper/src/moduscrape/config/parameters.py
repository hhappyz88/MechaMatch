import os
from moduscrape.utils.paths import find_project_root

SAVE_ROOT = os.path.join("data", "downloads")
PROXY_TIMEOUT = 5
JOB_ROOT = os.path.join("data", "jobs")
SESSION_BASE_DIR = find_project_root() / "data"

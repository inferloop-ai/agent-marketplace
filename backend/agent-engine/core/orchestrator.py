# This request is for a shell or script operation, not Python code.
# To create all files in the `core` subdirectory as listed in your setup, use the following shell command:

import os

core_files = [
    "__init__.py",
    "agent_factory.py",
    "orchestrator.py",
    "executor.py",
    "registry.py",
]

core_dir = "backend/agent-engine/core"
os.makedirs(core_dir, exist_ok=True)
for fname in core_files:
    fpath = os.path.join(core_dir, fname)
    if not os.path.exists(fpath):
        with open(fpath, "w"):
            pass  # Creates an empty file

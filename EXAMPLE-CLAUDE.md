## How to code in this repository

We're building are using python for devepment, along with custom hooks that
enforce TDD principles and patterns, including a python wrapper and tool hook.
We are operating within a virtual environment and using pip for package mgmt.
You must source the venv before running the code or installing pip packages.
After compacting the conversation, you need to re-read this file. One of the
hooks will disallow git commits if there are files with no associated tests,
including `__init__.py`.

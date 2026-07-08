import asyncio
import os

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import subprocess
subprocess.run([os.path.join('.venv', 'Scripts', 'python.exe'), '-m', 'streamlit', 'run', 'src/ui/streamlit_app.py'])
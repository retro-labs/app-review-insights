import subprocess
import sys
import os
import asyncio

def main():
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    venv_python = os.path.join(project_dir, ".venv", "Scripts", "python.exe")
    
    if os.path.exists(venv_python):
        python_executable = venv_python
    else:
        python_executable = sys.executable
    
    subprocess.run([python_executable, "-m", "streamlit", "run", "src/ui/streamlit_app.py", "--server.port", "8501", "--server.headless", "true"])

if __name__ == "__main__":
    main()
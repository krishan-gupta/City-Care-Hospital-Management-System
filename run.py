"""
City Care Hospital Management System - Unified Runner
Double-click this file (run.py) or run `python run.py` in your terminal to start
both the FastAPI backend and React frontend simultaneously.
"""

import atexit
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import traceback
import webbrowser

# Ensure unbuffered / line-buffered stdout for real-time console feedback
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(line_buffering=True)
except Exception:
    pass

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

stop_event = threading.Event()
active_processes = []


def set_terminal_title(title: str):
    if sys.platform == "win32":
        try:
            os.system(f"title {title}")
        except Exception:
            pass


def is_port_in_use(port: int) -> bool:
    """Check if a TCP port is in use on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def free_ports(*ports):
    """Ensure ports 8000 and 5173 are freed if previously occupied."""
    if sys.platform != "win32":
        return
    for port in ports:
        if is_port_in_use(port):
            try:
                cmd = f'for /f "tokens=5" %a in (\'netstat -aon ^| findstr /r ":{port}[ ]"\' ) do taskkill /f /pid %a'
                subprocess.run(
                    cmd,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                pass


def kill_process_tree(proc: subprocess.Popen):
    """Safely terminate a process and its whole subtree."""
    if proc is None or proc.poll() is not None:
        return
    try:
        if sys.platform == "win32":
            subprocess.run(
                f"taskkill /F /T /PID {proc.pid}",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            proc.terminate()
            proc.wait(timeout=2)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def cleanup():
    """Cleanup all spawned servers on exit."""
    if stop_event.is_set() and not active_processes:
        return
    stop_event.set()
    print("\n[Shutdown] Stopping servers...", flush=True)
    for proc in active_processes:
        kill_process_tree(proc)
    free_ports(8000, 5173)
    print("[Shutdown] All services stopped successfully.", flush=True)


atexit.register(cleanup)


def stream_output(proc: subprocess.Popen, prefix: str):
    """Stream process stdout line-by-line with prefix."""
    try:
        for line in iter(proc.stdout.readline, ""):
            if not line:
                break
            line_str = line.rstrip()
            if line_str:
                print(f"[{prefix}] {line_str}", flush=True)
    except Exception:
        pass
    finally:
        if proc.stdout:
            try:
                proc.stdout.close()
            except Exception:
                pass


def find_backend_python() -> str:
    """Find the best python executable to run backend (preferring venv)."""
    venv_win = ROOT_DIR / "venv" / "Scripts" / "python.exe"
    venv_unix = ROOT_DIR / "venv" / "bin" / "python"
    if venv_win.exists():
        return str(venv_win)
    if venv_unix.exists():
        return str(venv_unix)
    return sys.executable


def find_npm() -> str:
    """Find npm executable on system path."""
    npm_path = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm_path:
        raise FileNotFoundError(
            "Node.js / npm was not found on your system PATH.\n"
            "Please install Node.js (https://nodejs.org) to run the frontend."
        )
    return npm_path


def open_browser_delayed(url: str, delay: int = 3):
    """Open web browser after a short delay so servers can bind."""
    time.sleep(delay)
    if not stop_event.is_set():
        print(f"\n[Browser] Opening {url} ...\n", flush=True)
        try:
            webbrowser.open(url)
        except Exception:
            pass


def listen_for_user_exit():
    """Listen for Enter key in interactive console to trigger graceful shutdown."""
    try:
        if sys.stdin and sys.stdin.isatty():
            input()
            stop_event.set()
    except Exception:
        pass


def main():
    set_terminal_title("City Care Hospital Management System")

    print("=" * 65)
    print("      City Care Hospital Management System - Launcher")
    print("=" * 65)
    print()

    # 1. Validation
    if not BACKEND_DIR.exists():
        print(f"[ERROR] Backend directory not found: {BACKEND_DIR}", flush=True)
        input("\nPress Enter to exit...")
        sys.exit(1)

    if not FRONTEND_DIR.exists():
        print(f"[ERROR] Frontend directory not found: {FRONTEND_DIR}", flush=True)
        input("\nPress Enter to exit...")
        sys.exit(1)

    # 2. Check & free ports
    print("[1/4] Checking ports 8000 & 5173...", flush=True)
    free_ports(8000, 5173)

    # 3. Detect Python and npm
    backend_python = find_backend_python()
    npm_bin = find_npm()

    print(f"[2/4] Using Backend Python: {backend_python}", flush=True)
    print(f"      Using Node/npm:       {npm_bin}", flush=True)

    # Check frontend dependencies
    if not (FRONTEND_DIR / "node_modules").exists():
        print("[INFO] Installing frontend dependencies (npm install)...", flush=True)
        subprocess.run([npm_bin, "install"], cwd=FRONTEND_DIR, check=True)

    # 4. Start Backend (FastAPI / Uvicorn)
    print("[3/4] Starting Backend (FastAPI on port 8000)...", flush=True)
    backend_env = os.environ.copy()
    backend_env["PYTHONUNBUFFERED"] = "1"

    backend_cmd = [
        backend_python,
        "-m",
        "uvicorn",
        "main:app",
        "--reload",
        "--port",
        "8000",
    ]
    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=backend_env,
    )
    active_processes.append(backend_proc)

    # 5. Start Frontend (React Vite)
    print("[4/4] Starting Frontend (React Vite on port 5173)...", flush=True)
    frontend_cmd = [npm_bin, "run", "dev"]
    frontend_proc = subprocess.Popen(
        frontend_cmd,
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        shell=True,
    )
    active_processes.append(frontend_proc)

    # Start output streaming threads
    t_backend = threading.Thread(
        target=stream_output, args=(backend_proc, "Backend"), daemon=True
    )
    t_frontend = threading.Thread(
        target=stream_output, args=(frontend_proc, "Frontend"), daemon=True
    )
    t_backend.start()
    t_frontend.start()

    # Launch browser in separate thread
    t_browser = threading.Thread(
        target=open_browser_delayed, args=("http://localhost:5173", 3), daemon=True
    )
    t_browser.start()

    print("\n" + "=" * 65)
    print("  City Care Hospital Management System is LIVE!")
    print("=" * 65)
    print("  * Frontend Web App:   http://localhost:5173")
    print("  * Backend API:        http://localhost:8000")
    print("  * Swagger API Docs:   http://localhost:8000/docs")
    print("=" * 65)
    print("  Press Enter or Ctrl+C at any time to STOP all servers.")
    print("=" * 65 + "\n", flush=True)

    # Start listener for Enter key
    t_input = threading.Thread(target=listen_for_user_exit, daemon=True)
    t_input.start()

    # Main wait loop
    try:
        while not stop_event.is_set():
            if backend_proc.poll() is not None:
                print("\n[WARNING] Backend process exited unexpectedly.", flush=True)
                break
            if frontend_proc.poll() is not None:
                print("\n[WARNING] Frontend process exited unexpectedly.", flush=True)
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[Interrupted by user]", flush=True)
    finally:
        cleanup()


if __name__ == "__main__":
    def handle_signal(sig, frame):
        stop_event.set()

    signal.signal(signal.SIGINT, handle_signal)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, handle_signal)

    try:
        main()
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}", flush=True)
        traceback.print_exc()
        input("\nPress Enter to exit...")

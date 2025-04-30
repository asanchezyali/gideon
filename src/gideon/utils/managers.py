import os
import platform
import signal
import subprocess
from pathlib import Path
from gideon.utils.bcolors import print_info


def open_file(file):
    print_info(f"Opening file: {file}")
    if platform.system() == "Linux":
        cmd = ["xdg-open", file]
    elif platform.system() == "Darwin":
        cmd = ["open", file]
    elif platform.system() == "Windows":
        cmd = ["start", file]
    else:
        raise OSError("Unsupported operating system")

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        shell=True if platform.system() == "Windows" else False,
    )
    return process


def close_file(process):
    if platform.system() in ("Linux", "Darwin"):
        # os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        os.kill(process.pid, signal.SIGTERM)
    elif platform.system() == "Windows":
        process.terminate()
    else:
        raise OSError("Unsupported operating system")

import importlib
import os
import subprocess
import sys


def run(command, desc=None, errdesc=None, custom_env=None):
    if desc is not None:
        print(desc)

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        env=os.environ if custom_env is None else custom_env,
    )

    if result.returncode != 0:
        message = f"""{errdesc or 'Error running command'}.
Command: {command}
Error code: {result.returncode}
stdout: {result.stdout.decode(encoding="utf8", errors="ignore") if len(result.stdout)>0 else '<empty>'}
stderr: {result.stderr.decode(encoding="utf8", errors="ignore") if len(result.stderr)>0 else '<empty>'}
"""
        raise RuntimeError(message)

    return result.stdout.decode(encoding="utf8", errors="ignore")


def is_installed(package):
    try:
        spec = importlib.util.find_spec(package)
    except ModuleNotFoundError:
        return False

    return spec is not None


def run_pip_from_git(url=None, desc=None, args=""):
    return run(
        f"python -m pip install git+{url} {args}",
        desc=f"Installing {desc}",
        errdesc=f"Couldn't install {desc}",
    )


def run_pip(pkg, desc=None, args=""):
    python = sys.executable
    return run(
        f'"{python}" -m pip install {pkg} {args}',
        desc=f"Installing {desc}",
        errdesc=f"Couldn't install {desc}",
    )

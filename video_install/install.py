
import os
import sys
import platform
from subprocess import STDOUT, check_call, check_output, CalledProcessError
import argparse

THISDIR = os.path.dirname(os.path.realpath(__file__))
THIS_VP_BASE = os.path.abspath(os.path.join(THISDIR, ".."))
VIDEO_INSTALL_DIR = "video_install"

PYTHON_BIN = "python" if platform.system().lower() == "windows" else "python3"

print(THISDIR, "\n", THIS_VP_BASE)

def pip_install(args, pip_config=None, get_output=False, cwd=None):
    cmd = f"{PYTHON_BIN} -m pip install {args}"
    env = os.environ.copy()
    if pip_config is not None:
        env["PIP_CONFIG_FILE"] = pip_config

    try:
        if get_output:
            return check_output(cmd, shell=True, env=env, stderr=STDOUT, cwd=cwd)
        else:
            check_call(cmd, shell=True, env=env, cwd=cwd)
    except CalledProcessError:
        args = f"{args} --no-cache-dir"
        if get_output:
            return check_output(cmd, shell=True, env=env, stderr=STDOUT, cwd=cwd)
        else:
            check_call(cmd, shell=True, env=env, cwd=cwd)


try:
    import virtualenv
except ModuleNotFoundError:
    pip_install('virtualenv')
    import virtualenv


def activate_path(venv_dir):
    scripts_dir = "bin"
    if "windows" == platform.system().lower():
        scripts_dir = "Scripts"
    else:
        raise Exception("Suported only on Windows OS")

    return os.path.join(venv_dir, scripts_dir, "activate_this.py")

def setup_venv(venv_path):
    # check python version >= python 3.9
    if sys.version_info.major != 3 and sys.version_info.minor < 9:
        raise Exception("Called python must be at least python 3.9")

    created_venv = False
    
    venv_dir = os.path.abspath(os.path.expanduser(venv_path))
    print("venv:", venv_path, venv_dir)
    
    activate_file = activate_path(venv_dir)
    
    if not os.path.exists(venv_dir) or not os.path.exists(activate_file):
        print(f">>> Creating virtual environment in {venv_dir}")
        virtualenv.cli_run([venv_dir])
        created_venv = True

    print(f">>> Activating virtual environment in {venv_dir}")
    with open(activate_file, "rb") as pfile:
        exec(pfile.read(), {"__file__": activate_file})

    if created_venv:
        print(">>> Ensuring virtual environment is installed in new virtualenv")
        pip_install("virtualenv")

    print(">>> Ensuring pip set to proper version in  virtualenv")
    # --upgrade flag needed on windows to support pip upgrade in place
    # see https://github.com/pypa/pip/issues/1299
    #pip_install("--upgrade pip==22.3.1")

    print(">>> Ensuring setuptools is updated in  virtualenv")
    pip_install("-U setuptools==65.7.0")


def get_src_package_dirs(workspace):
    lib_dir = os.path.join(workspace, "src")
    thedir = os.path.abspath(lib_dir)
    dirs = []
    for name in os.listdir(thedir):
        sub_dir = os.path.join(thedir, name)
        if os.path.isdir(sub_dir):
            if "setup.py" in os.listdir(sub_dir):  # ensure its actually a subpackage
                print(f"Found package: {name}")
                dirs.append(sub_dir)
    return dirs

def install_src_packages(workspace):
    print("Checking src folder")
    src_dirs = get_src_package_dirs(workspace)
    # perform pip installs
    for libdir in src_dirs:
        pip_config = os.path.join(workspace, VIDEO_INSTALL_DIR)
        print(f"Installing {libdir}")
        output = pip_install("-e .", pip_config=pip_config, cwd=libdir, get_output=True)
        print(f'Install output: {output.decode("UTF-8")}')
        print(f"Done installing {libdir}")
        

def install_workspace(workspace):
    install_dir = os.path.join(workspace, VIDEO_INSTALL_DIR)
    
    print(">>> Installing external requirements")
    pip_install("-r " + os.path.join(install_dir, "ext-requirements.txt"))

    print(f">>> Installing code source packages from {workspace}")
    install_src_packages(workspace)


def main():
    argp = argparse.ArgumentParser(
        description="Creates/uses a virtualenv for Video Projection and install dev packages"
    )
    argp.add_argument(
        "--venv",
        help="Path to virtualenv to install against, will create if nonexistent",
        default=os.environ.get("VIRTUAL_ENV")
    )
    argp.add_argument(
        "--workspace", help="Path to orc3 source workspace", default=THIS_VP_BASE
    )
    
    args = argp.parse_args()

    if args.venv:
        # activate virtual environment
        setup_venv(args.venv)
    else:
        raise Exception("No virtual environment provided")

    install_workspace(args.workspace)

if __name__ == "__main__":
    main()
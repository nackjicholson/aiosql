import shutil
import importlib


def has_cmd(cmd):
    return shutil.which(cmd) is not None


def has_pkg(pkg):
    try:
        importlib.import_module(pkg)
        return True
    except ModuleNotFoundError:
        return False

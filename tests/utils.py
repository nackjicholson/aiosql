import shutil
import importlib
import logging

log = logging.getLogger("pytest-aiosql")
logging.basicConfig(level=logging.INFO)


def has_cmd(cmd):
    return shutil.which(cmd) is not None


def has_pkg(pkg):
    try:
        importlib.import_module(pkg)
        return True
    except ModuleNotFoundError:
        return False


def has_service(host="localhost", port=22, retry=1):
    import socket
    import time

    while retry > 0:
        retry -= 1
        try:
            tcp_ip = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_ip.settimeout(1)
            res = tcp_ip.connect_ex((host, port))
            if res == 0:
                return True
            if retry > 0:
                time.sleep(3)
        except Exception as e:
            log.info(f"connection to {(host, port)} failed: {e}")
            if retry > 0:
                time.sleep(3)
        finally:
            tcp_ip.close()
    return False

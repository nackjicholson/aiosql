import shutil
import importlib
import logging
import time
import contextlib
import asyncio

log = logging.getLogger("pytest-aiosql")
logging.basicConfig(level=logging.INFO)

def has_cmd(cmd):
    return shutil.which(cmd) is not None

def has_pkg(pkg):
    """Tell whether a module is available."""
    try:
        importlib.import_module(pkg)
        return True
    except ModuleNotFoundError:
        return False

def has_service(host="localhost", port=22, retry=1):
    """Tell whether a service (host port) is available."""
    import socket

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

@contextlib.contextmanager
def db_connect(db, tries, *args, **kwargs):
    """Return an auto-closing database connection, possibly with several attempts."""
    fails, done = 0, False
    while not done and fails < tries:
        try:
            with db.connect(*args, **kwargs) as conn:
                done = True
                yield conn
        except Exception as e:
            fails += 1
            log.warning(f"{db.__name__} connection failed ({fails}): {e}")
            time.sleep(1.0)
    if not done:
        log.error(f"failed to connect after {tries} attempts")

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def run_async(awaitable):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(awaitable)

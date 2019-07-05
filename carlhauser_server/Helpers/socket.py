#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys
import subprocess
import redis
import time

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))


# ==================== ------ PATHS ------- ====================

class Socket:

    def __init__(self, socket_path: pathlib.Path, script_folder_path: pathlib.Path):
        # Create a socket handler which know scripts path and socket path for a specific database

        # STD attributes
        self.logger = logging.getLogger(__name__)

        # Specific attributes
        self.socket_path = socket_path
        self.script_folder_path = script_folder_path

        # Run/Flush/Stop scripts
        self.launch_script_path = script_folder_path / "run.sh"
        self.shutdown_script_path = script_folder_path / "shutdown.sh"
        self.flush_script_path = script_folder_path / "flush.sh"

    def launch(self):
        # Launch the database behind the given socket
        if not self.is_running():
            self.run_script(self.launch_script_path)

    def shutdown(self):
        # Stop the database behind the given socket
        self.run_script(self.shutdown_script_path)

    def flush(self):
        # Flush the database behind the given socket
        self.run_script(self.flush_script_path)

    def get_access(self, decode_responses=True):
        # Get an access to the redis database behind the given socket
        return redis.Redis(unix_socket_path=str(self.socket_path), decode_responses=decode_responses)

    def is_running(self) -> bool:
        # Check if the database is running behind the given socket

        try:
            self.logger.debug(f"Checking if redis db is running on {self.socket_path}")
            r = redis.Redis(unix_socket_path=str(self.socket_path))
            if r.ping():
                self.logger.debug(f"{self.socket_path} is running")
                return True
        except Exception as e:
            self.logger.debug(f"{self.socket_path} is NOT running : {e}")
            # logger = logging.getLogger(__name__)
            # logger.error(f"PING got no answer. Invalid socket. {e}")
            return False

    def wait_until_running(self, timeout: int = 60) -> bool:
        # Wait until the database behind the given socket is launched (= answer to a ping)
        # Put timeout -1 if you don't want to function to timeout

        start = time.time()

        while not self.is_running():
            time.sleep(5)
            if timeout != -1 and abs(time.time() - start) > timeout:
                self.logger.warning("Waiting for Redis database to run has timeout-ed.")
                return False

        return True

    def wait_until_stopped(self, timeout: int = 60) -> bool:
        # Wait until the database is stopped (= does not answer to a ping)
        # Put timeout -1 if you don't want to function to timeout

        start = time.time()

        while self.is_running():
            time.sleep(5)
            if timeout != -1 and abs(time.time() - start) > timeout:
                self.logger.warning("Waiting for Redis database to stop has timeout-ed.")
                return False

        return True

    def prevent_workers_stop(self):
        # Put "Halt" key in database
        redis_access = self.get_access()
        try :
            redis_access.delete("halt")
        except Exception as e :
            self.logger.error(f"Can't remove stop signal to worker via {self.socket_path.name}, as database is not accessible : {e}")

    def stop_workers(self):
        # Put "Halt" key in database
        redis_access = self.get_access()
        try :
            redis_access.set("halt", "true")
        except Exception as e :
            self.logger.error(f"Can't send stop signal to worker via {self.socket_path.name}, as database is not accessible : {e}")

    def run_script(self, script_path: pathlib.Path):
        # Run a given script file (bash)
        self.logger.debug(f"Running script {script_path} at {script_path.parent}")
        subprocess.Popen([str(script_path)], cwd=script_path.parent)
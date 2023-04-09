import sys
import os
import time
import inspect


# Software informations
class serverVersion:
    version = "5.00"
    codename = "Spring Rain"

class softwareInfo:
    server = serverVersion

info = softwareInfo()


# Config
class baseConfig:
    debug_mode = os.getenv("FREA_DEBUG_MODE", "false")

class redisConfig:
    host = os.getenv("REDIS_HOST", "127.0.0.1")
    port = os.getenv("REDIS_PORT", "6379")

class postgresConfig:
    host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    port = os.getenv("POSTGRES_PORT", "5432")

class Config:
    base = baseConfig
    redis = redisConfig
    db = postgresConfig

config = Config()


class log:
    def __init__(self):
        self.target_file = os.path.splitext(os.path.basename(inspect.stack()[1].filename))[0]

        if config.base.debug_mode == "true":
            self._debug_mode = True
        else:
            self._debug_mode = False

    def info(self, message):
        sys.stdout.write(f"[{self.target_file}]\033[32;1m [INFO]\033[0m " + str(message) + "\n")

    def warn(self, message):
        sys.stdout.write(f"[{self.target_file}]\033[33;1m [WARNING]\033[0m " + str(message) + "\n")

    def dbg(self, message):
        if self._debug_mode:
            sys.stdout.write(f"[{self.target_file}]\033[90;1m [DEBUG] @{time.time()}\033[0m " + str(message) + "\n")

    def error(self, message):
        sys.stderr.write(f"[{self.target_file}]\033[31;1m [ERROR] " + str(message) + "\033[0m\n")

    def fatal_error(self, message):
        sys.stderr.write("\n\033[31;1m=!=========FATAL ERROR=========!=\n")
        sys.stderr.write(f"\033[31m[{self.target_file}] {message}\n")
        sys.stderr.write("\033[31;1m=================================\033[0m\n")

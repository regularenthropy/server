import sys
import os
import time
import inspect

class BaseConfig:
    debug_mode = os.getenv("FREA_DEBUG_MODE", "false")

class RedisConfig:
    host = os.getenv("REDIS_HOST", "127.0.0.1")
    port = os.getenv("REDIS_PORT", "6379")

class PostgresConfig:
    host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    port = os.getenv("POSTGRES_PORT", "5432")

config = {
    "system": BaseConfig,
    "redis": RedisConfig,
    "db": PostgresConfig
}


class log:
    def __init__(self):
        self.target_file = os.path.splitext(os.path.basename(inspect.stack()[1].filename))[0]

    def info(self, message):
        sys.stdout.write(f"[{self.target_file}]\033[32;1m [INFO]\033[0m " + str(message) + "\n")

    def warn(self, message):
        sys.stdout.write(f"[{self.target_file}]\033[33;1m [WARNING]\033[0m " + str(message) + "\n")

    def dbg(self, message):
        if os.environ['FREA_DEBUG_MODE'] == "true":
            sys.stdout.write(f"[{self.target_file}]\033[90;1m [DEBUG] @{time.time()}\033[0m " + str(message) + "\n")

    def error(self, message):
        sys.stderr.write(f"[{self.target_file}]\033[31;1m [ERROR] " + str(message) + "\033[0m\n")

    def fatal_error(self, message):
        sys.stderr.write("\n\033[31;1m=!=========FATAL ERROR=========!=\n")
        sys.stderr.write(f"\033[31m[{self.target_file}] {message}\n")
        sys.stderr.write("\033[31;1m=================================\033[0m\n")

import sys
import time

def info(message):
    sys.stdout.write("\033[32m[INFO]\033[0m " + str(message) + "\n")

def dbg(message):
    sys.stdout.write(f"\033[90m[DEBUG] @{time.time()}\033[0m " + str(message) + "\n")

def error(message):
    sys.stderr.write("\033[31m" + str(message) + "\033[0m\n")

def fetal_error(message):
    error("=!=========FETAL ERROR=========!=")
    error(message)
    error("=================================")

# SPDX-License-Identifier: AGPL-3.0-or-later

'''
Frea Search is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Frea Search is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with Frea Search. If not, see < http://www.gnu.org/licenses/ >.

(C) 2022  Frea Search, Ablaze
                   nexryai <gnomer@tuta.io>
'''


import sys
import os
import time
import inspect

def info(message):
    target_file = os.path.splitext(os.path.basename(inspect.stack()[1].filename))[0]
    sys.stdout.write(f"[{target_file}]\033[32;1m [INFO]\033[0m " + str(message) + "\n")

def warn(message):
    target_file = os.path.splitext(os.path.basename(inspect.stack()[1].filename))[0]
    sys.stdout.write(f"[{target_file}]\033[33;1m [WARNING]\033[0m " + str(message) + "\n")

def dbg(message):
    if os.environ['FREA_DEBUG_MODE'] == "true":
        target_file = os.path.splitext(os.path.basename(inspect.stack()[1].filename))[0]
        sys.stdout.write(f"[{target_file}]\033[90;1m [DEBUG] @{time.time()}\033[0m " + str(message) + "\n")

def error(message):
    target_file = os.path.splitext(os.path.basename(inspect.stack()[1].filename))[0]
    sys.stderr.write(f"[{target_file}]\033[31;1m [ERROR] " + str(message) + "\033[0m\n")

def fatal_error(message):
    target_file = os.path.splitext(os.path.basename(inspect.stack()[1].filename))[0]
    sys.stderr.write("\n\033[31;1m=!=========FATAL ERROR=========!=\n")
    sys.stderr.write(f"\033[31m[{target_file}] {message}\n")
    sys.stderr.write("\033[31;1m=================================\033[0m\n")

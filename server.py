#!/usr/bin/env python3
#
# This file is part of rainfall (https://github.com/mrworf/rainfall).
#
# rainfall is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rainfall is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rainfall.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import logging
import argparse
import sys

from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.exceptions import HTTPException

from modules.rainfall import rainfall

if __name__ != '__main__':
  print('ERROR: This should not be imported')
  sys.exit(255)

parser = argparse.ArgumentParser(description="Rainfall - A RaspberryPi based sprinkler controller", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--port', default=7770, type=int, help="Port to listen on")
parser.add_argument('--listen', default="0.0.0.0", help="Address to listen on")
parser.add_argument('--debug', action='store_true', default=False, help='Enable loads more logging')
cmdline = parser.parse_args()

if cmdline.debug:
  logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
else:
  logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

""" Disable some logging by-default """
logging.getLogger("Flask-Cors").setLevel(logging.ERROR)
logging.getLogger("werkzeug").setLevel(logging.ERROR)

""" Initialize the REST server """
app = Flask(__name__, static_url_path='/html/')
#cors = CORS(app) # Needed to make us CORS compatible

rf = rainfall()
rf.load()
rf.start()
app.run()

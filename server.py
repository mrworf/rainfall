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
import json

from flask import Flask, request, send_file, abort, jsonify, make_response
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
app = Flask(__name__, static_url_path='')
rf = rainfall()

""" So we can host the content here as well """
@app.route('/', defaults={'path':None})
@app.route('/js/<path:path>', defaults={'path':None})
@app.route('/css/<path:path>', defaults={'path':None})
@app.route('/img/<path:path>', defaults={'path':None})
def file_resources(type, path):
  print('Hello')
  if path is None:
    return send_file('html/index.html')
  elif '/js/' in self.getRequest().url:
    return send_file('html/js/%s' % path)
  elif '/ccs/' in self.getRequest().url:
    return send_file('html/ccs/%s' % path)
  elif '/img/' in self.getRequest().url:
    return send_file('html/img/%s' % path)
  return abort(404)

@app.route('/sprinklers', defaults={'id': None})
@app.route('/sprinklers/<int:id>')
def get_sprinkler(id):
  result = None
  if id is None:
    result = []
    for s in rf.getSprinklers():
      result.append({
        'id' : s.id,
        'name' : s.name,
        'enabled' : s.enabled,
        'running' : s.valve.enabled,
        'pin' : s.valve.getUserData(),
        'group' : 0,
        'schedule' : {
          'duration' : s.schedule.duration,
          'cycles' : s.schedule.cycles,
          'days' : s.schedule.days,
          'shift' : s.schedule.shift,
        }
      })
  else:
    s = rf.getSprinkler(id)
    result = {
      'id' : s.id,
      'name' : s.name,
      'enabled' : s.enabled,
      'running' : s.valve.enabled,
      'pin' : s.valve.getUserData(),
      'group' : 0,
      'schedule' : {
        'duration' : s.schedule.duration,
        'cycles' : s.schedule.cycles,
        'days' : s.schedule.days,
        'shift' : s.schedule.shift,
      }
    }
  return jsonify(result)

@app.route('/sprinkler/<int:id>', methods=['GET', 'POST'])
def control_sprinkler(id):
  j = None
  if 'POST' == request.method:
    j = request.json

  if j is not None:
    if 'open' in j:
      rf.openSprinkler(id, j['open'])
    if 'name' in j:
      rf.getSprinkler(id).setName(j['name'])
    if 'enable' in j:
      rf.getSprinkler(id).setEnable(j['enable'])
    if 'group' in j:
      rf.getSprinkler(id).setGroup(j['group'])
    rf.save()
  return get_sprinkler(id)

@app.route('/schedule/<int:id>', methods=['GET', 'POST'])
def control_schedule(id):
  j = None
  if 'POST' == request.method:
    j = request.json

  if j is not None:
    if 'duration' in j:
      rf.getSprinkler(id).schedule.setDuration(j['duration'])
    if 'cycles' in j:
      rf.getSprinkler(id).schedule.setCycles(j['cycles'])
    if 'days' in j:
      rf.getSprinkler(id).schedule.setDays(j['days'])
    if 'shift' in j:
      rf.getSprinkler(id).schedule.setShift(j['shift'])
    rf.save()
  s = rf.getSprinkler(id)
  return jsonify({
    'duration' : s.schedule.duration,
    'cycles' : s.schedule.cycles,
    'days' : s.schedule.days,
    'shift' : s.schedule.shift,
  })

@app.route('/add', methods=['POST'])
def control_add():
  j = request.json
  for f in ['enabled', 'name', 'group', 'schedule', 'pin']:
    if f not in j:
      logging.error('Adding sprinkler missing field %s', f)
      return abort(500)
  for f in ['duration', 'cycles', 'days', 'shift']:
    if f not in j['schedule']:
      logging.error('Adding sprinkler missing schedule field %s', f)
      return abort(500)
  s = rf.addSprinkler(j['pin'], j['name'])
  s.setEnable(j['enabled'])
  s.setSchedule(j['schedule']['duration'], j['schedule']['cycles'], j['schedule']['days'], j['schedule']['shift'])
  rf.save()
  return get_sprinkler(s.id)

@app.route('/delete', methods=['POST'])
def control_delete():
  j = request.json
  if 'id' in j:
    if rf.deleteSprinkler(j['id']):
      rf.save()
      return make_response('', 200)
  return abort(404)


rf.load()
rf.start()
app.run(debug=False, port=cmdline.port, host=cmdline.listen)

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
import json

class config:
  DIR_BASE = 'conf/'
  FILE_SPRINKLER = DIR_BASE + 'sprinklers.json'
  FILE_CONFIG = DIR_BASE + 'config.json'

  def __init__(self):
    self.sprinklers = []
    self.config = {'start-time' : 400}
    if not os.path.exists(config.DIR_BASE):
      os.mkdir(config.DIR_BASE)

  def save(self):
    with open(config.FILE_SPRINKLER, 'w') as f:
      json.dump(self.sprinklers, f, ensure_ascii=False)
    with open(config.FILE_CONFIG, 'w') as f:
      json.dump(self.config, f, ensure_ascii=False)

  def load(self):
    if os.path.exists(config.FILE_SPRINKLER):
      with open(config.FILE_SPRINKLER, 'r') as f:
        self.sprinklers = json.load(f)
    else:
      self.sprinklers = []

    if os.path.exists(config.FILE_CONFIG):
      with open(config.FILE_CONFIG, 'r') as f:
        self.config = json.load(f)
    else:
      self.config = {
        'time' : 400,
        'timing' : 0
      }

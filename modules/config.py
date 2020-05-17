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

import json

class config:
  def __init__(self):
    self.sprinklers = []
    self.config = {'start-time' : 400}

  def save(self):
    with open('conf/sprinklers.json', 'w') as f:
      json.dump(self.sprinklers, f, ensure_ascii=False)
    with open('conf/config.json', 'w') as f:
      json.dump(self.config, f, ensure_ascii=False)

  def load(self):
    with open('conf/sprinklers.json', 'r') as f:
      self.sprinklers = json.load(f)
    with open('conf/config.json', 'r') as f:
      self.config = json.load(f)

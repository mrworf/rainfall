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

import logging
import time

class audit:
  MAX_EVENTS_IN_MEMORY = 100
  _INSTANCE = None

  def __init__(self, filename):
    audit._INSTANCE = self

    self.filename = filename
    self.latestEvents = []
    self.file = None
    try:
      self.file = open(filename, 'a')
    except:
      logging.exception('Issue opening "%s" for writing', self.filename)
    if self.file is None:
      logging.error('Unable to open "%s" for saving audit log, no audit will be saved', self.filename)

  @staticmethod
  def addEvent(tag, message):
    if audit._INSTANCE is None:
      #logging.error('Cannot use audit module, not initialized')
      return
    self = audit._INSTANCE

    evt = {
      'time' : datetime.now(),
      'tag' : tag,
      'message' : message
    }

    if self.file:
      self.file.write('%s: [%s] %s\n' % (
        evt['time'].strftime('%c'),
        evt['tag'],
        evt['message']
      ))
    self.latestEvents.append(evt)
    while len(self.latestEvents) > audit.MAX_EVENTS_IN_MEMORY:
      self.latestEvents.pop(0)

  @staticmethod
  def getEvents(latestEvents=True):
    if audit._INSTANCE is None:
      #logging.error('Cannot use audit module, not initialized')
      return
    self = audit._INSTANCE
    return self.latestEvents

  @staticmethod
  def numberOfEvents(latestEvents=True):
    if audit._INSTANCE is None:
      #logging.error('Cannot use audit module, not initialized')
      return
    self = audit._INSTANCE
    return len(self.latestEvents)

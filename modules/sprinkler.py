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

class sprinkler:
  def __init__(self, valve, schedule, enabled=True):
    self.valve = valve
    self.schedule = schedule
    self.enabled = enabled
    self.name = 'TBD'
    self.id = None

  def setId(self, id):
    self.id = id
    return self

  def setName(self, name):
    self.name = name
    return self

  def setEnable(self, enable):
    self.enabled = enable
    if not enable:
      self.valve.setEnable(False) # Stop asap
    return self

  def setSchedule(self, duration=None, cycles=None, days=None, shiftDay=None):
    if duration is not None:
      self.schedule.setDuration(duration)
    if cycles is not None:
      self.schedule.setCycles(cycles)
    if days is not None:
      self.schedule.setDays(days)
    if shiftDay is not None:
      self.schedule.setShift(shiftDay)
    return self

  def resetSchedule(self):
    self.setSchedule(1, 1, 1, 0)


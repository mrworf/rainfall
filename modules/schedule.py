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

class schedule:
  def __init__(self, duration=1, cycles=1, days=1, shiftDay=0):
    self.setDuration(duration)
    self.setCycles(cycles)
    self.setDays(days)
    self.setShift(shiftDay)

  def setDuration(self, duration):
    self.duration = 1 if duration < 1 else duration

  def setCycles(self, cycles):
    self.cycles = 1 if cycles < 1 else cycles

  def setDays(self, days):
    self.days = 1 if days < 1 else days

  def setShift(self, shiftDay):
    self.shift = 0 if shiftDay < 0 else shiftDay

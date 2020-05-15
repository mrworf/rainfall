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
import sys
import time
import math

from datetime import datetime
from threading import Thread

from modules.valve import valve
from modules.program import program
from modules.schedule import schedule
from modules.sprinkler import sprinkler
from modules.gpiodrv import gpiodrv

class rainfall(Thread):
  DEADLINE_FINISHBY = 0
  DEADLINE_START = 1

  def __init__(self):
    Thread.__init__(self)
    self._sprinklers = []
    self._sprinklerid = 0
    self.setDeadline(4, rainfall.DEADLINE_FINISHBY)
    self.gpiodrv = gpiodrv()

  def addSprinkler(self, valve, id=None, name=None, enable=True):
    s = sprinkler(valve, schedule(), enable)
    if id is None:
      s.setId(self._sprinklerid)
    else:
      s.setId(id)
    self._sprinklerid = max(s.id, self._sprinklerid)+1
    if name is not None:
      s.setName(name)
    self._sprinklers.append(s)
    return s

  def load(self):
    # Bank 1:  2,  3,  4, 14, 18, 15, 17, 27
    # Bank 2: 22, 23, 24, 10,  9, 11, 25,  8
    #
    self.addSprinkler(valve(self.gpiodrv.enablePin, self.gpiodrv.disablePin,  3),  0, 'Backyard drip').setSchedule(5, 2, 1, 0)
    self.addSprinkler(valve(self.gpiodrv.enablePin, self.gpiodrv.disablePin, 15),  1, 'Backyard lawn (1st half)').setSchedule(5, 2, 2, 0)
    self.addSprinkler(valve(self.gpiodrv.enablePin, self.gpiodrv.disablePin, 27),  2, 'Backyard lawn (2nd half)').setSchedule(5, 2, 2, 0)
    self.addSprinkler(valve(self.gpiodrv.enablePin, self.gpiodrv.disablePin, 22),  3, 'Sideyard tree').setSchedule(5, 2, 2, 1)
    self.addSprinkler(valve(self.gpiodrv.enablePin, self.gpiodrv.disablePin,  8),  4, 'Frontyard tree').setSchedule(15, 2, 1, 0)
    self.addSprinkler(valve(self.gpiodrv.enablePin, self.gpiodrv.disablePin, 10),  5, 'Front hedge').setSchedule(5, 2, 1, 0)
    self.addSprinkler(valve(self.gpiodrv.enablePin, self.gpiodrv.disablePin,  9),  6, 'Front lawn (1st half)').setSchedule(5, 2, 1, 0)
    self.addSprinkler(valve(self.gpiodrv.enablePin, self.gpiodrv.disablePin, 11),  7, 'Front lawn (2nd half plus side)').setSchedule(5, 2, 1, 0)

    self.addSprinkler(valve(self.gpiodrv.enablePin, self.gpiodrv.disablePin, 23),  8, 'New planterbox').setSchedule(10, 2, 1, 0)
    self.addSprinkler(valve(self.gpiodrv.enablePin, self.gpiodrv.disablePin, 25),  9, 'Old planterbox').setSchedule(10, 2, 1, 0)
    self.addSprinkler(valve(self.gpiodrv.enablePin, self.gpiodrv.disablePin, 24), 10, 'Roses along the house').setSchedule(5, 3, 1, 0)
    self.listSprinkler()

  def start(self):
    self.quit = False
    Thread.start(self)

  def run(self):
    self.program = program(self._sprinklers)
    while not self.quit:
      time.sleep(1) # Uhm, no, not great, but lazy for now
      dt = datetime.today()
      now = (dt.hour * 60 + dt.minute)
      #logging.debug('Current time: %d:%02d - Deadline: %d:%02d - Estimated start time: %d:%02d', now / 60, now % 60, self.deadline / 60, self.deadline % 60, self.getStartTime() / 60, self.getStartTime() % 60)
      #print('\x1b[A\x1b[KCurrent time: %d:%02d - Deadline: %d:%02d - Estimated start time: %d:%02d' % (now / 60, now % 60, self.deadline / 60, self.deadline % 60, self.getStartTime() / 60, self.getStartTime() % 60))
      run = False
      if self.deadlineMode == rainfall.DEADLINE_FINISHBY and now == self.getStartTime():
        deadline = self.getStartTime()
        logging.info('Deadline is %d:%02d, sprinklers will start now at %d:%02d since they take an estimated %d minutes to run',
          self.deadline / 60,
          self.deadline % 60,
          deadline / 60,
          deadline % 60,
          self.program.getEstimatedDuration())
        run = True
      elif self.deadlineMode == rainfall.DEADLINE_START and now == self.deadline:
        logging.info('Deadline is %d:%02d, sprinklers will start now. Estimated runtime is %d minutes',
          self.deadline / 60,
          self.deadline % 60,
          self.program.getEstimatedDuration())
        run = True
      if run:
        self.program.run()
        # It's assumed that the run takes more than a minute
        self.program = program(self._sprinklers)


  def setDeadline(self, hour, mode=0):
    self.deadline = hour*60
    self.deadlineMode = mode

  def getStartTime(self):
    minutes = self.deadline
    deadline = minutes - self.program.getEstimatedDuration()
    if deadline < 0:
      deadline += (24*60)
    return deadline % 1440


  def getSprinkler(self, id):
    for _sprinkler in self._sprinklers:
      if _sprinkler.valve.id == id:
        return _sprinkler
    return None

  def listSprinkler(self):
    for _sprinkler in self._sprinklers:
      logging.debug('%3d : (%3s | %-8s) %-40s %2dmin, %2d cycles, Every %2d days (shifted %d days)' % (
        _sprinkler.id,
        'on' if _sprinkler.valve.enabled else 'off',
        'enabled' if _sprinkler.enabled else 'disabled',
        _sprinkler.name,
        _sprinkler.schedule.duration,
        _sprinkler.schedule.cycles,
        _sprinkler.schedule.days,
        _sprinkler.schedule.shift
      ))
    logging.debug('Total runtime: %d minutes' % self.getDurationTotal())

  def getDurationTotal(self, enabledOnly=False):
    result = 0
    for _sprinkler in self._sprinklers:
      if _sprinkler.enabled or not enabledOnly:
        result += _sprinkler.schedule.cycles * _sprinkler.schedule.duration
    return result

  def getDuration(self, id, enabledOnly=False):
    for _sprinkler in self._sprinklers:
      if _sprinkler.id == id and (_sprinkler.enabled or not enabledOnly):
        return _sprinkler.schedule.cycles * _sprinkler.schedule.duration
    return 0

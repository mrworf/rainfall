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
from modules.config import config

class rainfall(Thread):
  DEADLINE_FINISHBY = 0
  DEADLINE_START = 1

  def __init__(self):
    Thread.__init__(self)
    self._sprinklers = []
    self._sprinklerid = 0
    self.setDeadline(4, rainfall.DEADLINE_FINISHBY)
    self.gpiodrv = gpiodrv()
    self.config = config()

  def addSprinkler(self, pin, name):
    return self.__addSprinkler(valve(self.gpiodrv.enablePin, self.gpiodrv.disablePin,  pin),  name=name).setSchedule(1, 1, 1, 0)

  def __addSprinkler(self, valve, id=None, name=None, enable=True):
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
    self.config.load()

    for cfg in self.config.sprinklers:
      s = self.__addSprinkler(valve(self.gpiodrv.enablePin, self.gpiodrv.disablePin, cfg['pin']), cfg['id'], cfg['name'], cfg['enabled'] if 'enabled' in cfg else True)
      s.setSchedule(
        cfg['schedule']['duration'],
        cfg['schedule']['cycles'],
        cfg['schedule']['days'],
        cfg['schedule']['shift']
      )

    self.listSprinkler()

  def save(self):
    self.config.sprinkers = []
    for s in self._sprinklers:
      self.config.sprinklers.append(
        {
          'name' : s.name,
          'id' : s.id,
          'pin' : s.valve.getUserData(),
          'enabled' : s.enabled,
          'schedule' : {
            'duration' : s.schedule.duration,
            'cycles' : s.schedule.cycles,
            'days' : s.schedule.days,
            'shift' : s.schedule.shift
          }
        })
      self.config.save()

  def start(self):
    self.quit = False
    Thread.start(self)

  def run(self):
    self.program = program(self._sprinklers)
    while not self.quit:
      time.sleep(1) # Uhm, no, not great, but lazy for now
      dt = datetime.today()
      now = (dt.hour * 60 + dt.minute)
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

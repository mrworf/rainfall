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
from threading import Thread, Event

from modules.valve import valve
from modules.program import program
from modules.schedule import schedule
from modules.sprinkler import sprinkler
from modules.config import config

class rainfall(Thread):
  DEADLINE_FINISHBY = 0
  DEADLINE_START = 1

  MAX_RUNTIME = 30*60

  EVT_OPEN = 1
  EVT_CLOSE = 2
  EVT_RECALCULATE = 3
  EVT_RUN_PROGRAM = 4

  def __init__(self, useVirtual=False, accelerateTime=False):
    Thread.__init__(self)
    self._sprinklers = []
    self._sprinklerid = 0
    if useVirtual:
      from modules.virtualdrv import virtualdrv
      self.gpiodrv = virtualdrv()
    else:
      from modules.gpiodrv import gpiodrv
      self.gpiodrv = gpiodrv()
    self.config = config()
    self.events = []
    self.delayer = Event()
    self.programRunning = False
    self.accelerateTime = accelerateTime
    logging.warning('Accelerating wallclock')

  def addSprinkler(self, pin, name):
    return self.__addSprinkler(valve(self.gpiodrv.enablePin, self.gpiodrv.disablePin,  pin),  name=name).setSchedule(1, 1, 1, 0)

  def deleteSprinkler(self, id):
    s = self.getSprinkler(id)
    if s is not None:
      s.valve.setEnable(False)
      self._sprinklers.remove(s)
      return True
    return False

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

    clean = False
    for cfg in self.config.sprinklers:
      if self.getSprinkler(cfg['id']):
        logging.warning('Sprinkler with ID %d already exists, skipping', cfg['id'])
        clean=True
        continue
      s = self.__addSprinkler(valve(self.gpiodrv.enablePin, self.gpiodrv.disablePin, cfg['pin']), cfg['id'], cfg['name'], cfg['enabled'] if 'enabled' in cfg else True)
      s.setSchedule(
        cfg['schedule']['duration'],
        cfg['schedule']['cycles'],
        cfg['schedule']['days'],
        cfg['schedule']['shift']
      )

    if clean:
      logging.info('Saving cleaned sprinkler list')
      self.save()

    self.listSprinkler()

  def save(self):
    self.config.sprinklers = []
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
    self.program = program(self._sprinklers, 1 if self.accelerateTime else 60)
    now = 0
    if self.accelerateTime:
      dt = datetime.today()
      now = (dt.hour * 60 + dt.minute)
      now = 0

    while not self.quit:
      self.delayer.wait(30 if not self.accelerateTime else 0.1 ) # +/- 30s response time
      self.delayer.clear()
      forceRun = False
      # Handle potential events
      while len(self.events) > 0:
        evt = self.events.pop(0)
        if evt['event'] == rainfall.EVT_OPEN:
          self.getSprinkler(evt['value']).valve.setEnable(True)
        elif evt['event'] == rainfall.EVT_CLOSE:
          self.getSprinkler(evt['value']).valve.setEnable(False)
        elif evt['event'] == rainfall.EVT_RECALCULATE:
          self.program = program(self._sprinklers, 1 if self.accelerateTime else 60)
        elif evt['event'] == rainfall.EVT_RUN_PROGRAM:
          forceRun = True

      # Watchdog!
      for s in self._sprinklers:
        if s.valve.enableAt is not None and (time.time() - s.valve.enableAt) > rainfall.MAX_RUNTIME:
          logging.error('Valve %d (%s), pin #%d has been open for %d seconds which exceeds max runtime (%d). Closing', s.id, s.name, s.valve.getUserData(), (time.time() - s.valve.enableAt), rainfall.MAX_RUNTIME)
          s.valve.setEnable(False)

      if self.accelerateTime:
        now = (now + 1) % 1440
        if now % 30 == 0:
          logging.debug('Assumed time is now: %d:%02d', now / 60, now % 60)
      else:
        dt = datetime.today()
        now = (dt.hour * 60 + dt.minute)
      run = False
      if self.config.config['timing'] == rainfall.DEADLINE_FINISHBY and now == self.getStartTime():
        deadline = self.getStartTime()
        logging.info('Deadline is %d:%02d, sprinklers will start at %d:%02d since they take an estimated %d minutes to run and should be done by %d:%02d',
          self.config.config['time'] / 60,
          self.config.config['time'] % 60,
          deadline / 60,
          deadline % 60,
          self.program.getEstimatedDuration(),
          now / 60,
          now % 60
          )
        run = True
      elif self.config.config['timing'] == rainfall.DEADLINE_START and now == self.config.config['time']:
        logging.info('Deadline is %d:%02d, sprinklers will start now at %d:%02d. Estimated runtime is %d minutes',
          self.config.config['timing'] / 60,
          self.config.config['timing'] % 60,
          now / 60,
          now % 60,
          self.program.getEstimatedDuration())
        run = True
      if run or forceRun:
        self.programRunning = True
        self.program.run()
        self.programRunning = False
        # It's assumed that the run takes more than a minute
        self.program = program(self._sprinklers, 1 if self.accelerateTime else 60)

  def getStartTime(self):
    minutes = self.config.config['time']
    deadline = minutes - self.program.getEstimatedDuration()
    #logging.debug('Deadline is %d', deadline)
    if deadline < 0:
      deadline += (24*60)
    return deadline % 1440

  def getSprinkler(self, id):
    for s in self._sprinklers:
      if s.id == id:
        return s
    return None

  def getSprinklers(self):
    return self._sprinklers

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

  def addEvent(self, event, value):
    self.events.append({'event':event, 'value':value})
    self.delayer.set()

  def openSprinkler(self, id, open):
    self.addEvent(rainfall.EVT_OPEN if open else rainfall.EVT_CLOSE, id)

  def settingsChanged(self):
    self.addEvent(rainfall.EVT_RECALCULATE, 0)

  def setGroup(self, id, group):
    pass # Not yet implemented

  def programStop(self):
    if self.programRunning:
      self.program.quit = True

  def programStart(self):
    if not self.programRunning:
      self.addEvent(rainfall.EVT_RUN_PROGRAM, 0)

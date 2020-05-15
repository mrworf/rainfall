#!/usr/bin/env python3

import os
import logging
import argparse
import sys
import time
import math

from datetime import datetime
from threading import Thread
import gpiozero

#from flask import Flask, request
#from flask_httpauth import HTTPBasicAuth
#from werkzeug.exceptions import HTTPException

class program(Thread):
  def __init__(self, sprinklers, timeScale=60):
    Thread.__init__(self)
    self.work = []
    self.duration = 0
    for sprinkler in sprinklers:
      if not sprinkler.enabled:
        continue
      if (self._getDayCounter() + sprinkler.schedule.shift) % sprinkler.schedule.days != 0:
        logging.debug('Skipping %s due to days=%d, shift=%d setting', sprinkler.name, sprinkler.schedule.days, sprinkler.schedule.shift)
        continue

      work = {
        'sprinkler' : sprinkler,
        'cycles' : 0
      }
      self.work.append(work)
      self.duration += sprinkler.schedule.duration * sprinkler.schedule.cycles

    self.active = None
    self.time = 0
    self.timeScale = timeScale
    self.done = False
    self.quit = False
    if len(self.work) == 0:
      logging.warning('No (enabled) sprinklers were provided')

  def getEstimatedDuration(self):
    return self.duration

  def _getDayCounter(self):
    return math.floor(time.time() / 86400)

  def isDone(self):
    return self.done

  def start(self):
    if self.done:
      return False
    self.quit = False
    Thread.start(self)
    return True

  def run(self):
    remaining = 1
    logging.info('Starting program with %d sprinklers, expected runtime %d minutes (1 min = %d seconds)', len(self.work), self.duration, self.timeScale)
    cycle = 0

    while remaining > 0 and not self.quit:
      remaining = 0
      cycle += 1
      logging.info('Starting cycle #%d', cycle)
      for self.active in self.work:
        sprinkler = self.active['sprinkler']
        if self.active['cycles'] < sprinkler.schedule.cycles:
          logging.info('Running sprinkler %2d (%s) for %d minutes (cycle %d of %d)' % (
            sprinkler.id,
            sprinkler.name,
            sprinkler.schedule.duration,
            self.active['cycles'] + 1,
            sprinkler.schedule.cycles
          ))
          sprinkler.valve.setEnable(True)
          for self.time in range(0, sprinkler.schedule.duration * self.timeScale):
            if self.quit: break
            time.sleep(1)
          sprinkler.valve.setEnable(False)
          self.active['cycles'] += 1
          remaining += (sprinkler.schedule.cycles - self.active['cycles'])
    self.done = True

class valve:
  def __init__(self, cbEnable, cbDisable, userData):
    self._cbEnable = cbEnable
    self._cbDisable = cbDisable
    self._userData = userData
    self.enabled = False
    if not cbEnable or not cbDisable:
      logging.warning('No actual way of enabling/disabling valve')

  def setEnable(self, enable):
    if enable and self._cbEnable:
      logging.debug('Opening valve')
      self._cbEnable(self._userData)
    elif self._cbDisable:
      logging.debug('Closing valve')
      self._cbDisable(self._userData)
    self.enabled = enable
    return self

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
    dayBefore = False
    if deadline < 0:
      deadline += (24*60)
      dayBefore = True
    return deadline


  def getSprinkler(self, id):
    for sprinkler in self._sprinklers:
      if sprinkler.valve.id == id:
        return sprinkler
    return None

  def listSprinkler(self):
    for sprinkler in self._sprinklers:
      logging.debug('%3d : (%3s | %-8s) %-40s %2dmin, %2d cycles, Every %2d days (shifted %d days)' % (
        sprinkler.id,
        'on' if sprinkler.valve.enabled else 'off',
        'enabled' if sprinkler.enabled else 'disabled',
        sprinkler.name,
        sprinkler.schedule.duration,
        sprinkler.schedule.cycles,
        sprinkler.schedule.days,
        sprinkler.schedule.shift
      ))
    logging.debug('Total runtime: %d minutes' % self.getDurationTotal())

  def getDurationTotal(self, enabledOnly=False):
    result = 0
    for sprinkler in self._sprinklers:
      if sprinkler.enabled or not enabledOnly:
        result += sprinkler.schedule.cycles * sprinkler.schedule.duration
    return result

  def getDuration(self, id, enabledOnly=False):
    for sprinkler in self._sprinklers:
      if sprinkler.id == id and (sprinkler.enabled or not enabledOnly):
        return sprinkler.schedule.cycles * sprinkler.schedule.duration
    return 0

class gpiodrv:
  def __init__(self):
    self.pin = None
    self.hw = None
    pass

  def enablePin(self, pin):
    if self.pin != pin:
      self.pin = pin
      self.hw = gpiozero.LED(pin, active_high=False)

    self.hw.on()

  def disablePin(self, pin):
    if self.pin != pin:
      self.pin = pin
      self.hw = gpiozero.LED(pin, active_high=False)

    self.hw.off()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

rf = rainfall()
rf.load()
sys.exit(rf.start())

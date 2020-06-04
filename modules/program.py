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
import math

from threading import Thread
from modules.audit import audit

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

    audit.addEvent('PROGRAM', 'Initialized with %d sprinklers. Expected runtime %d minutes' % (len(self.work), self.duration))

    startTime = time.time()

    while remaining > 0 and not self.quit:
      remaining = 0
      cycle += 1
      logging.info('Starting cycle #%d', cycle)
      for self.active in self.work:
        if self.quit: break
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

    endTime = time.time()
    runTime = endTime - startTime

    audit.addEvent('PROGRAM', 'Ended after %d.%02d minutes, end reason was %s' %
      (
        math.floor(runTime / 60),
        int(runTime % 60),
        "completed" if not self.quit else "user ended it"
      )
    )
    self.done = True

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

import gpiozero
import logging

class gpiodrv:
  def __init__(self, stateChange):
    self.pin = None
    self.hw = None
    self.stateChange = stateChange
    pass

  def notifyChange(self, pin, state):
    if self.stateChange is None:
      return
    self.stateChange(pin, state)

  def enablePin(self, pin):
    if self.pin != pin:
      if self.pin is not None and self.hw is not None:
        logging.debug('Turning off pin %d', self.pin)
        self.hw.off()
        self.notifyChange(self.pin, False)
      self.pin = pin
      self.hw = gpiozero.LED(pin, active_high=False)
    logging.debug('Turning on pin %d', pin)
    self.hw.on()
    self.notifyChange(self.pin, True)

  def disablePin(self, pin):
    if self.pin != pin:
      # Not enabled in the first place
      return

    logging.debug('Turning off pin %d', pin)
    self.hw.off()
    self.notifyChange(self.pin, False)

  def initPin(self, pin):
    if pin == self.pin:
      logging.warning('Cannot init a PIN which is in-use')
      return
    # Simply creating the object will reset the GPIO, but just to be sure
    gpiozero.LED(pin, active_high=False).off()

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

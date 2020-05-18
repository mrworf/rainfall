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

class virtualdrv:
  def __init__(self):
    self.pin = None
    self.hw = None
    logging.warning('Using virtual GPIO driver. No actual GPIO changes will happen!')

  def enablePin(self, pin):
    if self.pin != pin:
      if self.pin is not None and self.hw is not None:
        logging.info('Turning off pin %d', self.pin)
      self.pin = pin
      self.hw = True
    logging.info('Turning on pin %d', pin)

  def disablePin(self, pin):
    if self.pin != pin:
      # Not enabled in the first place
      return
    logging.info('Turning off pin %d', pin)

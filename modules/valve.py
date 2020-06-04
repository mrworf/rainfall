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
from modules.audit import audit

class valve:
  def __init__(self, cbEnable, cbDisable, userData):
    self._cbEnable = cbEnable
    self._cbDisable = cbDisable
    self._userData = userData
    self.enabled = False
    self.enableAt = None
    if not cbEnable or not cbDisable:
      logging.warning('No actual way of enabling/disabling valve')

  def getUserData(self):
    return self._userData

  def setEnable(self, enable):
    if enable and self._cbEnable:
      self.enabled = enable
      logging.debug('Opening valve')
      self.enableAt = time.time()
      audit.addEvent('VALVE', 'setEnable(%s) on valve %s' % ('True' if enable else 'False', repr(self._userData)))
      self._cbEnable(self._userData)
    elif self.enabled and self._cbDisable:
      self.enabled = enable
      logging.debug('Closing valve')
      self.enableAt = None
      audit.addEvent('VALVE', 'setEnable(%s) on valve %s' % ('True' if enable else 'False', repr(self._userData)))
      self._cbDisable(self._userData)
    return self


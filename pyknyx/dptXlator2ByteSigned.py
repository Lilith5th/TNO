# -*- coding: utf-8 -*-



""" Python KNX framework
License
=======
 - B{PyKNyX} (U{https://github.com/knxd/pyknyx}) is Copyright:
  - © 2016-2017 Matthias Urlichs
  - PyKNyX is a fork of pKNyX
   - © 2013-2015 Frédéric Mantegazza
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
or see:
 - U{http://www.gnu.org/licenses/gpl.html}
Module purpose
==============
Datapoint Types management
Implements
==========
 - B{DPTXlator2ByteSigned}
Usage
=====
see L{DPTXlatorBoolean}
@author: Frédéric Mantegazza
@author: B. Malinowsky
@copyright: (C) 2013-2015 Frédéric Mantegazza
@copyright: (C) 2006, 2011 B. Malinowsky
@license: GPL
"""

import struct
#from pyknyx.services.logger import logging; logger = logging.getLogger(__name__)
from pyknyx.dptId import DPTID
from pyknyx.dpt import DPT
from pyknyx.dptXlatorBase import DPTXlatorBase, DPTXlatorValueError

class DPTXlator2ByteSigned(DPTXlatorBase):
    """ DPTXlator class for 2-Byte-Unsigned (V16) KNX Datapoint Type
     - 2 Byte Signed: VVVVVVVV VVVVVVVV
     - V: Bytes [-32768:32767]
    .
    """

    DPT_Generic = DPT("8.xxx", "Generic", (-32768, 32767))
    DPT_Value_2_Count = DPT("8.001", "Signed count", (-32768, 32767), "pulses")
    DPT_DeltaTimeMsec = DPT("8.002", "Delta time (ms)", (-32768, 32767), "ms")
    DPT_DeltaTime10Msec = DPT("8.003", "Delta time (10ms)", (-327680, 327670), "ms")
    DPT_DeltaTime100Msec = DPT("8.004", "Delta time (100ms)", (-3276800, 3276700), "ms")
    DPT_DeltaTimeSec = DPT("8.005", "Delta time (s)", (-32768, 32767), "s")
    DPT_DeltaTimeMin = DPT("8.006", "Delta time (min)", (-32768, 32767), "min")
    DPT_DeltaTimeHrs = DPT("8.007", "Delta time (h)", (-32768, 32767), "h")
    DPT_Percent_V16 = DPT("8.010", "Percent (16 bit)", (-327.68, 327.67), "%")
    DPT_Rotation_Angle = DPT("8.011", "Rotation angle", (-32768, 32767), "°")

    def __init__(self, dptId):
        super(DPTXlator2ByteSigned, self).__init__(dptId, 2)

    def checkData(self, data):
        if not 0x0000 <= data <= 0xffff:
            raise DPTXlatorValueError("data %s not in (0x0000, 0xffff)" % hex(data))

    def checkValue(self, value):
        if not self._dpt.limits[0] <= value <= self._dpt.limits[1]:
            raise DPTXlatorValueError("Value not in range %s" % repr(self._dpt.limits))

    def dataToValue(self, data):
        if data >= 0x8000:
            data = -((data - 1) ^ 0xffff)  # invert twos complement
        else:
            data = data
        if self._dpt is self.DPT_DeltaTime10Msec:
            value = data * 10.
        elif self._dpt is self.DPT_DeltaTime100Msec:
            value =data * 100.
        elif self._dpt is self.DPT_Percent_V16:
            value = data / 100.
        else:
            value = data
        #logger.debug("DPTXlator2ByteSigned._toValue(): value=%d" % value)
        return value

    def valueToData(self, value):
        if value < 0:
            value = (abs(value) ^ 0xffff) + 1  # twos complement
        if self._dpt is self.DPT_DeltaTime10Msec:
            data = int(round(value / 10.))
        elif self._dpt is self.DPT_DeltaTime100Msec:
            data = int(round(value / 100.))
        elif self._dpt is self.DPT_Percent_V16:
            data = int(round(value * 100.))
        else:
            data = value
        #logger.debug("DPTXlator2ByteSigned.valueToData(): data=%s" % hex(data))
        return data

    def dataToFrame(self, data):
        return bytearray(struct.pack(">H", data))

    def frameToData(self, frame):
        data = struct.unpack(">H", frame)[0]
        return data

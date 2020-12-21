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

 - B{DPTXlator2ByteUnsigned}

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


class DPTXlator2ByteUnsigned(DPTXlatorBase):
    """ DPTXlator class for 2-Byte-Unsigned (U16) KNX Datapoint Type

      - 2 Byte Unsigned: UUUUUUUU UUUUUUUU
      - U: Bytes [0:65535]

    .
    """
    DPT_Generic = DPT("7.xxx", "Generic", (0, 65535))

    DPT_Value_2_Ucount = DPT("7.001", "Unsigned count", (0, 65535), "pulses")
    DPT_TimePeriodMsec = DPT("7.002", "Time period (resol. 1ms)", (0, 65535), "ms")
    DPT_TimePeriod10Msec = DPT("7.003", "Time period (resol. 10ms)", (0, 655350), "ms")
    DPT_TimePeriod100Msec = DPT("7.004", "Time period (resol. 100ms)", (0, 6553500), "ms")
    DPT_TimePeriodSec = DPT("7.005", "Time period (resol. 1s)", (0, 65535), "s")
    DPT_TimePeriodMin = DPT("7.006", "Time period (resol. 1min)", (0, 65535), "min")
    DPT_TimePeriodHrs = DPT("7.007", "Time period (resol. 1h)", (0, 65535), "h")
    DPT_PropDataType = DPT("7.010", "Interface object property ID", (0, 65535))
    DPT_Length_mm = DPT("7.011", "Length", (0, 65535), "mm")
    #DPT_UEICurrentmA = DPT("7.012", "Electrical current", (0, 65535), "mA")  # Add special meaning for 0 (create Limit object)
    DPT_Brightness = DPT("7.013", "Brightness", (0, 65535), "lx")

    def __init__(self, dptId):
        super(DPTXlator2ByteUnsigned, self).__init__(dptId, 2)

    def checkData(self, data):
        if not 0x0000 <= data <= 0xffff:
            raise DPTXlatorValueError("data %s not in (0x0000, 0xffff)" % hex(data))

    def checkValue(self, value):
        if not self._dpt.limits[0] <= value <= self._dpt.limits[1]:
            raise DPTXlatorValueError("Value not in range %s" % repr(self._dpt.limits))

    def dataToValue(self, data):
        if self._dpt is self.DPT_TimePeriod10Msec:
            value = data * 10.
        elif self._dpt is self.DPT_TimePeriod100Msec:
            value = data * 100.
        else:
            value = data
        #logger.debug("DPTXlator2ByteUnsigned._toValue(): value=%d" % value)
        return value

    def valueToData(self, value):
        if self._dpt is self.DPT_TimePeriod10Msec:
            data = int(round(value / 10.))
        elif self._dpt is self.DPT_TimePeriod100Msec:
            data = int(round(value / 100.))
        else:
            data = value
        #logger.debug("DPTXlator2ByteUnsigned.valueToData(): data=%s" % hex(data))
        return data

    def dataToFrame(self, data):
        return bytearray(struct.pack(">H", data))

    def frameToData(self, frame):
        data = struct.unpack(">H", frame)[0]
        return data

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

Datapoint Types management.

Implements
==========

 - B{DPTXlatorTime}

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

#from pyknyx.logger import logging; logger = logging.getLogger(__name__)
from pyknyx.dptId import DPTID
from pyknyx.dpt import DPT
from pyknyx.dptXlatorBase import DPTXlatorBase, DPTXlatorValueError


class DPTXlatorTime(DPTXlatorBase):
    """ DPTXlator class for Time (N3U5r2U6r2U6) KNX Datapoint Type

     - 3 Byte: NNNHHHHH rrMMMMMM rrSSSSSS
     - N: Week day [0:7]
     - H: Hour [0:23]
     - M: Minute [0:59]
     - S: Second [0:59]
     - r: reserved (0)

    .
    """
    DPT_Generic = DPT("10.xxx", "Generic", (0, 16777215))
    DPT_TimeOfDay = DPT("10.001", "Time of day", ((0, 0, 0, 0), (7, 23, 59, 59)))

    def __init__(self, dptId):
        super(DPTXlatorTime, self).__init__(dptId, 3)

    def checkData(self, data):
        if not 0x000000 <= data <= 0xffffff:
            raise DPTXlatorValueError("data %s not in (0x000000, 0xffffff)" % hex(data))

    def checkValue(self, value):
        for index in range(4):
            if not self._dpt.limits[0][index] <= value[index] <= self._dpt.limits[1][index]:
                raise DPTXlatorValueError("value not in range %s" % repr(self._dpt.limits))

    def dataToValue(self, data):
        wDay = (data >> 21) & 0x07
        hour = (data >> 16) & 0x1f
        min_ = (data >> 8) & 0x3f
        sec = data & 0x3f
        value = (wDay, hour, min_, sec)
        #logger.debug("DPTXlatorTime._toValue(): value=%d" % value)
        return value

    def valueToData(self, value):
        # add from string and from int (sec)?
        wDay = value[0]
        hour = value[1]
        min_ = value[2]
        sec = value[3]
        data = wDay << 21 | hour << 16 | min_ << 8 | sec
        #logger.debug("DPTXlatorTime.valueToData(): data=%s" % hex(data))
        return data

    def dataToFrame(self, data):
        data = [(data >> shift) & 0xff for shift in range(16, -1, -8)]
        return bytearray(struct.pack(">3B", *data))

    def frameToData(self, frame):
        data = struct.unpack(">3B", frame)
        data = data[0] << 16 | data[1] << 8 | data[2]
        return data

    @property
    def weekDay(self):
        wDay = self.value[0]
        hour = self.value[1]
        min_ = self.value[2]
        sec = self.value[3]
        if wDay == 0:
            format_ = "No day"  # "No day, %H:%M:%S"
        else:
            format_ = "%a"
        s = time.strftime(format_, (0, 0, 0, hour, min_, sec, wDay - 1, 0, 0))
        return s

    @property
    def hour(self):
        return self.value[1]

    @property
    def minute(self):
        return self.value[2]

    @property
    def second(self):
        return self.value[3]


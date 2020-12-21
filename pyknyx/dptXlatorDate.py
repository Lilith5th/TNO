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

 - B{DPTXlatorDate}

Usage
=====

see L{DPTXlatorBoolean}

Note
====

KNX century encoding is as following:

 - if byte year >= 90, then real year is 20th century year
 - if byte year is < 90, then real year is 21th century year

Python time module does not encode century the same way:

 - if byte year >= 69, then real year is 20th century year
 - if byte year is < 69, then real year is 21th century year

The DPTXlatorDate class follows the python encoding.

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


class DPTXlatorDate(DPTXlatorBase):
    """ DPTXlator class for Date (r3U5r4U4r1U7) KNX Datapoint Type

     - 3 Byte: rrrDDDDD rrrrMMMM rYYYYYYY
     - D: Day [1:31]
     - M: Month [1:12]
     - Y: Year [0:99]
     - r: reserved (0)

    .
    """
    DPT_Generic = DPT("11.xxx", "Generic", (0, 16777215))
    DPT_Date = DPT("11.001", "Date", ((1, 1, 1969), (31, 12, 2068)))

    def __init__(self, dptId):
        super(DPTXlatorDate, self).__init__(dptId, 3)

    def checkData(self, data):
        if not 0x000000 <= data <= 0xffffff:
            raise DPTXlatorValueError("data %s not in (0x000000, 0xffffff)" % hex(data))

    def checkValue(self, value):
        for index in range(3):
            if not self._dpt.limits[0][index] <= value[index] <= self._dpt.limits[1][index]:
                raise DPTXlatorValueError("value not in range %s" % repr(self._dpt.limits))

    def dataToValue(self, data):
        day = (data >> 16) & 0x1f
        month = (data >> 8) & 0x0f
        year = data & 0x7f
        if year >= 69:
            year += 1900
        else:
            year += 2000
        value = (day, month, year)
        #logger.debug("DPTXlatorDate._toValue(): value=%d" % value)
        return value

    def valueToData(self, value):
        day = value[0]
        month = value[1]
        year = value[2]
        if year >= 2000:
            year -= 2000
        else:
            year -= 1900
        data = day << 16 | month << 8 | year
        #logger.debug("DPTXlatorDate.valueToData(): data=%s" % hex(data))
        return data

    def dataToFrame(self, data):
        data = [(data >> shift) & 0xff for shift in range(16, -1, -8)]
        return bytearray(struct.pack(">3B", *data))

    def frameToData(self, frame):
        data = struct.unpack(">3B", frame)
        data = data[0] << 16 | data[1] << 8 | data[2]
        return data

    @property
    def day(self):
        return self.value[0]

    @property
    def month(self):
        return self.value[1]

    @property
    def year(self):
        return self.value[2]


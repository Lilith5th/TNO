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

 - B{DPTXlatorString}

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

The DPTXlatorString class follows the python encoding.

@author: Frédéric Mantegazza
@author: B. Malinowsky
@copyright: (C) 2013-2015 Frédéric Mantegazza
@copyright: (C) 2006, 2011 B. Malinowsky
@license: GPL
"""

from __future__ import division

import struct

#from pyknyx.services.logger import logging; logger = logging.getLogger(__name__)
from pyknyx.dptId import DPTID
from pyknyx.dpt import DPT
from pyknyx.dptXlatorBase import DPTXlatorBase, DPTXlatorValueError


class DPTXlatorString(DPTXlatorBase):
    """ DPTXlator class for String (A112) KNX Datapoint Type

     - 14 Byte: AAAAAAAA ... AAAAAAAA
     - A: Char [0:255]

    .
    """
    DPT_Generic = DPT("16.xxx", "Generic", (0, 5192296858534827628530496329220095))

    DPT_String_ASCII = DPT("16.000", "String", (14 * (0,), 14 * (127,)))
    DPT_String_8859_1 = DPT("16.001", "String", (14 * (0,), 14 * (255,)))

    def __init__(self, dptId):
        super(DPTXlatorString, self).__init__(dptId, 14)

    def checkData(self, data):
        if not 0x0000000000000000000000000000 <= data <= 0xffffffffffffffffffffffffffff:
            raise DPTXlatorValueError("data %s not in (0x0000000000000000000000000000, 0xffffffffffffffffffffffffffff)" % hex(data))

    def checkValue(self, value):
        for index in range(14):
            if not self._dpt.limits[0][index] <= value[index] <= self._dpt.limits[1][index]:
                raise DPTXlatorValueError("value not in range %s" % repr(self._dpt.limits))

    def dataToValue(self, data):
        value = tuple([int((data >> shift) & 0xff) for shift in range(104, -1, -8)])
        #logger.debug("DPTXlatorString._toValue(): value=%d" % value)
        return value

    def valueToData(self, value):
        data = 0x00
        for shift in range(104, -1, -8):
            data |= value[13 - shift // 8] << shift
        #logger.debug("DPTXlatorString.valueToData(): data=%s" % hex(data))
        return data

    def dataToFrame(self, data):
        return bytearray(struct.pack(">14B", *self.dataToValue(data)))

    def frameToData(self, frame):
        value = struct.unpack(">14B", frame)
        data = self.valueToData(value)
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


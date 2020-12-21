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

 - B{DPTXlator8BitSigned}

Usage
=====

see L{DPTXlatorBoolean}

@author: Frédéric Mantegazza
@author: B. Malinowsky
@copyright: (C) 2013-2015 Frédéric Mantegazza
@copyright: (C) 2006, 2012 B. Malinowsky
@license: GPL
"""

import struct

#from pyknyx.services.logger import logging; logger = logging.getLogger(__name__)
from pyknyx.dptId import DPTID
from pyknyx.dpt import DPT
from pyknyx.dptXlatorBase import DPTXlatorBase, DPTXlatorValueError


def twos_comp(val, bits):
    """compute the 2's compliment of int value val"""
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val


class DPTXlator8BitSigned(DPTXlatorBase):
    """ DPTXlator class for 8-Bit-Signed (V8) KNX Datapoint Type

     - 1 Byte: VVVVVVVV
     - V: Byte [-128:127]

    .
    """
    DPT_Generic = DPT("6.xxx", "Generic", (-128, 127))

    DPT_Percent_V8 = DPT("6.001", "Percent (8 bit)", (-128, 127), "%")
    DPT_Value_1_Count = DPT("6.010", "Signed count", (-128, 127), "pulses")
    #DPT_Status_Mode3 = DPT("6.020", "Status mode 3", (, ))

    def __init__(self, dptId):
        super(DPTXlator8BitSigned, self).__init__(dptId, 1)

    def checkData(self, data):
        if not 0x00 <= data <= 0xff:
            raise DPTXlatorValueError("data %s not in (0x00, 0xff)" % hex(data))

    def checkValue(self, value):
        if not self._dpt.limits[0] <= value <= self._dpt.limits[1]:
            raise DPTXlatorValueError("value not in range %s" % repr(self._dpt.limits))

    def dataToValue(self, data):
        if data >= 0x80:
            value = -((data - 1) ^ 0xff)  # invert twos complement
        else:
            value = data
        #logger.debug("DPTXlator8BitSigned._toValue(): value=%d" % value)
        return value

    def valueToData(self, value):
        if value < 0:
            value = (abs(value) ^ 0xff) + 1  # twos complement
        data = value
        #logger.debug("DPTXlator8BitSigned.valueToData(): data=%s" % hex(data))
        return data

    def dataToFrame(self, data):
        return bytearray(struct.pack(">B", data))

    def frameToData(self, frame):
        data = struct.unpack(">B", frame)[0]
        return data

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

 - B{DPTXlator8BitUnsigned}

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


class DPTXlator8BitUnsigned(DPTXlatorBase):
    """ DPTXlator class for 8-Bit-Unsigned (U8) KNX Datapoint Type

     - 1 Byte: UUUUUUUU
     - U: Byte [0:255]

    .
    """
    DPT_Generic = DPT("5.xxx", "Generic", (0, 255))

    DPT_Scaling = DPT("5.001", "Scaling", (0, 100), "%")
    DPT_Angle = DPT("5.003", "Angle", (0, 360), "°")
    DPT_Percent_U8 = DPT("5.004", "Percent (8 bit)", (0, 255), "%")
    DPT_DecimalFactor = DPT("5.005", "Decimal factor", (0, 1), "ratio")
    #DPT_Tariff = DPT("5.006", "Tariff", (0, 254), "ratio")
    DPT_Value_1_Ucount = DPT("5.010", "Unsigned count", (0, 255), "pulses")

    def __init__(self, dptId):
        super(DPTXlator8BitUnsigned, self).__init__(dptId, 1)

    def checkData(self, data):
        if not 0x00 <= data <= 0xff:
            raise DPTXlatorValueError("data %s not in (0x00, 0xff)" % hex(data))

    def checkValue(self, value):
        if not self._dpt.limits[0] <= value <= self._dpt.limits[1]:
            raise DPTXlatorValueError("value not in range %s" % repr(self._dpt.limits))

    def dataToValue(self, data):
        #if type(data) is str:       ##TODO ADDED LUCANO
        #    data = float (data)     ##TODO ADDED LUCANO
        if data is None:
            print ("incorrect data value. Data can not be 'None' ")
        else:
            value = data
            if self._dpt is self.DPT_Scaling:# PERCENTAGE
                value = value * 100.0 / 255.0
            elif self._dpt is self.DPT_Angle:
                value = value * 360. / 255.
            elif self._dpt is self.DPT_DecimalFactor:
                value = value / 255.
            #logger.debug("DPTXlator8BitUnsigned.dataToValue(): value=%d" % value)
            return value

    def valueToData(self, value):
        if self._dpt is self.DPT_Scaling:
            data = int(round(value * 255 / 100.))
        elif self._dpt is self.DPT_Angle:
            data = int(round(value * 255 / 360.))
        elif self._dpt is self.DPT_DecimalFactor:
            data = int(round(value * 255))
        else:
            data = value
        #logger.debug("DPTXlator8BitUnsigned.valueToData(): data=%s" % hex(data))
        return data

    def dataToFrame(self, data):
        try:
            return bytearray(struct.pack(">B", data))
        except:
            return

    def frameToData(self, frame):
        data = struct.unpack(">B", frame)[0]
        return data

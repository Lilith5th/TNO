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

 - B{DPTXlator4ByteSigned}

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


class DPTXlator4ByteSigned(DPTXlatorBase):
    """ DPTXlator class for 4-Byte-Signed (V32) KNX Datapoint Type

     - 4 Byte Signed: VVVVVVVV VVVVVVVV VVVVVVVV VVVVVVVV
     - V: Bytes [-2147483648:2147483647]

    .
    """
    DPT_Generic = DPT("13.xxx", "Generic", (-2147483648, 2147483647))

    DPT_Value_4_Count = DPT("13.001", "Signed count", (-2147483648, 2147483647), "pulses")
    DPT_Value_FlowRate_m3h = DPT("13.001", "Flow rate", (-214748.3648, 214748.3647), "m³/h")
    DPT_ActiveEnergy = DPT("13.010", "Active energy", (-214748.3648, 214748.3647), "W.h")
    DPT_ApparentEnergy = DPT("13.011", "Apparent energy", (-214748.3648, 214748.3647), "VA.h")
    DPT_ReactiveEnergy = DPT("13.012", "Reactive energy", (-214748.3648, 214748.3647), "VAR.h")
    DPT_ActiveEnergy_kWh = DPT("13.013", "Active energy (kWh)", (-214748.3648, 214748.3647), "kW.h")
    DPT_ApparentEnergy_kVAh = DPT("13.014", "Apparent energy (kVAh)", (-214748.3648, 214748.3647), "kVA.h")
    DPT_ReactiveEnergy_KVARh = DPT("13.015", "Reactive energy (kVARh)", (-214748.3648, 214748.3647), "kVAR.h")
    DPT_LongDeltaTimeSec = DPT("13.100", "Long delta time", (-214748.3648, 214748.3647), "s")

    def __init__(self, dptId):
        super(DPTXlator4ByteSigned, self).__init__(dptId, 4)

    def checkData(self, data):
        if not 0x00000000 <= data <= 0xffffffff:
            raise DPTXlatorValueError("data %s not in (0x00000000, 0xffffffff)" % hex(data))

    def checkValue(self, value):
        if not self._dpt.limits[0] <= value <= self._dpt.limits[1]:
            raise DPTXlatorValueError("Value not in range %s" % repr(self._dpt.limits))

    def dataToValue(self, data):
        if data >= 0x80000000:
            data = -((data - 1) ^ 0xffffffff)  # invert twos complement
        else:
            data = data
        if self._dpt is self.DPT_Value_FlowRate_m3h:
            value = data / 10000.
        else:
            value = data
        #logger.debug("DPTXlator4ByteSigned._toValue(): value=%d" % value)
        return value

    def valueToData(self, value):
        if value < 0:
            value = (abs(value) ^ 0xffffffff) + 1  # twos complement
        if self._dpt is self.DPT_Value_FlowRate_m3h:
            data = int(round(value * 10000.))
        else:
            data = value
        #logger.debug("DPTXlator4ByteSigned.valueToData(): data=%s" % hex(data))
        return data

    def dataToFrame(self, data):
        return bytearray(struct.pack(">L", data))

    def frameToData(self, frame):
        data = struct.unpack(">L", frame)[0]
        return data

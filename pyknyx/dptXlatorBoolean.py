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

 - B{DPTXlatorBoolean}

Usage
=====

from dptBoolean import DPTXlatorBoolean
dpt = DPTXlatorBoolean("1.001")
dpt.value
ValueError: data not initialized
dpt.data = 0x01
dpt.data
1
dpt.value
'On'
dpt.value = 'Off'
dpt.data
0
dpt.frame
'\x00'
dpt.data = 2
ValueError: data 0x2 not in (0x00, 0x01)
dpt.value = 3
ValueError: value 3 not in ("Off", "On")
dpt.handledDPT
[<DPTID("1.xxx")>, <DPTID("1.001")>, <DPTID("1.002")>, <DPTID("1.003")>, <DPTID("1.004")>, <DPTID("1.005")>,
<DPTID("1.006")>, <DPTID("1.007")>, <DPTID("1.008")>, <DPTID("1.009")>, <DPTID("1.010")>, <DPTID("1.011")>,
<DPTID("1.012")>, <DPTID("1.013")>, <DPTID("1.014")>, <DPTID("1.015")>, <DPTID("1.016")>, <DPTID("1.017")>,
<DPTID("1.018")>, <DPTID("1.019")>, <DPTID("1.021")>, <DPTID("1.022")>, <DPTID("1.023")>]

@author: Frédéric Mantegazza
@author: B. Malinowsky
@copyright: (C) 2013-2015 Frédéric Mantegazza
@copyright: (C) 2006, 2011 B. Malinowsky
@license: GPL
"""

import struct

#from pyknyx.services.logger import logging; logger = logging.getLogger(__name__)
from pyknyx.dpt import DPT
from pyknyx.dptXlatorBase import DPTXlatorBase, DPTXlatorValueError


class DPTXlatorBoolean(DPTXlatorBase):
    """ DPTXlator class for 1-Bit (b0) KNX Datapoint Type

     - 1 Byte: 00000000B
     - B: Binary [0, 1]

    .
    """
    DPT_Generic = DPT("1.xxx", "Generic", (0, 1))

    DPT_Switch = DPT("1.001", "Switch", ("Off", "On"))
    DPT_Bool = DPT("1.002", "Boolean", (False, True))
    DPT_Enable = DPT("1.003", "Enable", ("Disable", "Enable"))
    DPT_Ramp = DPT("1.004", "Ramp", ("No ramp", "Ramp"))
    DPT_Alarm = DPT("1.005", "Alarm", ("No alarm", "Alarm"))
    DPT_BinaryValue = DPT("1.006", "Binary value", ("Low", "High"))
    DPT_Step = DPT("1.007", "Step", ("Decrease", "Increase"))
    DPT_UpDown = DPT("1.008", "Up/Down", ("Up", "Down"))
    DPT_OpenClose = DPT("1.009", "Open/Close", ("Open", "Close"))
    DPT_Start = DPT("1.010", "Start", ("Stop", "Start"))
    DPT_State = DPT("1.011", "State", ("Inactive", "Active"))
    DPT_Invert = DPT("1.012", "Invert", ("Not inverted", "Inverted"))
    DPT_DimSendStyle = DPT("1.013", "Dimmer send-style", ("Start/stop", "Cyclically"))
    DPT_InputSource = DPT("1.014", "Input source", ("Fixed", "Calculated"))
    DPT_Reset = DPT("1.015", "Reset", ("No action", "Reset"))
    DPT_Ack = DPT("1.016", "Acknowledge", ("No action", "Acknowledge"))
    DPT_Trigger = DPT("1.017", "Trigger", ("Trigger", "Trigger"))
    DPT_Occupancy = DPT("1.018", "Occupancy", ("Not occupied", "Occupied"))
    DPT_Window_Door = DPT("1.019", "Window/Door", ("Closed", "Open"))
    DPT_LogicalFunction = DPT("1.021", "Logical function", ("OR", "AND"))
    DPT_Scene_AB = DPT("1.022", "Scene A/B", ("Scene A", "Scene B"))
    DPT_ShutterBlinds_Mode = DPT("1.023", "Shutter/Blinds mode", ("Only move Up/Down", "Move Up/Down + StepStop"))

    def __init__(self, dptId):
        super(DPTXlatorBoolean, self).__init__(dptId, 0)

    def checkData(self, data):
        if data not in (0x00, 0x01):
            try:
                raise DPTXlatorValueError("data %s not in (0x00, 0x01)" % hex(data))
            except TypeError:
                raise DPTXlatorValueError("data not in (0x00, 0x01)")

    def checkValue(self, value):
        if value not in self._dpt.limits and value not in self.DPT_Generic.limits:
            raise DPTXlatorValueError("value %s not in %s" % (value, str(self._dpt.limits)))

    def dataToValue(self, data):
        #data = int(data, 16)#TODO LUCANO ADDED
        value = self._dpt.limits[data]
        #logger.debug("DPTXlatorBoolean.dataToValue(): value=%d" % value)
        return value

    def valueToData(self, value):
        #logger.debug("DPTXlatorBoolean.valueToData(): value=%d" % value)
        self.checkValue(value)
        try:
            data = self._dpt.limits.index(value)
        except ValueError:
            raise ValueError("Index not in tuple", self._dpt.limits,value)
        #logger.debug("DPTXlatorBoolean.valueToData(): data=%s" % hex(data))
        return data

    def dataToFrame(self, data):
        return bytearray(struct.pack(">B", data))

    def frameToData(self, frame):
        data = struct.unpack(">B", frame)[0]
        return data

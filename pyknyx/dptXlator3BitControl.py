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



 - B{DPTXlator3BitControl}



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



from pyknyx.services.logger import logging; logger = logging.getLogger(__name__)

from pyknyx.dpt import DPT

from pyknyx.dptXlatorBoolean import DPTXlatorBoolean

from pyknyx.dptXlatorBase import DPTXlatorBase, DPTXlatorValueError





class DPTXlator3BitControl(DPTXlatorBase):

    """ DPTXlator class for 3-Bit-Control (b0U3) KNX Datapoint Type



    This is a composite DPT.



     - 1 Byte: 0000CSSSS

     - C: Control bit [0, 1]

     - S: StepCode [0:7]



    The _data param of this DPT only handles the stepCode; the control bit is handled by the sub-DPT.



    @todo: create and use a DPTCompositeConverterBase?



    @ivar _dpt: sub-DPT

    @type _dpt: L{DPT}

    """

    DPT_Generic = DPT("3.xxx", "Generic", (-7, 7))



    DPT_Control_Dimming = DPT("3.007", "Dimming", (-7, 7))

    DPT_Control_Blinds = DPT("3.008", "Blinds", (-7, 7))



    def __init__(self, dptId):

        super(DPTXlator3BitControl, self).__init__(dptId, 0)



        sub = self.dpt.id.sub

        if sub is None:

            sub = 'xxx'

        dptId_ = '1.'+sub

        self._dpt2 = DPTXlatorBoolean(dptId_)



    def checkData(self, data):

        if not 0x00 <= data <= 0x0f:

            raise DPTXlatorValueError("data %s not in (0x00, 0x0f)" % hex(data))



    def checkValue(self, value):

        if not self._dpt.limits[0] <= value <= self._dpt.limits[1]:

            raise DPTXlatorValueError("value %d not in range %s" % (value, repr(self._dpt.limits)))



    def dataToValue(self, data):

        ctrl = (data & 0x08) >> 3

        stepCode = data & 0x07

        value = stepCode if ctrl else -stepCode

        return value



    def valueToData(self, value):

        ctrl = 1 if value > 0 else 0

        stepCode = abs(value) & 0x07

        data = ctrl << 3 | stepCode

        return data



    # Add properties control and stepCode + helper methods (+ intervals?)



    def dataToFrame(self, data):

        return bytearray(struct.pack(">B", data))



    def frameToData(self, frame):



        # Note the usage of self.data, and not data!

        data = struct.unpack(">B", frame)[0]

        return data



    #def nbIntervalsToStepCode(self, nbIntervals):

        #""" Compute the stepCode for a given number of intervals



        #The number of intervals is rounded to the nearest intervals representable with a stepcode

        #(e.g 48 rounded of to 32, 3 rounded of to 2).



        #@todo: use property, and work on _data



        #@param nbIntervals: number of intervals to devide the 0-100% range

        #@type nbIntervals: int



        #@return: stepCode

        #@rtype: int

        #"""

        #if nbIntervals - 1 not in range(64):

            #raise ValueError("nbIntervals not in range (1, 64)");

        #stepCode = 7

        #thres = 0x30

        #while thres >= nbIntervals:

            #stepCode -= 1

            #thres >>= 1

        #return stepCode



    #def stepCodeToNbIntervals(self, stepCode):

        #""" Compute the number of intervals for a given stepCode



        #@todo: use property, and work on _data



        #@param stepCode: stepCode to use

        #@type stepCode: int



        #@return: number of intervals

        #@rtype: int

        #"""

        #return 1 << stepCode - 1

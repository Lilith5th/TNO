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
 - B{DPTIDValueError}
 - B{DPTID}
Usage
=====
from dptId import DPTID
dptId = DPTID("1")
ValueError: invalid Datapoint Type ID ('1')
dptId = DPTID("1.001")
dptId
<DPTID("1.001")>
dptId.id
'1.001'
dptId.main
'1'
dptId.sub
'001'
dptId.generic
<DPTID("1.xxx")>
dptId.generic.main
'1'
dptId.generic.sub
'xxx'
dptId.generic.generic
<DPTID("1.xxx")>
@author: Frédéric Mantegazza
@copyright: (C) 2013-2015 Frédéric Mantegazza
@license: GPL
"""

import re

#from pyknyx.common.exception import PyKNyXValueError
#from pyknyx.services.logger import logging; logger = logging.getLogger(__name__)


#class DPTIDValueError(PyKNyXValueError):
#    """
#    """


class DPTID(object):
    """ Datapoint Type ID class
    @ivar _id: Datapoint Type ID
    @type _id: str
    """
    def __init__(self, dptId=None, main=None,sub=None):
        """ Create a new Datapoint Type ID from the given id
        @param dptId: Datapoint Type ID to create
        @type dptId: str
        raise DPTIDValueError: invalid id
        """
        super(DPTID, self).__init__()

        if dptId is None:
            assert main is not None
            if sub is None:
                dptId = "%d.xxx" % (main,)
            else:
                dptId = "%d.%03d" % (main,sub)

        elif not re.match("^\d{1,3}\.\d{1,3}$", dptId) and not re.match("^\d{1,3}\.xxx$", dptId):
            raise DPTIDValueError("invalid Datapoint Type ID (%r)" % repr(dptId))

        self._id = dptId

    def __repr__(self):
        return "<DPTID('%s')>" % self._id

    def __str__(self):
        return self._id

    def __lt__(self, other):
        return self._cmp(other) < 0

    def __le__(self, other):
        return self._cmp(other) <= 0

    def __eq__(self, other):
        return self._cmp(other) == 0

    def __ne__(self, other):
        return self._cmp(other) != 0

    def __gt__(self, other):
        return self._cmp(other) > 0

    def __ge__(self, other):
        return self._cmp(other) >= 0

    def __hash__(self):
        return hash((self.main, self.sub))

    def _cmp(self, other):
        """ Make comp on id
        @return: -1 if self < other, zero if self == other, +1 if self > other
        @rtype: int
        """

        if self.main != other.main:
            return self.main - other.main
        elif other.sub is None:
            return self.sub is not None
        elif self.sub is None:
            return -1
        else:
            return self.sub - other.sub

    @property
    def id(self):
        """ Return the Datapoint Type ID
        """
        return self._id

    @property
    def main(self):
        """ Return the main part of the Datapoint Type ID
        """
        return int(self._id.split('.')[0])

    @property
    def sub(self):
        """ Return the sub part of the Datapoint Type ID
        """
        try:
            return int(self._id.split('.')[1])
        except ValueError:
            return None

    @property
    def generic(self):
        """ Return the generic Datapoint Type ID
        """
        genericId = re.sub(r"^(.*)\..*$", r"\1.xxx",  self._id)
        return DPTID(genericId)

    def isGeneric(self):
        """ Test if generic ID
        @return: True if Datapoint Type ID is a generic Datapoint Type ID
        @rtype: bool
        """
        return self == self.generic


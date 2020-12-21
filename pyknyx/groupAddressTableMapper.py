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

Manage GroupAddress table mapping.

Implements
==========

 - B{GroupAddressTableMapper}

Documentation
=============

Allow the mapping between real L{GroupAddress<pyknyx.stack.groupAddress>} and nick names, for easier use.

By default, the mapper will look in the given path for a module named B{gadMapTable.py}, and will load the map table
from B{GAD_MAP_TABLE} dict.

The GAD map table must be in the form:

GAD_MAP_TABLE = {
    "1/-/-": dict(name="light", desc="Lights (1/-/-)"),
    "1/1/-": dict(name="light_cmd", desc="Commands (1/1/-)"),
    "1/1/1": dict(name="light_cmd_test", desc="Test (1/1/1)"),
    "1/2/-": dict(name="light_state", desc="States (1/2/-)"),
    "1/2/1": dict(name="light_state_test", desc="Test (1/2/1)"),
    "1/3/-": dict(name="light_delay", desc="Delays (1/3/-)"),
    "1/3/1": dict(name="light_delay_test", desc="Test (1/3/1)"),
}

GroupAddressTableMapper object is a singleton.

Usage
=====

mapper = GroupAddressTableMapper()
mapper.loadFrom("/tmp")
print(mapper.table)
{'1/2/1': {'name': 'light_state_test', 'desc': 'Test'}, '1/3/-': {'name': 'light_delay', 'desc': 'Delays'},
'1/2/-': {'name': 'light_state', 'desc': 'States'}, '1/1/-': {'name': 'light_cmd', 'desc': 'Commands'},
'1/-/-': {'name': 'light', 'desc': 'Lights'}, '1/1/1': {'name': 'light_cmd_test', 'desc': 'Test'},
'1/3/1': {'name': 'light_delay_test', 'desc': 'Test'}}
print(mapper.deepTable)

print(mapper.getNickname("1/1/1"))
'light_cmd_test'
print(mapper.getGad("light_state_test"))
'1/2/1'
print(mapper.getDesc("1/3/1"))
'Test (1/3/1)'
print(mapper.getDesc("light_state_test"))
'Test (1/3/1)'

@author: Frédéric Mantegazza
@copyright: (C) 2014 Frédéric Mantegazza
@license: GPL
"""

import six
import re
import os.path
import imp
import xml.etree.ElementTree as etree

from pyknyx.exception import PyKNyXValueError
from pyknyx.common.singleton import Singleton
from pyknyx.dptXlatorFactory import DPTXlatorFactory
from pyknyx.services.logger import logging; logger = logging.getLogger(__name__)
#from pyknyx.groupAddress import GroupAddress, GroupAddressValueError       #pyknyx.stack.

class GroupAddressTableMapperValueError(PyKNyXValueError):
    """
    """


@six.add_metaclass(Singleton)
class GroupAddressTableMapper(object):
    """ GroupAddressTableMapper class

    @ivar _gadMapModule: customized map module name
    @type _gadMapModule: str

    @ivar _gadMapTable: GroupAddress mapping table
    @type _gadMapTable: dict
    """

    def __init__(self, module='gadMapTable'):
        """ Init the GroupAddressTableMapper.

        @param module: module name to load
        @type module: str

        raise GroupAddressTableMapperValueError:
        """
        super(GroupAddressTableMapper, self).__init__()

        self._gadMapModule = module

        self._gadMapTable = {}

    @property
    def table(self):
        return self._gadMapTable

    def isTableValid(self, table):
        """ Check GAD map table validity.

        GAD and nickname should be unique (GAD are, as they are dict keys!)
        """
        nicknames = {}
        for key, value in table.items():
            if value['name'] in nicknames:
                logger.warning("Duplicated nickname '%s' in GAD map table" % value['name'])
                return False
            else:
                nicknames[value['name']] = dict(gad=key, desc=value['desc'])
        return True

    def _loadTable(self, path):
        """ Do load the GAD map table from module.

        @param path: path from where import module
        @type path: str
        """
        gadMapTable = {}
        if os.path.exists(path):
            logger.debug("GroupAddressTableMapper.loadTable(): GAD map path is '%s'" % path)

            try:
                fp, pathname, description = imp.find_module(self._gadMapModule, [os.path.curdir, path])
            except ImportError:
                logger.warning("Can't find '%s' module in '%s'" % (self._gadMapModule, path))
            else:
                try:
                    gadMapModule = imp.load_module(self._gadMapModule, fp, pathname, description)
                finally:
                    if fp:
                        fp.close()
                gadMapTable.update(gadMapModule.GAD_MAP_TABLE)

        elif path != "$PKNYX_GAD_MAP_PATH":
            logger.warning("GAD map path '%s' does not exists" % path)
        return gadMapTable

    def _loadXMLTable(self, file):
        gadMapTable = {}
        if os.path.exists(file):
            logger.debug("GroupAddressTableMapper.loadXMLTable(): loading from '%s'" % file)

            tree = etree.parse(file)
            root = tree.getroot()
            for gad in root.findall('.//ets:GroupAddress', namespaces={'ets': 'http://knx.org/xml/project/12'}):
                numericAddress = int(gad.get('Address'))
                name = gad.get('Name')
                dpt = gad.get('DatapointType')
                dptId = None

                hg = (numericAddress >> 11) & 0x0F
                mg = (numericAddress >>  8) & 0x07
                ga = (numericAddress >>  0) & 0xFF

                dptmatch = re.search('DPT-([0-9]+)', dpt)
                if dptmatch:
                    dptId="%i.*" % (int(dptmatch.group(1)))

                dpstmatch = re.search('DPST-([0-9]+)-([0-9]+)', dpt)
                if dpstmatch:
                    dptId="%i.%i" % (int(dpstmatch.group(1)), int(dpstmatch.group(2)))

                gadMapTable["%i/%i/%i" % (hg,mg,ga)] = {'name': name, 'desc': None, 'dptId': dptId}

        else:
            logger.warning("GAD map XML '%s' does not exist" % file)
        return gadMapTable

    def loadXML(self, file):
        """ Load GAD map table from ETS XML Project File.
        """

        table = self._loadXMLTable(file)
        if self.isTableValid(table):
            self._gadMapTable = {}
            self._gadMapTable.update(table)

    def loadFrom(self, path):
        """ Load GAD map table from module in GAD map path.
        """
        table = self._loadTable(path)
        if self.isTableValid(table):
            self._gadMapTable = {}
            self._gadMapTable.update(table)

    def updateFrom(self, path):
        """ Updated GAD map table from module in GAD map path.
        """
        table = self._loadTable(path)
        if self.isTableValid(table):
            self._gadMapTable.update(table)

    def loadWith(self, table):
        """ Load GAD map table from given table.
        """
        if self.isTableValid(table):
            self._gadMapTable = {}
            self._gadMapTable.update(table)

    def updateWith(self, table):
        """ Updated GAD map table from given table.
        """
        if self.isTableValid(table):
            self._gadMapTable.update(table)

    def getGad(self, nickname):
        """ Convert GAD nickname to GAD.
        @param nickname: GAD nickname
        @type nickname: str
        @return: real GAD
        @rtype: str
        @raise GroupAddressTableMapperValueError:
        """
        for key, value in self._gadMapTable.items():
            if nickname == value['name']:
                return key
        else:
            raise GroupAddressTableMapperValueError("Can't find '%s' GAD nickname in GAD map table" % nickname)

    def getNickname(self, gad):
        """ Convert GAD to GAD nickname.
        @param gad: real GAD
        @type gad: str
        @return: GAD nickname
        @rtype: str
        @raise GroupAddressTableMapperValueError:
        """
        try:
            return self._gadMapTable[gad]['name']
        except KeyError:
            raise GroupAddressTableMapperValueError("Can't find GAD '%s' in GAD map table" % gad)

    def getDesc(self, gad):
        """ Return the description of the given GAD/nickname.

        @param gad: GAD/nickname
        @type gad: str

        @return: GAD/nickname description
        @rtype: str

        @raise GroupAddressTableMapperValueError:
        """
        try:
            value = self._gadMapTable[gad]
        except KeyError:
            try:
                value = self._gadMapTable[self.getGad(gad)]
            except KeyError:
                raise GroupAddressTableMapperValueError("Can't find GAD nor nickname '%s' in GAD map table" % gad)

        try:
            return value['desc']
        except KeyError:
            raise GroupAddressTableMapperValueError("Can't find a description for given GAD/nickname (%s)" % gad)

    def getDptXlator(self, gad):
        """ Return a datapoint translator for the given GAD/nickname

        @param: GAD/nickname
        @type: str

        @return: datapoint translator
        @tpye DPTXlator

        @raise GroupAddressTableMapperValueError:
        """
        try:
            value = self._gadMapTable[gad]
        except KeyError:
            try:
                value = self._gadMapTable[self.getGad(gad)]
            except KeyError:
                raise GroupAddressTableMapperValueError("Can't find GAD nor nickname '%s' in GAD map table" % gad)

        try:
            dptId = value['dptId']
        except KeyError:
            raise  GroupAddressTableMapperValueError("Can't find a dataponint id for given GAD/nickname (%s)" % gad)

        if dptId == None:
            return None

        return DPTXlatorFactory().create(dptId)


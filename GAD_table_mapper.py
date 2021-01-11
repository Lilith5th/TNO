# -*- coding: utf-8 -*-

import six
import re
import os.path
import imp
import xml.etree.ElementTree as etree

from pyknyx.exception import PyKNyXValueError
from pyknyx.common.singleton import Singleton
from pyknyx.dptXlatorFactory import DPTXlatorFactory
#from pyknyx.services.logger import logging; logger = logging.getLogger(__name__)
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

    def __init__(self, module='DATA_KNXAdresses', GAD=""):
        """ Init the GroupAddressTableMapper.

        @param module: module name to load
        @type module: str

        raise GroupAddressTableMapperValueError:
        """
        super(GroupAddressTableMapper, self).__init__()

        self._gadMapModule = module
        self._gadMapTable = {}
        if GAD is not "":
            self._gadMapTable=GAD
        #from CurProjectSettings.DATA_SPELLCHECK import CUR_SPELLCHECK_TABLE
        #self._gadMapTable = CUR_SPELLCHECK_TABLE

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
            elif nickname == value['inputAddress']:#LUCANO 4 SPELLCHECKER
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
            return self._gadMapTable[gad]['read_write']
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



    def getRead_Write(self, gad):
        """ Convert GAD to GAD nickname.
        @param gad: real GAD
        @type gad: str
        @return: GAD nickname
        @rtype: str
        @raise GroupAddressTableMapperValueError:
        """
        try:
            return self._gadMapTable[gad]['read_write']
        except KeyError:
            raise GroupAddressTableMapperValueError("Can't find GAD '%s' in GAD map table" % gad)
    

    def getLocation(self, gad):
        """ Convert GAD to GAD nickname.
        @param gad: real GAD
        @type gad: str
        @return: GAD nickname
        @rtype: str
        @raise GroupAddressTableMapperValueError:
        """
        try:
            return self._gadMapTable[gad]['location']
        except KeyError:
            raise GroupAddressTableMapperValueError("Can't find GAD '%s' in GAD map table" % gad)

        return DPTXlatorFactory().create(dptId)
    

    def getBlinds_Pair(self, gad):
        """ Convert GAD to GAD nickname.
        @param gad: real GAD
        @type gad: str
        @return: GAD nickname
        @rtype: str
        @raise GroupAddressTableMapperValueError:
        """
        try:
            return self._gadMapTable[gad]['blinds_pair']
        except KeyError:
            raise GroupAddressTableMapperValueError("Can't find GAD '%s' in GAD map table" % gad)

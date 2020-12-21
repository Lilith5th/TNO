import subprocess
from LKNX.LKNX_ProjectSettings import ProjectSettings
from LKNX.LKNX_AddressData import AddressData
from LKNX.LKNX_Errors import *
import time

import logging

def setup_logger(name, level=logging.INFO):
    """To setup as many loggers as you want"""
    from datetime import datetime
    curFilename = ("{}_{}.log".format(datetime.now().strftime("%Y_%m_%d"), name))
    handler = logging.FileHandler(curFilename, mode='a')    
    #handler.setFormatter('%(asctime)s %(message)s')
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

KNX_ToolRead_Log = setup_logger(__name__ + '_KNX_ToolRead_Log')
KNX_ToolWrite_Log = setup_logger(__name__ + '_KNX_ToolWrite_Log')
KNX_Data2Int_Log = setup_logger(__name__ + 'KNX_Data2Int_Log')
KNX_Error = setup_logger(__name__ + 'KNX_Error')

#from KNXClientMDPC import CURRENTGADTABLE
class KNXToolCommandSender(AddressData):
    def __init__(self,KNX_Address, *args,**kwargs):
        super().__init__(KNX_Address,args,**kwargs)

        # if self.KNX_Address is "" and 'name' in kwargs:
            # print ("setting name"+kwargs['name'])
            # #self.SetName(kwargs['name'])  
            # pass            
            
    # def SetName(self, name):
        # print ("try this...")
        # updatedName = name.replace("Pos", "Set_Pos")
        # updatedName = name.replace("Ang", "Set_Ang")
        # self.name=updatedName
        # print ("wow {}".format(self.name))
        # for (GAD_key, GAD_list) in self.GAD_TABLE.items():
            # print ("what")
            # if  updatedName in GAD_list['name'] :
                # self.KNX_Address = GAD_key
                # AddressData.__init__(self, self.KNX_Address,GAD_TABLE=self.GAD_TABLE)

                        

        
                         

    def runCmd(self, KNXGroup,readWrite, ValueHEX=""):

        try:
            KNXToolCommand = ('knxtool {} local: {} {}'.format(readWrite ,   KNXGroup,   ValueHEX))
            print (KNXToolCommand)
           
            KNX_ToolWrite_Log.info('KNXToolCommand: '.format(KNXToolCommand))
            proc = subprocess.Popen(KNXToolCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            KNXToolData,error = proc.communicate(timeout=5)
            print ("knxtool command result:{} error:{}".format(KNXToolData, error))
            KNX_ToolWrite_Log.info('TIMEOUT EXCEPTION: KNXGroup: {}, ValueHex: {}, readwrite: {} \n'.format(KNXGroup,ValueHEX, readWrite))            
            print ("runcmtError: {}".format(error))

            if error is not b'':
                return '-999',"error"

            if readWrite == 'read':
                KNX_ToolWrite_Log.info('SUCCESS: KNXGroup: {}, ValueHex: {}, readwrite: {} \nKNXtool_data: {}, KNXTool_error: {}'.format(KNXGroup,ValueHEX, readWrite, KNXToolData,error))
                return KNXToolData,""

            if 'write' in readWrite and KNXToolData == b'Send request':
                KNX_ToolWrite_Log.info('SUCCESS: KNXGroup: {}, ValueHex: {}, readwrite: {} \nKNXtool_data: {}, KNXTool_error: {}'.format(KNXGroup,ValueHEX, readWrite, KNXToolData,error))
                return "",""

            else: 
                KNX_ToolWrite_Log.error('Unknown KNXToolData reply : KNXGroup: {}, ValueHex: {}, readwrite: {} \nKNXtool_data: {}, KNXTool_error: {}'.format(KNXGroup,ValueHEX, readWrite, KNXToolData,error))
                return "",""
        
        except subprocess.TimeoutExpired:
            KNX_Error.info('TIMEOUT EXCEPTION: KNXGroup: {}, ValueHex: {}, readwrite: {} \n'.format(KNXGroup,ValueHEX, readWrite))
            return '-999', 'error'
                        
        except Exception as e:
            KNX_Error.info('EXCEPTION: KNXGroup: {}, ValueHex: {}, readwrite: {} \n'.format(KNXGroup,ValueHEX, readWrite))
            return '-999', 'error'
            


class KNXReader(KNXToolCommandSender):
 
    def __init__(self,KNX_Address="", *args,**kwargs):
        if KNX_Address is "" and 'name' in kwargs:
            name = kwargs['name']
            name = name.replace("Pos", "Get_Pos")
            name = name.replace("Ang", "Get_Ang")
            super().__init__(KNX_Address,name = name)
            return
        super().__init__(KNX_Address,args,kwargs)
        
    
        # print ("c")

            
        #super().__init__(KNX_Address,name=name,args,kwargs)
        
            # for (GAD_key, GAD_list) in self.GAD_TABLE.items():
                # if  name in GAD_list['name'] :
                    # KNX_Address = GAD_key
                    # KNXToolCommandSender.__init__(self,KNX_Address,GAD_TABLE=self.GAD_TABLE)



    def ReadValue(self):
        rawKNXtoolReply = super().runCmd(self.KNX_Address, self.readwrite)
        if rawKNXtoolReply[1] == "":
            HumanValue = self.KNXToolData2Int(self.KNX_Address,rawKNXtoolReply[0])
            KNX_ToolRead_Log.info('rawKNXtoolReply: {}, HumanValue: {}'.format(rawKNXtoolReply,HumanValue))
            return HumanValue[0],"" 
        else:
            KNX_ToolRead_Log.info('ERROR: rawKNXtoolReply: {}'.format(rawKNXtoolReply))
            return rawKNXtoolReply

    def KNXToolData2Int(self,group, data):
        try:
            from  GAD_table_mapper import GroupAddressTableMapper
            mapper = GroupAddressTableMapper(GAD=self.GAD_TABLE) 
            KNXToolDataStr = data.decode("utf-8") 
            numValue = self.convertHex2Int(KNXToolDataStr)
            translator = mapper.getDptXlator(group)
            if numValue != None:
                KNXToolDataTranslated = translator.dataToValue(numValue)
                self.value = KNXToolDataTranslated 
                return KNXToolDataTranslated, ''

        except Exception as e:
            KNX_Data2Int_Log.error('EXCEPTION: group: {} data: {} error: {}'.format(group, data, e))
            return 'N/A', 'error in KNXToolData2Int'

    def convertHex2Int(self, hex_number):
        test = hex_number.replace(' ', '')
        try:
            result = int(test, 16)
            return result
        except:
            logging.info("error converting hex 2 int")

class KNXWriter( KNXToolCommandSender):
    def __init__(self,KNX_Address="", *args,**kwargs):
        if KNX_Address != "": 
            print ("1")
            super().__init__(KNX_Address,args,kwargs)

        if KNX_Address is "" and 'name' in kwargs:
            name = kwargs['name']
            if "Set" not in name:
                name = name.replace("Pos", "Set_Pos")
                name = name.replace("Ang", "Set_Ang")   
            print ("name is "+name)  
            super().__init__(KNX_Address,name=name)
        print ("now here")
            
        if 'value' in kwargs:
            self.SetNewValue(kwargs['value'])
   

    def SetNewValue(self,value):
        DTPVal = None
        valueInt = int(value)

        if 'Ang' in self.name:
            valuePercent = int(valueInt / 0.9)
            DTPVal = self.__value2DPT(valuePercent)

        if 'Pos' in self.name:
            DTPVal = self.__value2DPT(valueInt)
        print ("get result" )
        result = super().runCmd(self.KNX_Address, self.readwrite,DTPVal)
        print ("got it"+ result[1])
        if result[1] != b'':
            pass


    #send data to knxbuss
    def __value2DPT(self, value):
        try:
            from  GAD_table_mapper import GroupAddressTableMapper
            mapper = GroupAddressTableMapper(GAD=self.GAD_TABLE) 
            translator = mapper.getDptXlator(self.KNX_Address)
            if value == '' or value is None:
                return ''
            else:
                self.value = value
                self.valueData = translator.valueToData(value)
                self.valueAsFrame = translator.dataToFrame(self.valueData)
                self.valueAsFrameHEX = self.valueAsFrame.hex()
                return str(self.valueAsFrameHEX)
        except Exception as e:
            pass





if __name__ == "__main__":
    try:
        settings = ProjectSettings()
        from LKNX_ProjectSettings import ProjectSettings
        from DATA_KNXAdresses import GAD_MAP_TABLE_OUTSIDE
        settings.GAD_TABLE = GAD_MAP_TABLE_OUTSIDE
        


        #tempData = KNXReader(name= "indoorTemp")
        #curVal,error = tempData.ReadValue()
        
        #settings.ServerIP = "http://90.145.162.7:8109"
        #startLogging()
        #main()
    
    except Exception as e:
        pass


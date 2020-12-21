
class KNXReaderOLD(AddressData):
    '''
    kwargs: {KNX_Address'', name=''}
    '''
    def __init__(self,*args,**kwargs):
        if 'KNX_Address' in kwargs:
            AddressData.__init__(self,*args,**kwargs)
            print (self)

        if 'name' in kwargs:
            GAD_TABLE = ProjectSettings().GAD_TABLE
            name = kwargs['name']
            print (name)
            name = name.replace("Pos", "Get_Pos")
            name = name.replace("Ang", "Get_Ang")
            for (GAD_key, GAD_list) in GAD_TABLE.items():
                if  name in GAD_list['name'] :
                    KNX_Address = GAD_key
                    AddressData.__init__(self,*args,**dict(GAD_TABLE=GAD_TABLE, KNX_Address=KNX_Address))
                    return

    def ReadValue(self):
        rawKNXToolReply = self.__getSensorOrCurrentBlindValue()
        if rawKNXtoolReply[1]==b'':
            HumanValue = self.KNXToolData2Int(self.KNX_Address,rawKNXToolReply)
            print(type(HumanValue))
            return HumanValue, b''
        else:
            return rawKNXtoolReply

    def __getSensorOrCurrentBlindValue(self):
        KNXToolCommand = ('knxtool {} local: {}'.format(self.readwrite, self.KNX_Address))

        try:
            proc = subprocess.Popen(KNXToolCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            KNXToolData,error = proc.communicate(timeout=5)
            print ('command:',KNXToolCommand)          
            print ('result: ', KNXToolData)
            self.valueAsFrame = KNXToolData
            return KNXToolData, error
        except:
            return 'N/A'

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
                return KNXToolDataTranslated
        except Exception as e:
            KNX_Data2Int_Log.error('group: {} data: {} error: {}'.format(group, data, e))
            return 'N/A', 'error in KNXToolData2Int'

    def convertHex2Int(self, hex_number):
        test = hex_number.replace(' ', '')
        try:
            result = int(test, 16)
            return result
        except:
            logging.info("error converting hex 2 int")

class KNXWriterOLD(AddressData):
    def __init__(self, *args,**kwargs):
        if 'KNX_Address' in kwargs:
            AddressData.__init__(self,KNX_Address,*args,**kwargs)
        elif  'name' in kwargs:
                self.GAD_TABLE =GAD_TABLE= ProjectSettings().GAD_TABLE
                name = kwargs['name'].replace("Pos", "Set_Pos")
                name = kwargs['name'].replace("Ang", "Set_Ang")
                for (GAD_key, GAD_list) in GAD_TABLE.items():
                    if  name in GAD_list['name'] :
                        KNX_Address = GAD_key
                        AddressData.__init__(self,*args,**dict(GAD_TABLE=GAD_TABLE, KNX_Address=KNX_Address))
                         
        if 'value' in kwargs and self.KNX_Address !="N/A":
                self.SetNewValue(kwargs['value'])

    def SetNewValue(self,value):
        DTPVal = None
        valueInt = int(value)

        if 'Ang' in self.name:
            valuePercent = int(valueInt * 0.9)
            DTPVal = self.__value2DPT(valuePercent)

        if 'Pos' in self.name:
            DTPVal = self.__value2DPT(valueInt)
        print ('dptval',DTPVal)
        result = self.__runCmd(self.KNX_Address, DTPVal, self.readwrite)

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


    def __runCmd(self, KNXGroup, ValueHEX, readWrite):
        try:
            KNXToolCommand = ('knxtool {} local: {} {}'.format(readWrite ,   KNXGroup,   ValueHEX))
            print('DATAPACKAGE runcmd running commandstring actual value is: {} ({})'.format(KNXToolCommand,ValueHEX))
            proc = subprocess.Popen(KNXToolCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            KNXToolData,error = proc.communicate(timeout=5)

            if KNXToolData == b'Send request' and error == b'':
                KNX_ToolWrite_Log.info('SUCCESS: KNXGroup: {}, ValueHex: {}, readwrite: {} \nKNXtool_data: {}, KNXTool_error: {}'.format(KNXGroup,ValueHEX, readWrite, KNXToolData,error))
                return 
            KNX_ToolWrite_Log.error('KNXGroup: {}, ValueHex: {}, readwrite: {} \nKNXtool_data: {}, KNXTool_error: {}'.format(KNXGroup,ValueHEX, readWrite, KNXToolData,error))
        except Exception as e:
            KNX_ToolWrite_Log.error('EXCEPTION: KNXGroup: {}, ValueHex: {}, readwrite: {} \nException: {}, KNXTool_error: {}'.format(KNXGroup,ValueHEX, readWrite, KNXToolData,e))

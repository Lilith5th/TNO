import sys
sys.path.append('..')

from LKNX.LKNX_flags import Flags
from LKNX.LKNX_AddressData import AddressData
from datetime import datetime
from LKNX.LKNX_converter import *
from LKNX.LKNX_ReadWriteValue import  KNXReader
from GAD_table_mapper import GroupAddressTableMapperValueError

class stdoutData(KNXReader):
    value = -999
    def __init__(self,stdout, *args, **kwargs):
        self.stdoutString = stdout
        list_of_words = stdout.split()
        KNX_Address = list_of_words[list_of_words.index('to') + 1]
        super().__init__(KNX_Address,args,kwargs)

        if "A_GroupValue_Write" in stdout:
            valueAsFrameHex = stdout.split("A_GroupValue_Write")[1].rstrip()
            valueAsFrameHex = valueAsFrameHex.replace('(small) ','')

            if valueAsFrameHex != None and valueAsFrameHex != '':
                    self.valueAsFrameHex = valueAsFrameHex
                    self.value = self.KNXToolData2Int(KNX_Address,valueAsFrameHex)
                    return

    def KNXToolData2Int(self,group, KNXToolDataStr):
        try:
            from  GAD_table_mapper import GroupAddressTableMapper
            mapper = GroupAddressTableMapper(GAD=self.GAD_TABLE) 
            try:
                KNXToolDataStr = KNXToolDataStr.decode("utf-8") 
            except:
                pass
            
            numValue =  self.convertHex2Int(KNXToolDataStr)
            translator = mapper.getDptXlator(group)
            if numValue != None:
                KNXToolDataTranslated = translator.dataToValue(numValue)
                self.value = KNXToolDataTranslated 
                return KNXToolDataTranslated

        except GroupAddressTableMapperValueError as e:
            return  b''

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)            
            print ("exception in stdoutData2int!{}".format(e))
            return '-999'

    def convertHex2Int(self, hex_number):
        test = hex_number.replace(' ', '')
        result = int(test, 16)
        return result





class stdoutDataLegacy(AddressData):
    def __init__(self,stdout, *args, **kwargs):
        print("stdout")
        self.stdoutString = stdout
        list_of_words = stdout.split()
        KNX_Address = list_of_words[list_of_words.index('to') + 1]
        print("how bout nou")
        valueAsFrameHex = stdout.split("A_GroupValue_Write")[1].rstrip()
        AddressData.__init__(self,KNX_Address=KNX_Address)
        print('converting hex value...')
        valueAsFrameHex = valueAsFrameHex.replace('(small) ','')
        print(valueAsFrameHex)
        
        if valueAsFrameHex != None or valueAsFrameHex != '':
            print("hex value present, and not none... converting")
            self.valueAsFrameHex = valueAsFrameHex


            conversion = Converter()
            self.value = self.KNXToolData2Int()
            print("ooook")
        
    def KNXToolData2Int(self):        
            print("converter")
            print(self.GAD_TABLE)
            
            if self.KNX_Address in self.GAD_TABLE:
                    print("address in GAD")
                    from  GAD_table_mapper import GroupAddressTableMapper
    
                    mapper = GroupAddressTableMapper(self.GAD_TABLE) 
                    KNXToolDataStr = self.valueAsFrameHex        
                    
                    #KNXToolDataStr = dataFrameHex.decode("utf-8")
                    print("here I go again")
                    #cleanup if (small) or (large) in value
                    cleanString = KNXToolDataStr[KNXToolDataStr.find(')') + 1:]
                    print("cleanstring - {}".format(cleanString))
                    #cleanup remove blank spaces
                    cleanString = cleanString.replace(' ','')
                    print(cleanString)      
                      
                    numValue = int(cleanString, 16)
                    print("now here...")
    
               
                    translator = mapper.getDptXlator(self.KNX_Address)
                    print('now herre again')
                    if numValue != None:
                        KNXToolDataTranslated = translator.dataToValue(numValue)
                        return KNXToolDataTranslated
                    return 'N/A'
    


from LKNX.LKNX_ProjectSettings import ProjectSettings


class Converter:
        GAD_TABLE={}
        def __init__(self,*args,**kwargs):
                if "GAD_TABLE" in kwargs:
                        self.GAD_TABLE=kwargs['GAD_TABLE']
                else:
                        self.GAD_TABLE= ProjectSettings().GAD_TABLE
                        
                
        def KNXToolData2Int(self,KNX_Address, dataFrameHex):        
                print("converter")
                
                if KNX_Address in GAD_TABLE:
                        print("address in GAD")
                        from  GAD_table_mapper import GroupAddressTableMapper
        
                        mapper = GroupAddressTableMapper(self.GAD_TABLE) 
                        KNXToolDataStr=dataFrameHex        
                        
                        #KNXToolDataStr = dataFrameHex.decode("utf-8") 
                        print ("here I go again")
                        #cleanup if (small) or (large) in value
                        cleanString = KNXToolDataStr[KNXToolDataStr.find(')')+1:]
                        print ("cleanstring - {}".format(cleanString))
                        #cleanup remove blank spaces   
                        cleanString = cleanString.replace(' ','')
                        print (cleanString)      
                          
                        numValue = int(cleanString, 16)
        
                        translator = mapper.getDptXlator(KNX_Address)
                        if numValue != None:
                            KNXToolDataTranslated = translator.dataToValue(numValue)
                            return KNXToolDataTranslated
                        return 'N/A'
        

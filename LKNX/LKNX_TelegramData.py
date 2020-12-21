from datetime import datetime
from LKNX.LKNX_AddressData import AddressData
from  GAD_table_mapper import GroupAddressTableMapper


class TelegramData(AddressData):
    def __init__(self,GAD_TABLE, KNX_Address,value=None,valueFrameHex=None, *args, **kwargs):
            super(TelegramData, self).__init__(GAD_TABLE, KNX_Address)
            #AddressData.__init__(self,GAD_TABLE,KNX_Address)
            #self.KNX_Address = KNX_Address
            self.time = datetime.now()
            self.timeString = self.time.strftime("%d/%m_%H:%M:%S")
            #self.timeString = self.time.strftime("%d/%m/%Y_%H:%M:%S")

            self.value = value
            self.valueAsData = None
            self.valueAsFrame = None
            self.valueAsFrameHEX = None
        
            if value is not None:
                self.value = value
                self.set_value(self.value,GAD_TABLE)

            if valueFrameHex is not None:
                if type(valueFrameHex) == str:
                
                    self.valueAsFrameHEX = bytearray.fromhex(str(valueFrameHex))
                    print('2 attribute:{}, converted ={}'.format(valueFrameHex,self.valueAsFrameHEX))                
                elif type(valueFrameHex) == bytearray:
                    self.valueAsFrameHEX = valueFrameHex
                self.set_frame_hex(self.valueAsFrameHEX,GAD_TABLE)
            #self.valueAsFrameHEX = ' '.join(a+b for a,b in
            #zip(iter(self.valueAsFrameHEX), iter(self.valueAsFrameHEX)))



    def set_value(self,value,GAD_TABLE):
        if self.KNX_Address in str(GAD_TABLE.keys()):
            mapper = GroupAddressTableMapper(GAD=GAD_TABLE) 
            translator = mapper.getDptXlator(self.KNX_Address)
            self.valueAsData = translator.valueToData(self.value)
            self.valueAsFrame = translator.dataToFrame(self.valueAsData)
            self.valueAsFrameHEX = self.valueAsFrame.hex()

    def set_frame_hex(self,valueFrameHex,GAD_TABLE):
        try:
            if self.KNX_Address in str(GAD_TABLE):
                mapper = GroupAddressTableMapper(GAD=GAD_TABLE) 
                translator = mapper.getDptXlator(self.KNX_Address)
                if type(valueFrameHex) == str:
                    valueFrameHex = bytearray.fromhex(valueFrameHex)
                if type(valueFrameHex) == bytearray:
                    self.valueAsData = translator.frameToData(valueFrameHex)
                    self.value = translator.dataToValue(self.valueAsData)
        except Exception as e:
            print( e)


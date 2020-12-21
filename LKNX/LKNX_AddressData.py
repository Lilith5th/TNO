from  GAD_table_mapper import GroupAddressTableMapper
from datetime import datetime
import tkinter as Tkinter
import tkinter.ttk as ttk
from collections import UserList
from LKNX.LKNX_flags import Flags
from LKNX.LKNX_ProjectSettings import ProjectSettings
from LKNX.LKNX_Errors import *

class AddressData:
    '''
    '''
    name = "N/A"
    dpt = "N/A"
    readwrite = "N/A"
    flags = Flags("")
    flagsString = "N/A"
    KNX_Address=''
    GAD_TABLE =dict()
    
    def __init__(self,KNX_Address, *args, **kwargs):
        if 'GAD_TABLE' in kwargs:
            self.GAD_TABLE= kwargs['GAD_TABLE']
        else:            
            self.GAD_TABLE= ProjectSettings().GAD_TABLE

        self.KNX_Address=KNX_Address
            
        if KNX_Address is not '':
            if self.KNX_Address in self.GAD_TABLE:
                GAD_list= self.GAD_TABLE[self.KNX_Address]
                self.name = GAD_list["name"]
                self.dpt = GAD_list["dptId"]
                self.readwrite = GAD_list["read_write"]
                self.flags = Flags(GAD_list["flags"])
                self.flagsString = GAD_list["flags"]
          
        elif 'name' in kwargs:
            for (GAD_key, GAD_list) in self.GAD_TABLE.items():
                if  kwargs['name'] == GAD_list['name'] :
                    self.KNX_Address = GAD_key
                    self.name = GAD_list["name"]
                    self.dpt = GAD_list["dptId"]
                    self.readwrite = GAD_list["read_write"]
                    self.flags = Flags(GAD_list["flags"])
                    self.flagsString = GAD_list["flags"]
                

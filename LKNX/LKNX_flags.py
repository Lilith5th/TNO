from  GAD_table_mapper import GroupAddressTableMapper
from datetime import datetime
import tkinter as Tkinter
import tkinter.ttk as ttk
from collections import UserList

#__all__ = ['vbusmonitorListener','stdoutDATA','ProjectSettings']
#Queue_vbus_stdoutDATA = queue.Queue()

class Flags(object):
    isBlind = False
    isSensor = False
    isAngle = False
    isPosition = False
    hasEcho = False
    isEcho = False
    isController = False
    isFeedback = False
    isInactive = False
    isUI = False
    isPassiveSensor=False
    def __init__(self, FlagsString,  *args, **kwargs):
        if 'blind' in FlagsString:
            self.isBlind = True
        if 'sensor' in FlagsString:
            self.isSensor=True
        if 'angle' in FlagsString:
            self.isAngle = True
        if 'position' in FlagsString:
            self.isPosition = True
        if 'hasEcho' in FlagsString:
            self.hasEcho = True
        if 'isEcho' in FlagsString:
            self.isEcho = True
        if 'isController' in FlagsString:
            self.isController = True
        if 'isFeedback' in FlagsString:
            self.isFeedback = True
        if 'inactive' in FlagsString:
            self.isInactive = True
        if 'isUI' in FlagsString:
            self.isUI= True
        if 'PassiveSensor' in FlagsString:
            self.isPassiveSensor= True
        return super().__init__(*args, **kwargs)

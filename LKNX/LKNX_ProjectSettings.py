import tkinter as Tkinter
import tkinter as ttk
from LKNX.LKNX_Singleton import Singleton

#from py_singleton import singleton

#@singleton
class ProjectSettings(metaclass=Singleton):
    KNXTOOL_ON :bool =None
    ServerIP : str =None
    GAD_TABLE :dict=None 
    def __init__(self, *args, **kwargs):
    
        for key in kwargs:
            print ("BASE BASE BASE " + key)
            setattr(self, key, kwargs[key])

        return super().__init__(*args, **kwargs)


import threading
import os          
import sys                      
import json 
import requests 
import serial
import time
import subprocess
import logging
import random
import traceback
from DATA_KNXAdresses import GAD_MAP_TABLE_OUTSIDE
from datetime import datetime

#from LKNX.LKNX_Singleton import Singleton
#from LKNX.LKNX_ProjectSettings import ProjectSettings
from LKNX.LKNX_ReadWriteValue import KNXReader, KNXWriter


from DATA_CurrentValues import currentValues
from ActivityData import ActivityData
from EmailNotice import EmailError
from PeriodicCamera import PeriodicCamera


log_dir = os.path.join(os.getcwd() ,"Logs")
log_dir_all = os.path.join(log_dir,"All")
log_dir_csv = os.path.join(log_dir,"CSV")

if not os.path.exists(log_dir):
    os.makedirs("Logs")
if not os.path.exists(log_dir_all):
    os.makedirs(os.path.join(log_dir,"All"))

#from pyknyx.services.logger import logging; logger =
#logging.getLogger(__name__)
def startLogging():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    curFilename = os.path.join(log_dir_all , ("{}_spellchecker_all_events.log".format(datetime.now().strftime("%Y_%m_%d"))))
    logging.basicConfig(filename=curFilename, filemode='a', 
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

def setup_logger(name):
    """To setup as many loggers as you want"""
    from datetime import datetime
    log_dir = os.path.join(os.getcwd() ,"Logs")  
    log_dir_current = os.path.join(log_dir,name)  
    if not os.path.exists(log_dir_current):
        os.makedirs(log_dir_current)    
    
    curFilename = os.path.join(log_dir_current, "{}_{}.log".format(datetime.now().strftime("%Y_%m_%d"), name))
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
    

    handler = logging.FileHandler(curFilename, mode='a')
    handler.setFormatter(formatter)
      
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    screen_handler.setLevel(40)
     
    #logging.basicConfig(level=logging.DEBUG,)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger
    
def setup_CSV_logger(name, level=logging.INFO):
    """To setup as many loggers as you want"""
    from datetime import datetime
    log_dir = os.path.join(os.getcwd() ,"Logs")  
    log_dir_current = os.path.join(log_dir,name)  
    if not os.path.exists(log_dir_current):
        os.makedirs(log_dir_current)    
    
    curFilename = os.path.join(log_dir_current, "{}_{}.csv".format(datetime.now().strftime("%Y_%m_%d"), name))
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
    

    handler = logging.FileHandler(curFilename, mode='a')
    handler.setFormatter(formatter)
      
    #screen_handler = logging.StreamHandler(stream=sys.stdout)
    #screen_handler.setFormatter(formatter)
     
    #logging.basicConfig(level=logging.DEBUG,)
    logger = logging.getLogger(name)
    logger.setLevel(40)
    logger.addHandler(handler)
    #logger.addHandler(screen_handler)
    return logger 

LOG_KNX_SENSORS= setup_logger('Sensors')
LOG_KNX_BLINDS = setup_logger('Blinds')

LOG_KNX_SENSORS_CSV = setup_CSV_logger('CSV_SENSORS')#NOT USED
LOG_KNX_BLINDS_CSV = setup_CSV_logger('CSV_BLINDS')#NOT USED

      
class KNX(object):
    errors = list()
    def __init__(self):
        self.g_DATA = currentValues()

    def refreshKNXData(self):
        try:
            print("KNX...acquiring sensor data...")
            self.errors = list()

            self.g_DATA.STATUS = "KNX...Acquiring KNX Sensors data..."
            self.getSensorValues()
            LOG_KNX_SENSORS_CSV.info(json.dumps(self.g_DATA.SENSORS))
            ActivityData().KNXSensorsActive()
            
            self.getBlindPos()
            LOG_KNX_BLINDS_CSV.info(json.dumps(self.g_DATA.BLINDS))
            ActivityData().KNXBlindsActive()

#            LOG_KNX_BLINDS_CSV.info('{},{},{},{}'.format(\
#                                    self.g_DATA.BLINDS['b0_Ang']['value'],\
#                                    self.g_DATA.BLINDS['b1_Ang']['value'],\
#                                    self.g_DATA.BLINDS['b0_Pos']['value'],\
#                                    self.g_DATA.BLINDS['b1_Pos']['value']))
                                    
 #           LOG_KNX_BLINDS.info('b0_Ang: {0:<10} b1_Ang: {1:<8} b0_Pos: {2:<8}
 #           b1_Pos:
 #           {3:<8}'.format(self.g_DATA.BLINDS['b0_Ang']['value'],self.g_DATA.BLINDS['b1_Ang']['value'],
 #           self.g_DATA.BLINDS['b0_Pos']['value'] ,
 #           self.g_DATA.BLINDS['b1_Pos']['value']))
             
        except Exception as e:
            exc_type, exc_value, exc_tb = sys.exc_info()
            tb=traceback.format_exception(exc_type, exc_value, exc_tb)   
            EmailError().emailMe("error in refreshing data... \n {}".format(tb))
            raise e

    def getSensorValues(self):

        sensorErrors = list()
        errorCount = 0
        print("get sensor data...")
        try:
            for key in self.g_DATA.SENSORS:
                if 'KNX' not in self.g_DATA.SENSORS[key]['sensortype']:
                    continue
                if  'isPassive' in self.g_DATA.SENSORS[key]['flags']:
                    continue
                if  'inactive' in self.g_DATA.SENSORS[key]['flags']:
                    self.g_DATA.SENSORS[key]['value'] = random.randrange(0,2)
                    continue           
                if  'disabled' in self.g_DATA.SENSORS[key]['flags']:
                    if  'useRange' in self.g_DATA.SENSORS[key]['flags']:
                        self.g_DATA.SENSORS[key]['value'] = random.randrange(self.g_DATA.SENSORS[key]['range'][0],self.g_DATA.SENSORS[key]['range'][1])
                    continue
    
                try:
                    value, error = self.getValueByName(key)
                except:
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    tb=traceback.format_exception(exc_type, exc_value, exc_tb)                      
                    LOG_KNX_SENSORS.error(tb)
                    continue
                
                if str(error).lower() == "error": 
                
                    errorCount+=1
                    self.g_DATA.SENSORS[key]['value'] = "-999"
                    self.g_DATA.SENSORS[key]['error'] = "error"
                    sensorErrors.append(str(key))
                else:
                    self.g_DATA.SENSORS[key]['value'] = str(value)[:5]
                    self.g_DATA.SENSORS[key]['error'] = "OK"
                    
            return self.g_DATA.SENSORS

            
        except Exception as e:        
            exc_type, exc_value, exc_tb = sys.exc_info()
            tb=traceback.format_exception(exc_type, exc_value, exc_tb)   
            EmailError().emailMe('error getting sensor data: {}'.format(tb))
            raise e
            
    def getBlindPos(self):
        blindsErrors = list()
        errorCount = 0
        for key in self.g_DATA.BLINDS:
            if "True" in self.g_DATA.BLINDS[key]['disabled']:
                continue
            
            values = self.getValueByName(key)
            self.g_DATA.BLINDS[key]['value'] = float(str(values[0])[:5])
            self.g_DATA.BLINDS[key]['error'] = str(values[1])
            
            if "error" in values[1]:
                errorCount+=1
                blindsErrors.append(str(key))
        
        
        if errorCount != 0:
            error = EmailError()
            error.emailMe("{} error(s) in reading blind positions".format(errorCount))
 
    def getValueByName(self,groupName):
        error = ''
        tempData = KNXReader(name= groupName)
        try:
            curVal,error = tempData.ReadValue()
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            tb=traceback.format_exception(exc_type, exc_value, exc_tb)                      
            LOG_KNX_SENSORS.error("error for value: {}".format(groupName))
            LOG_KNX_SENSORS.error(tb)
        return curVal, error

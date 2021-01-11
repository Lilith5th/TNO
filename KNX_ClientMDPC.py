import threading
import os          
import sys                      
import json 
import requests 
import time
import subprocess
import logging
import random
from DATA_KNXAdresses import GAD_MAP_TABLE_OUTSIDE
from datetime import datetime

from LKNX.LKNX_Singleton import Singleton
from LKNX.LKNX_ProjectSettings import ProjectSettings
from LKNX.LKNX_ReadWriteValue import KNXReader, KNXWriter

from VBUSClass import KNXVbusMonitor
from KIPPClass import KippZonen
from KNXClass import KNX
from DATA_CurrentValues import currentValues
from ActivityData import ActivityData
from EmailNotice import EmailError
from PeriodicCamera import PeriodicCamera

import traceback




            
            #self.JSONDATA = {
            #    'time': datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            #    'status':str(self.STATUS),
            #    'UI': {'UI_Pos': self.UIControls['UI_Pos']['value'],
            #                'UI_Ang': self.UIControls['UI_Ang']['value']},
            #    'sensor_values':{
            #        'radiationSky':int(float(self.SENSORS['radiationSky']['value'])),
            #        'indoorLight':0,#RADIATION INDOOR
            #        'radiationIndoor':float(self.SENSORS['radiationIndoor']['value']),
            #        'radiationFacade':int(float(self.SENSORS['radiationFacade']['value'])),
            #        'indoorTemp': float(self.SENSORS['indoorTemp']['value']),
            #        'INTEXT': float(self.SENSORS['INTEXT']['value']),
            #         #'Presence': self.SENSORS['Presence']['value'], #BUGGY
            #         #0/2/3
            #         #'sunOnFacade': float(self.SENSORS['INTEXT']['value']),
            #         #'externalTemp':float(self.SENSORS['externalTemp']['value']),

            #        'SunAzimuth':self.SENSORS['SunAzimuth']['value'],
            #        'SunAltitude':self.SENSORS['SunAltitude']['value']
            #        },
            #         'get_controls':{
            #                         'b0_Pos':self.BLINDS['b0_Pos']['value'],
            #                         'b1_Pos':self.BLINDS['b1_Pos']['value'],
            #                         'b0_Ang':self.BLINDS['b0_Ang']['value'] *
            #                         0.9,
            #                         'b1_Ang':self.BLINDS['b1_Ang']['value'] *
            #                         0.9,
            #                         'preferred_blind':self.PREFERRED_BLIND
            #                         }
            #    }


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
      
    #screen_handler = logging.StreamHandler(stream=sys.stdout)
    #screen_handler.setFormatter(formatter)
     
    #logging.basicConfig(level=logging.DEBUG,)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    #logger.addHandler(screen_handler)
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
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    #logger.addHandler(screen_handler)
    return logger 

LOG_MAIN= setup_logger('MAIN')
LOG_KIPP = setup_logger('Kipp')
LOG_VBUS = setup_logger('Vbus')
LOG_ERRROR = setup_logger('Error')


LOG_KNX_BLINDS = setup_logger('Blinds')

LOG_SENT_RECIEVED = setup_logger('Sent_Recieved')
LOG_KNX_SENSORS_CSV = setup_CSV_logger('CSV_SENSORS')#NOT USED
LOG_KNX_BLINDS_CSV = setup_CSV_logger('CSV_BLINDS')#NOT USED

#
##use g_XXX prefix for singleton instances (global data storrage)
#class currentValues(metaclass=Singleton):
#    curTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
#    STATUS_KIPP = ""
#    STATUS_SENSORS_KNX = ""
#    STATUS_SENSORS_PASSIVE = ""
#    STATUS_BLINDS = ""
#    STATUS = str("{} {} {} {}".format(STATUS_KIPP,STATUS_SENSORS_KNX,STATUS_SENSORS_PASSIVE,STATUS_BLINDS))
#    
#    ID= str(uuid.uuid1())[:5]
#    
#    GAD_TABLE = None
#    
#    SENSORS = dict(radiationSky = dict(sensortype='Pyra',value=-800, error='',flags="", valType='float') ,
#        radiationIndoor = dict(sensortype='Pyra',value=-800, error='',flags="", valType='float') ,
#        radiationFacade = dict(sensortype='Pyra',value=-800, error='',flags="", valType='float'),
#        externalTemp = dict(sensortype='KNX',value=-800, error='',flags="", valType='float'),
#        indoorTemp = dict(sensortype='KNX',value=-800, error='',flags="", valType='float'),
#        Presence = dict(sensortype='KNX',range=[0,2],value=0, error='not initialized',flags='disabled, useRange, placeholderValue', valType='int'),
#
#        Heating = dict(sensortype='KNX',value=-800, error='',flags='isPassive', valType='float'),        
#        sunOnFacade = dict(sensortype='KNX',value=-800, error='',flags='isPassive', valType='float'),
#        SunAzimuth = dict(sensortype = "KNX",value = -800, error='',flags="", valType='float'),
#        SunAltitude = dict(sensortype = "KNX",value = -800, error='',flags="", valType='float'))
#
#    BLINDS = dict(b0_Pos = dict(value=0,error='not initialized', disabled="False"),
#              b1_Pos = dict(value=0,error='not initialized', disabled="False"),
#              b0_Ang = dict(value=0,error='not initialized', disabled="False"), 
#              b1_Ang = dict(value=0,error='not initialized', disabled="False"))
#
#    UIControls = dict(UI_Pos= dict(value =-800,error = ''),
#        UI_Ang= dict(value = -800,error = ''))
#    PREFERRED_BLIND = 0
#
#
#    JSONDATA = {'time': curTime, 
#                 'status':STATUS,
#                 'UI': {'UI_Pos': UIControls['UI_Pos']['value'], 
#                        'UI_Ang': UIControls['UI_Ang']['value']}, 
#                 
#                 'sensor_values':{'radiationSky':   SENSORS['radiationSky']['value'],
#                                  'indoorLight':0,#RADIATION INDOOR
#                                  'radiationIndoor':SENSORS['radiationIndoor']['value'],#RADIATION INDOOR
#                                  'radiationFacade':SENSORS['radiationFacade']['value'],
#                                  'indoorTemp':     SENSORS['indoorTemp']['value'], 
#                                  'externalTemp':   SENSORS['externalTemp']['value'], 
#                                  'Presence': 0,
#                                  #SENSORS['Presence']['value'],#BUGGY 0/2/3
#                                  'Heating':        SENSORS['Heating']['value'],
#                                  'sunOnFacade':    SENSORS['sunOnFacade']['value'],
#                                  'SunAzimuth':     SENSORS['SunAzimuth']['value'], 
#                                  'SunAltitude':   SENSORS['SunAltitude']['value'] 
#                                  }, 
#                 
#                 'get_controls':{
#                                 'b0_Pos':BLINDS['b0_Pos']['value'],
#                                 'b1_Pos':BLINDS['b1_Pos']['value'],
#                                 'b0_Ang':BLINDS['b0_Ang']['value'] * 0.9, 
#                                 'b1_Ang':BLINDS['b1_Ang']['value'] * 0.9,
#                                 'preferred_blind':PREFERRED_BLIND
#                                 }
#                 } 
#
#    def __init__(self, *args, **kwargs):
#        pass
#
#    def getUpdatedValues(self):
#        KNX().refreshKNXData()
#         
#        try:
#            time = {'time': datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
#            status = {'status':str(self.STATUS)}
#            ui = {'UI': {'UI_Pos': self.UIControls['UI_Pos']['value'], 
#                         'UI_Ang': self.UIControls['UI_Ang']['value']}}
#
#            sensors = {}
#
#            for key in self.SENSORS:
#                sensors[key] = self.SENSORS[key]['value']
#
#
#            blinds = {}
#            for key in self.BLINDS:
#                multiplier = 1
#                if 'Ang' in key:
#                    multiplier = 0.9
#                blinds[key] = float(self.BLINDS[key]['value']) * multiplier
#                #blinds['blinds_type']='float'
#            blinds['preferred_blind'] = self.PREFERRED_BLIND 
#                
#            tempData = {}
#            tempData.update(time) 
#            tempData.update(ui) 
#            tempData.update(status) 
#            tempData.update({'sensor_values':sensors}) 
#            tempData.update({'get_controls':blinds}) 
#            self.JSONDATA = tempData
#            return self.JSONDATA
#
#        except Exception as e:
#            print(e)
#            print("KNX getUpdatedValues... error getting updated values.{}".format(e))
#            #raise Exception 
#
#    def updateKippZonenData(self,radiationSky,radiationIndoor,radiationFacade):
#            self.SENSORS['radiationSky']['value'] = radiationSky
#            self.SENSORS['radiationIndoor']['value'] = radiationIndoor
#            self.SENSORS['radiationFacade']['value'] = radiationFacade
#
#    def getSunPosData(self):
#        # in case quadra not functioning
#        import pytz
#
#        tz = pytz.timezone('Europe/Berlin')
#        date = datetime.now(tz)
#
#        latitude_deg = 51.05667 # positive in the northern hemisphere (Drongen 51.05)
#        longitude_deg = 3.66410 # negative reckoning west from prime meridian in Greenwich, England (Drongen
#                                # 3.66)
#
#        from pysolar.solar import get_position
#        from pysolar.radiation import get_radiation_direct   
#        sun_azimuth, sun_altitude = get_position(latitude_deg, longitude_deg, date,elevation=4)
#        expectedRad = get_radiation_direct(date, latitude_deg)
#        return sun_azimuth, sun_altitude 


#
#class KippZonen(threading.Thread):
#    '''
#    listens to KippZonen log box
#    '''
#    SERIAL_PORT = '/dev/ttyUSB0'
#    SERIAL_BAUD = 115200
#    running = False
#    restartCounter = 0
#    
#    def __init__(self,*args, **kwargs):
#        threading.Thread.__init__(self)
#        self.setDaemon(False)
#        for key in ('SERIAL_PORT','SERIAL_BAUD'):
#            if key in kwargs:
#                setattr(self, key, kwargs[key])
#
#    def run(self) :
#        print('starting kipp zonen data gathering')
#        while True:
#            LOG_MAIN.info("KIPP WHILE LOOP RUNNING")
#            try:
#                self.running = True
#                g_DATA = currentValues()
#                self.serialConnection = serial.Serial(self.SERIAL_PORT, self.SERIAL_BAUD,  timeout=30)           #, timeout=30
#                curLine = self.serialConnection.readline()
#                curLineStr = str(curLine , 'utf-8')                
#
#                if "W:" in curLineStr :
#                    curValues = curLineStr.split()
#                    if  len(curValues) == 16:
#                        LOG_KIPP.info(curLineStr)
#                        g_DATA.updateKippZonenData(curValues[2], curValues[3], curValues[4])
#                        g_DATA.STATUS_KIPP = "OK"
#                        print('STATUS: Kipp Zonnen - OK')
#                ActivityData().KIPPActive()
#
#            except Exception as e:
#                g_DATA = currentValues()
#                g_DATA.STATUS_KIPP = "error acquiring pyranometer values. Service will be restarted".format(self.restartCounter)
#                self.running = False
#                print(e)
#                if self.restartCounter < 10:
#                    time.sleep(60)
#                    self.restartCounter = self.restartCounter + 1
#                else:
#                    error = EmailError()
#                    error.emailMe("error in serial port data listening... tried restarting 10x...shutting it down. \n {}".format(e))
#                    raise Exception(e)
#                                  
#class KNX(object):
#    errors = list()
#    def __init__(self):
#        self.g_DATA = currentValues()
#
#    def refreshKNXData(self):
#        try:
#
#            print("KNX...acquiring sensor data...")
#            self.errors = list()
#
#            self.g_DATA.STATUS = "KNX...Acquiring KNX Sensors data..."
#            self.getSensorValues()
#
#
##            LOG_KNX_SENSORS_CSV.info("{},{},{},{},pressencePlaceholder".format(str(self.g_DATA.SENSORS['SunAzimuth']['value'])[:4],
##                                        str(self.g_DATA.SENSORS['SunAltitude']['value'])[:4], 
##                                        str(self.g_DATA.SENSORS['externalTemp']['value'])[:4],
##                                        str(self.g_DATA.SENSORS['indoorTemp']['value'])[:4] 
##                                        #str(self.g_DATA.SENSORS['Presence']['value'])[:4]
##                                        ))
##            LOG_KNX_SENSORS.info('externalTemp: {0:<10} \
##                                 indoorTemp: {1:<8} \
##                                 Presence: {2:<8}'\
##                                        .format(str(self.g_DATA.SENSORS['externalTemp']['value'])[:4],\
##                                        str(self.g_DATA.SENSORS['indoorTemp']['value'])[:4],
##                                        \
##                                        self.g_DATA.SENSORS['Presence']['value']))
#            print ('getting blinds')
#            self.getBlindPos()
#            self.g_DATA.STATUS = "ok"
##            LOG_KNX_BLINDS_CSV.info('{},{},{},{}'.format(\
##                                    self.g_DATA.BLINDS['b0_Ang']['value'],\
##                                    self.g_DATA.BLINDS['b1_Ang']['value'],\
##                                    self.g_DATA.BLINDS['b0_Pos']['value'],\
##                                    self.g_DATA.BLINDS['b1_Pos']['value']))
#                                    
# #           LOG_KNX_BLINDS.info('b0_Ang: {0:<10} b1_Ang: {1:<8} b0_Pos: {2:<8}
# #           b1_Pos:
# #           {3:<8}'.format(self.g_DATA.BLINDS['b0_Ang']['value'],self.g_DATA.BLINDS['b1_Ang']['value'],
# #           self.g_DATA.BLINDS['b0_Pos']['value'] ,
# #           self.g_DATA.BLINDS['b1_Pos']['value']))
#             
#            ActivityData().KNXActive()
#
#        except Exception as e:
#            error = EmailError()
#            print("KNX error".format(e))
#            error.emailMe("error in refreshing data... \n {}".format(e))
#            raise Exception
#
#    #RUN FUNCTIONS
#    def getSensorValues(self):
#
#        sensorErrors = list()
#        errorCount = 0
#        print("get sensor data...")
#        try:
#            for key in self.g_DATA.SENSORS:
#                if 'KNX' not in self.g_DATA.SENSORS[key]['sensortype']:
#                    continue
#                if  'isPassive' in self.g_DATA.SENSORS[key]['flags']:
#                    continue
#                if  'inactive' in self.g_DATA.SENSORS[key]['flags']:
#                    self.g_DATA.SENSORS[key]['value'] = random.randrange(0,2)
#                    continue           
#                if  'disabled' in self.g_DATA.SENSORS[key]['flags']:
#                    if  'useRange' in self.g_DATA.SENSORS[key]['flags']:
#                        self.g_DATA.SENSORS[key]['value'] = random.randrange(self.g_DATA.SENSORS[key]['range'][0],self.g_DATA.SENSORS[key]['range'][1])
#                        #sensorErrors.append("presence sensor is using random values for testing purposes. Device not functioning")
#                    continue
#    
#                try:
#                    value, error = self.getValueByName(key)
#                except:
#                    print("getsensorval error...")
#                    continue
#                if str(error).lower() == "error": 
#                
#                    errorCount+=1
#                    self.g_DATA.SENSORS[key]['value'] = "-999"
#                    self.g_DATA.SENSORS[key]['error'] = "error"
#                    sensorErrors.append(str(key))
#                else:
#                    self.g_DATA.SENSORS[key]['value'] = str(value)[:5]
#                    self.g_DATA.SENSORS[key]['error'] = "OK"
#
#            #self.g_DATA.STATUS_SENSORS_KNX =  sensorErrors.__str__    #TODO STARTED UPDATING
#            #self.g_DATA.SENSORS['sensor_error']= self.g_DATA.STATUS_SENSORS_KNX
#            print ('got sensor values')
#
#            
#        except Exception as e:
#            print ('error getting sensor data: {}'.format(e))
#           
#           
#
#    def getBlindPos(self):
#        blindsErrors = list()
#        errorCount = 0
#        for key in self.g_DATA.BLINDS:
#            if "True" in self.g_DATA.BLINDS[key]['disabled']:
#                continue
#            
#            values = self.getValueByName(key)
#            self.g_DATA.BLINDS[key]['value'] = float(str(values[0])[:5])
#            self.g_DATA.BLINDS[key]['error'] = str(values[1])
#            
#            if "error" in values[1]:
#                errorCount+=1
#                blindsErrors.append(str(key))
#        
#        self.g_DATA.STATUS_BLINDS = blindsErrors.__str__    #TODO STARTED UPDATING                    
#        if errorCount != 0:
#            error = EmailError()
#            error.emailMe("{} error(s) in reading blind positions".format(errorCount))
# 
#
#    def getValueByName(self,groupName):
#        error = ''
#        tempData = KNXReader(name= groupName)
#        curVal,error = tempData.ReadValue()
#        return curVal, error


#
#class KNXVbusMonitor(threading.Thread):
#    running = False
#    restartCounter = 0
#    restartScript=False
#    def __init__(self, *args, **kwargs):
#        print("vbusmonitor init")
#        threading.Thread.__init__(self)
#        self.setDaemon(False)
#        self.g_DATA = currentValues()
#
#    def run(self):
#        try:
#            self.running = True
#            popen = subprocess.Popen('knxtool vbusmonitor1 local:',shell=True, stdout=subprocess.PIPE,stderr =subprocess.PIPE, universal_newlines=True)
#            for stdout_line in iter(popen.stdout.readline, ''):
#
#                LOG_MAIN.info("VBUS MONITOR RUNNING")
#                try:
#                    self.process_stdoutCommand(stdout_line)
#                    self.g_DATA.STATUS_KNX_SENSORS_PASSIVE = "OK"
#                    ActivityData().VBUSActive()
#                    
#                except Exception as e:
#                    exc_type, exc_value, exc_tb = sys.exc_info()
#                    tb=traceback.format_exception(exc_type, exc_value, exc_tb)
#                    LOG_ERRROR.error('error in subprocess popen stdout_line {} errorr: {} trackback:{}'.format(stdout_line,e,tb))
#  
#
#        except Exception as e:
#            exc_type, exc_value, exc_tb = sys.exc_info()
#            tb=traceback.format_exception(exc_type, exc_value, exc_tb)
#            LOG_ERRROR.error('vbusError:{}, \nerror: {} tb:{}'.format(stdout_line,e,tb))
#            LOG_VBUS.error("           !!!VBUS MONITOR ERROR!!!")
#            self.g_DATA.STATUS_KNX_SENSORS_PASSIVE = "error acquiring passive KNX values. Service will be restarted".format(self.restartCounter)
#            self.running = False
#            print("ERROR: vbusError: {}".format(e))
#            if self.restartCounter < 10:
#                time.sleep(60)
#                self.restartCounter = self.restartCounter + 1
#                self.run()
#            else:
#                self.restartScript=True
#                error = EmailError()
#                error.emailMe("error in vbusmonitor run... tried restarting 10x...shutting it down. \n {}".format(e))
#                raise Exception(e)
#
#    def process_stdoutCommand(self, stdout_line):
#        try:
#            from LKNX.LKNX_stdoutData import stdoutData 
#            recievedStdout= None
#            try:     
#                recievedStdout = stdoutData(stdout_line)
#            except:
#                print ('exception in processing stdoutCommand')
#                return
#        
#            if "inactive" in recievedStdout.flagsString.lower():
#                return
#            if "ispassive" not in recievedStdout.flagsString.lower():
#                return
#
#            temp = self.g_DATA.SENSORS[recievedStdout.name]
#            temp.update({"value" : str(recievedStdout.value)})
#            self.g_DATA.SENSORS.update({recievedStdout.name:temp})
#            
#        except Exception as e:
#            exc_type, exc_value, exc_tb = sys.exc_info()
#            tb=traceback.format_exception(exc_type, exc_value, exc_tb)
#            LOG_ERRROR.error('processing stdoutCommand stdout:{}, \nerror: {} \ntraceback:{}'.format(stdout_line,e,tb))
#            print('ERROR: processing stdoutCommand {}'.format(tb))
#            



class ConnectToServer(threading.Thread):
    g_SETTINGS = ProjectSettings()
    g_DATA = currentValues()

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self)
        self.setDaemon(False)
        print('INFO: connecting to server...')
 
    def run(self):
        runStartedTime = datetime.now().strftime("%m_%d-%H_%M_%S")
        runCounter=0;
        firstRun = True
        locaJSONData = dict()
        waitTime = 300
        print ("starting while loop...")
        while True:            
            LOG_MAIN.info("MAIN CLIENT-SERVER LOOP RUNNING")
            runCounter=runCounter+1
            print ("connecting to server for the {}x time\run started on:{}".format(runCounter, runStartedTime))            
            try:
                KNX().refreshKNXData()
                ActivityData().refreshData() 
                
                print("while loop... get updated values...")
                print (self.g_DATA)
                localJSONData = self.g_DATA.getUpdatedValues() 
                print("LocalJsonData:",
                        json.dumps(localJSONData, sort_keys=True, indent=4))

                time.sleep(5)
                
#                continue
#                if runCounter==1:#we do this to prevent 800 values at the start
#                    time.sleep(waitTime)
#                    continue

                server_BlindsData = self.getServerData(localJSONData)
                print("ServerJsonData:",
                        json.dumps(server_BlindsData, sort_keys=True, indent=4))
                
                if "error" in server_BlindsData or "error" in localJSONData:
                    time.sleep(waitTime)
                    continue
                    
                time.sleep(5)
                
                print ('comparing and moving blinds...')
                self.compareAndupdatePhysicalBlindsPosition(server_BlindsData,localJSONData)
                ActivityData().ServerActive()
                time.sleep(5)
                
                print("waiting 300 seconds to send new data to server...")
                time.sleep(waitTime)
                
            except Exception as e:
                exc_type, exc_value, exc_tb = sys.exc_info()
                tb=traceback.format_exception(exc_type, exc_value, exc_tb)  
                LOG_MAIN.error(tb)
                print("error ... waiting 300 seconds to try send new data to server...\n{}".format(e))
                #emailNotice = EmailError()
                #emailNotice.emailMe(e)
                #time.sleep(waitTime)
                raise e
            

    def getServerData(self,current_blinds_values):
        error = False
        errorList = list()
        try:
            r = requests.post(self.g_SETTINGS.ServerIP + '/MBPC/b', timeout=50, json=current_blinds_values)
            server_blinds_values = r.json()
            LOG_SENT_RECIEVED.info(current_blinds_values)
            LOG_SENT_RECIEVED.info(server_blinds_values)

            if 'error' in server_blinds_values['status']:
                return server_blinds_values
            else:
                return server_blinds_values
        except Exception as e:
            error = EmailError()
            error.emailMe(e)
            print("error getting server data")
            return "error"

    def compareAndupdatePhysicalBlindsPosition(self, server_blinds_values, current_JSON):
        from LKNX.LKNX_ReadWriteValue import KNXWriter
        current_blinds_values = current_JSON['get_controls']

        
        if server_blinds_values['status'] == 'ok':
            preferred_blind = server_blinds_values['preferred_blind']
            
            #WRITE TO PREFERED GROUP
            for group_name in server_blinds_values:
                if any (val in group_name for val in  ['status','time','preferred_blind'] ) :
                    continue
                   
                if str(preferred_blind) in group_name:
                    curBlindPos = current_blinds_values[group_name]
                    requestedBlindPos = server_blinds_values[group_name] 

                    #move prefered blind if change is beyond "threshold" (no point moving it 1%)
                    if abs(curBlindPos - requestedBlindPos) > 3:
                        print("move blind...curBlindPos = {} requestedBlindPos = {}".format(curBlindPos,requestedBlindPos))                        
                        print("move blind...moving group: {} value: {}".format(group_name, requestedBlindPos))
                        KNXWriter(name = group_name, value =requestedBlindPos)
                        print('move blind...WRITE COMPLETE')
                        #TODO CREATE DERIVED THREADED CLASS FROM KNXWRITER THAT PERFORMS CHECK AFTER 2 MINUTES
                else:
                    #move non preffered blind to default position
                    print('move non preffered blind to default position...')
                    KNXWriter(name = group_name, value =0)
            
            #DISABLED. Store previous data for any future comparison
            #self.old_blinds_values = server_blinds_values

        else:
            error = EmailError()
            error.emailMe("move blind...error with parsing blinds values")
            print('move blind...server status not OK')
            time.sleep(25)
            pass


class ActivityCheck(threading.Thread):
    def __init__(self,*args, **kwargs):
        print("starting")
        self.ActivityData= ActivityData()
        print ("started")
        threading.Thread.__init__(self)
        self.setDaemon(False)

        
    def run(self):
        while True:
            time.sleep(5)
            self.ActivityData.check()
            continue


class StartInfo:
    g_SETTINGS = ProjectSettings()
    g_DATA = currentValues()
    def __init__(self,  *args, **kwargs):
        pass
        
    def SendInfo(self):
        try:
            print ("sending start info")
            info = {'time': datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), 
                     'status':"STARTING NEW SESSION.", 'ID': self.g_DATA.ID}
            print ("sending start info {} ".format(info))
            r = requests.post(self.g_SETTINGS.ServerIP + '/MBPC/b', timeout=10, json=info)     
            response = r.json()
            print (info)
            print (response)
        except Exception as e:
            print (e)



''' experiments '''
if __name__ == "__main__2":
    kipLogger = KippZonen()
    connection = ConnectToServer()
    while True:
        running = False
        try:
            if running == False:
                settings = ProjectSettings()
                settings.GAD_TABLE = GAD_MAP_TABLE_OUTSIDE
                settings.ServerIP = "http://90.145.162.7:8109"#"http://90.145.162.7:8109"
                startLogging()
                kipLogger.start()
                connection.start()
                running = True
    
        except Exception as e:
            emailNotice = EmailError()
            emailNotice.emailMe(e)
            connection.join()
            kipLogger.join()
            running = False 

class bc:
    def __init__(self, b="bla"):
        self.a = b
class cc(bc):
    def __init__(self, b="oo", *args,**kwargs):
        super().__init__(b)
        print(self.a)
        print(kwargs["test"])
class dd(cc):
    def __init__(self, b,*args,**kwargs):
        super().__init__(b,test="now")
        print(self.a)
        

def testing():
        ActivityCheck().start()
        settings = ProjectSettings()
        settings.GAD_TABLE = GAD_MAP_TABLE_OUTSIDE
        KNXWriter(name='b0_Set_Pos', value=str(random.randint(0,100)))
        time.sleep(12)   
        tempData = KNXReader(name= "externalTemp")
        val = tempData.ReadValue()
        print(val)
        time.sleep(12)        
        KNXWriter(name='b0_Set_Pos', value='50')

def main():
    ActivityCheck().start()
    
    StartInfo().SendInfo()
    
    '''start logging KippZonen data'''
    KippZonen().start()
    '''
    start logging KNX data
    start connection to MDBPC server
    '''
    KNXVbusMonitor().start()

    #PeriodicCamera().start()

    ConnectToServer().start()

def goodbye():
    activeTime =ActivityData().ServerTime.total_seconds() 
    
    hours = activeTime // 3600
    minutes = (seconds % 3600) // 60
    if hours>23 and minutes >50 or hours>24 :
        LOG_MAIN.info("SCHEDUELED RESTART HAPPENING")
        EmailError().emailMe("Scheudled shutting down. Duration: {}".format(activeTime))
        return
    LOG_MAIN.error("script exiting... for reasons unknown")
    EmailError().emailMe("script exiting... for reasons unknown - duration: {}".format(activeTime))

import atexit
atexit.register(goodbye)

if __name__ == "__main__":
    print(os.getpid(), file=open("/home/pi/cron/PID_KNXTNO.pid", "w"))
    try:
        settings = ProjectSettings()
        settings.GAD_TABLE = GAD_MAP_TABLE_OUTSIDE    
        settings.ServerIP = "http://90.145.162.7:8109"#"http://90.145.162.7:8109"
        g_DATA = currentValues()
        g_DATA.GAD_TABLE = GAD_MAP_TABLE_OUTSIDE
        startLogging()
        
        main()
    
    except Exception as e:
        emailNotice = EmailError()
        emailNotice.emailMe(e)
        quit ()
        


      

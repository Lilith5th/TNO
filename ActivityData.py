from LKNX.LKNX_Singleton import Singleton
from DATA_CurrentValues import currentValues
from datetime import datetime
from datetime import timedelta
import sys
import os
import logging

#if not os.path.exists(log_dir):
#    os.makedirs("Logs")
#if not os.path.exists(log_dir_all):
#    os.makedirs(os.path.join(log_dir,"All"))

#from pyknyx.services.logger import logging; logger =
#logging.getLogger(__name__)
#def startLogging():
#    for handler in logging.root.handlers[:]:
#        logging.root.removeHandler(handler)
#
#    curFilename = os.path.join(log_dir_all , ("{}all_events.log".format(datetime.now().strftime("%Y_%m_%d"))))
#    logging.basicConfig(filename=curFilename, filemode='a', 
#        format='%(asctime)s %(levelname)-8s %(message)s',
#        level=logging.INFO,
#        datefmt='%Y-%m-%d %H:%M:%S')

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


LOG_ACTIVITY= setup_logger('Activity')




class ActivityData(metaclass=Singleton):
    StartTime=datetime.now()     
    KIPPTime=datetime.now() 
    VBUSTime=datetime.now() 
    KNXTime=datetime.now() 
    KNXSensorsTime=datetime.now()     
    KNXBlindsTime=datetime.now()     
        
    ServerTime=datetime.now() 
    threshold=350
    g_DATA= currentValues()
    
    def __init__(self, *args, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
        return super().__init__(*args, **kwargs) 
    
    def refreshData(self):
        self.runTime=str(timedelta(seconds=(datetime.now()   -self.StartTime).total_seconds() ))
        self.deltaVBUS=(datetime.now()   -self.VBUSTime).total_seconds()
        self.deltaKNX =(datetime.now()   -self.KNXTime).total_seconds()
        self.deltaKNXSensors =(datetime.now()   -self.KNXSensorsTime).total_seconds()       
        self.deltaBlinds  =(datetime.now()   -self.KNXBlindsTime).total_seconds()   
        
        self.deltaKIPP=(datetime.now()   -self.KIPPTime).total_seconds()
        self.deltaServer=(datetime.now()   -self.ServerTime).total_seconds() 
        
        print ("runTime {}".format(self.runTime))
        print ("deltaVBUS {}".format(self.deltaVBUS))
        print ("deltaKNXSensors {}".format(self.deltaKNXSensors))  
        print ("deltaKNXBlinds {}".format(self.deltaBlinds))          
        print ("deltaKIPP {}".format(self.deltaKIPP))    
        print ("deltaServer {}".format(self.deltaServer)) 
        
        self.g_DATA.STATUS_KIPP = str("Kipp zonen sensors updated {}s ago".format(self.deltaKIPP))
        self.g_DATA.STATUS_SENSORS_KNX = str("KNX sensors updated {}s ago".format(max(self.deltaKNXSensors,self.deltaVBUS)))
        self.g_DATA.STATUS_BLINDS = str("KNX blind positions updated {}s ago".format(self.deltaBlinds))
        self.g_DATA.STATUS_SERVER = str("Last server data:{}s ago".format(self.deltaServer))
        self.g_DATA.STATUS = str("OK")
        LOG_ACTIVITY.info  ("runTime {}".format(self.runTime))
                
    def check(self):
        timeNow=datetime.now().strftime("%H:%M:%S")
        self.refreshData()
        print("{} - ...activity check running...".format(timeNow), file=open("/home/pi/cron/LOG_KNXTNO.log", "a"))
        if self.deltaKIPP >self.threshold or \
            self.deltaVBUS>self.threshold or \
            self.deltaKNX>self.threshold or \
            self.deltaServer> self.threshold:
            LOG_ACTIVITY.error("{} - hasta la vista... baby...\n\n".format(timeNow), file=open("/home/pi/cron/LOG_KNXTNO.log", "a"))
            sys.exit()   
            
    def KIPPActive(self):
        self.KIPPTime=datetime.now()            
    def VBUSActive(self):
        self.VBUSTime=datetime.now()   
    def KNXSensorsActive(self):
        self.KNXSensorsTime=datetime.now()  
    def KNXBlindsActive(self):
        self.KNXBlindsTime=datetime.now()  
        
    def KNXActive(self):
        self.KNXTime=datetime.now()         
    def ServerActive (self):
        self.ServerTime=datetime.now()  
        
        
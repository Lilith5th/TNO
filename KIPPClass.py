import threading
import os          
import serial
import time
import logging
from DATA_CurrentValues import currentValues
from EmailNotice import EmailError
from ActivityData import ActivityData

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

LOG_KIPP = setup_logger('Kipp')

class KippZonen(threading.Thread):
    '''
    listens to KippZonen log box
    '''
    SERIAL_PORT = '/dev/ttyUSB0'
    SERIAL_BAUD = 115200
    running = False
    restartCounter = 0
    
    def __init__(self,*args, **kwargs):
        threading.Thread.__init__(self)
        self.setDaemon(False)
        for key in ('SERIAL_PORT','SERIAL_BAUD'):
            if key in kwargs:
                setattr(self, key, kwargs[key])

    def run(self) :
        print('starting kipp zonen data gathering')
        while True:
            try:
                self.running = True
                g_DATA = currentValues()
                self.serialConnection = serial.Serial(self.SERIAL_PORT, self.SERIAL_BAUD,  timeout=30)           #, timeout=30
                curLine = self.serialConnection.readline()
                curLineStr = str(curLine , 'utf-8')                

                if "W:" in curLineStr :
                    curValues = curLineStr.split()
                    if  len(curValues) == 16:
                        LOG_KIPP.info(curLineStr)
                        g_DATA.updateKippZonenData(curValues[2], curValues[3], curValues[4])
                        #g_DATA.STATUS_KIPP = "OK"
                        ActivityData().KIPPActive()

            except Exception as e:
                g_DATA = currentValues()
                LOG_KIPP.error ("error acquiring pyranometer values. Service will be restarted".format(self.restartCounter) )                  
                g_DATA.STATUS_KIPP = "error acquiring pyranometer values. Service will be restarted".format(self.restartCounter)
                self.running = False
                print(e)
                if self.restartCounter < 10:
                    time.sleep(60)
                    self.restartCounter = self.restartCounter + 1
                else:                    
                    LOG_KIPP.error ("error in serial port data listening... tried restarting 10x...shutting it down. \n {}".format(e))
                    EmailError().emailMe("error in serial port data listening... tried restarting 10x...shutting it down. \n {}".format(e))
                    raise Exception(e)
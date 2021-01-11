from datetime import datetime
from LKNX.LKNX_Singleton import Singleton
from EmailNotice import EmailError
import uuid 


#use g_XXX prefix for singleton instances (global data storrage)
class currentValues(metaclass=Singleton):
    curTime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    STATUS_KIPP = ""
    STATUS_SENSORS_KNX = ""
    STATUS_SENSORS_PASSIVE = ""#not needed
    STATUS_BLINDS= ""
    STATUS_SERVER = ""
    STATUS = str("{} {} {} {}".format(STATUS_KIPP,STATUS_SENSORS_KNX,STATUS_SENSORS_PASSIVE,STATUS_SERVER))
    
    ID= str(uuid.uuid1())[:5]
    
    GAD_TABLE = None
    
    SENSORS = dict(radiationSky = dict(sensortype='Pyra',value=-800, error='',flags="", valType='float') ,
        radiationIndoor = dict(sensortype='Pyra',value=-800, error='',flags="", valType='float') ,
        radiationFacade = dict(sensortype='Pyra',value=-800, error='',flags="", valType='float'),
        externalTemp = dict(sensortype='KNX',value=-800, error='',flags="", valType='float'),
        indoorTemp = dict(sensortype='KNX',value=-800, error='',flags="", valType='float'),
        Presence = dict(sensortype='KNX',range=[0,2],value=0, error='not initialized',flags='disabled, useRange, placeholderValue', valType='int'),

        Heating = dict(sensortype='KNX',value=-800, error='',flags='isPassive', valType='float'),        
        sunOnFacade = dict(sensortype='KNX',value=-800, error='',flags='isPassive', valType='float'),
        SunAzimuth = dict(sensortype = "KNX",value = -800, error='',flags="", valType='float'),
        SunAltitude = dict(sensortype = "KNX",value = -800, error='',flags="", valType='float'))

    BLINDS = dict(b0_Pos = dict(value=0,error='not initialized', disabled="False"),
              b1_Pos = dict(value=0,error='not initialized', disabled="False"),
              b0_Ang = dict(value=0,error='not initialized', disabled="False"), 
              b1_Ang = dict(value=0,error='not initialized', disabled="False"))

    UIControls = dict(UI_Pos= dict(value =-800,error = ''),
        UI_Ang= dict(value = -800,error = ''))
    PREFERRED_BLIND = 0


    JSONDATA = {'time': curTime, 
                 'status':STATUS,
                 'UI': {'UI_Pos': UIControls['UI_Pos']['value'], 
                        'UI_Ang': UIControls['UI_Ang']['value']}, 
                 
                 'sensor_values':{'radiationSky':   SENSORS['radiationSky']['value'],
                                  'indoorLight':0,#RADIATION INDOOR
                                  'radiationIndoor':SENSORS['radiationIndoor']['value'],#RADIATION INDOOR
                                  'radiationFacade':SENSORS['radiationFacade']['value'],
                                  'indoorTemp':     SENSORS['indoorTemp']['value'], 
                                  'externalTemp':   SENSORS['externalTemp']['value'], 
                                  'Presence': 0,
                                  #SENSORS['Presence']['value'],#BUGGY 0/2/3
                                  'Heating':        SENSORS['Heating']['value'],
                                  'sunOnFacade':    SENSORS['sunOnFacade']['value'],
                                  'SunAzimuth':     SENSORS['SunAzimuth']['value'], 
                                  'SunAltitude':   SENSORS['SunAltitude']['value'] 
                                  }, 
                 
                 'get_controls':{
                                 'b0_Pos':BLINDS['b0_Pos']['value'],
                                 'b1_Pos':BLINDS['b1_Pos']['value'],
                                 'b0_Ang':BLINDS['b0_Ang']['value'] * 0.9, 
                                 'b1_Ang':BLINDS['b1_Ang']['value'] * 0.9,
                                 'preferred_blind':PREFERRED_BLIND
                                 }
                 } 

    def __init__(self, *args, **kwargs):
        pass

    def getUpdatedValues(self):
        #KNX().refreshKNXData()

        try:
            time = {'time': datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
            status = {'status':str(self.STATUS)}
            statusDetails = {'session ID': self.ID,
                            'pyranometers':self.STATUS_KIPP ,
                             'KNX':self.STATUS_SENSORS_KNX,
                             'Blinds': self.STATUS_BLINDS ,
                             'SERVER':self.STATUS_SERVER}
            
            ui = {'UI': {'UI_Pos': self.UIControls['UI_Pos']['value'], 
                         'UI_Ang': self.UIControls['UI_Ang']['value']}}

            sensors = {}

            for key in self.SENSORS:
                sensors[key] = self.SENSORS[key]['value']


            blinds = {}
            for key in self.BLINDS:
                multiplier = 1
                if 'Ang' in key:
                    multiplier = 0.9
                blinds[key] = float(self.BLINDS[key]['value']) * multiplier
                #blinds['blinds_type']='float'
            blinds['preferred_blind'] = self.PREFERRED_BLIND 
                
            tempData = {}
            tempData.update(time) 
            tempData.update(ui) 
            tempData.update(status) 
            tempData.update({'status_details':statusDetails}) 
            tempData.update({'sensor_values':sensors}) 
            tempData.update({'get_controls':blinds}) 
            self.JSONDATA = tempData
            return self.JSONDATA

        except Exception as e:
            print(e)
            print("KNX getUpdatedValues... error getting updated values.{}".format(e))
            #raise Exception 

    def updateKippZonenData(self,radiationSky,radiationIndoor,radiationFacade):
            self.SENSORS['radiationSky']['value'] = radiationSky
            self.SENSORS['radiationIndoor']['value'] = radiationIndoor
            self.SENSORS['radiationFacade']['value'] = radiationFacade

    def getSunPosData(self):
        # in case quadra not functioning
        import pytz

        tz = pytz.timezone('Europe/Berlin')
        date = datetime.now(tz)

        latitude_deg = 51.05667 # positive in the northern hemisphere (Drongen 51.05)
        longitude_deg = 3.66410 # negative reckoning west from prime meridian in Greenwich, England (Drongen
                                # 3.66)

        from pysolar.solar import get_position
        from pysolar.radiation import get_radiation_direct   
        sun_azimuth, sun_altitude = get_position(latitude_deg, longitude_deg, date,elevation=4)
        expectedRad = get_radiation_direct(date, latitude_deg)
        return sun_azimuth, sun_altitude ,expectedRad

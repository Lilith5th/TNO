import random

myvar = [b'00',b'15',b'30',b'45',b'60',b'75',b'90']
def variable():
   return random.choice(myvar)

#OUTSIDE
GAD_MAP_TABLE_OUTSIDE = {
#OLD QUADRA    '0/1/8'  :  dict(typeOf='sensor', read_write='read', dptId='9.022', name='externalTemp', inOut = '', windowGroupName = '',flags='isPassiveSensor', value = 'N/A'),
#OLD QUADRA    '0/1/20' :  dict(typeOf='sensor', read_write='on', dptId='1.001', name='radiationSkyON', inOut = '', windowGroupName = '',flags='preCommand', value = ''),

    #'0/1/20' :  dict(typeOf='sensor', read_write='read', dptId='9.022', name='radiationSky', inOut = '', windowGroupName = '',flags='', value = 'N/A'),
    #'0/1/19' :  dict(typeOf='sensor', read_write='read', dptId='9.022', name='radiationSkyW', inOut = '', windowGroupName = '',flags='', value = 'N/A'),
    #'0/1/17' :  dict(typeOf='sensor', read_write='read', dptId='9.022', name='radiationSkyE', inOut = '', windowGroupName = '',flags='', value = 'N/A'),
    #'0/1/18' :  dict(typeOf='sensor', read_write='read', dptId='9.022', name='radiationSkyS', inOut = '', windowGroupName = '',flags='', value = 'N/A'),
    #'0/1/16' :  dict(typeOf='sensor', read_write='read', dptId='9.022', name='radiationSkyN', inOut = '', windowGroupName = '',flags='', value = 'N/A'),
    #'0/1/15' :  dict(typeOf='sensor', read_write='read', dptId='7.013', name='brightness', inOut = '', windowGroupName = '',flags='', value = 'N/A'), ##LX

    '0/7/1'  :  dict(typeOf='sensor', read_write='read', dptId='1.xxx', name='INTEXT', inOut = '', windowGroupName = '',flags='isUI', value = 'N/A'),
    '0/1/25'  :  dict(typeOf='sensor', read_write='read', dptId='1.xxx', name='sunOnFacade', inOut = '', windowGroupName = '',flags='isPassive', value = 'N/A'),
    '3/2/1'  :  dict(typeOf='sensor', read_write='read', dptId='1.xxx', name='Heating', inOut = '', windowGroupName = '',flags='isPassive', value = 'N/A'),
    '0/1/4'  :  dict(typeOf='sensor', read_write='read', dptId='8.011', name='SunAzimuth', inOut = '', windowGroupName = '',flags='', value = 'N/A'),
    '0/1/5'  :  dict(typeOf='sensor', read_write='read', dptId='8.011', name='SunAltitude', inOut = '', windowGroupName = '',flags='', value = 'N/A'),

    '0/1/8'  :  dict(typeOf='sensor', read_write='read', dptId='9.001', name='externalTemp', inOut = '', windowGroupName = '',flags='', value = 'N/A'),
    '0/2/2'  :  dict(typeOf = 'sensor', read_write = 'read', dptId = '9.001', name = 'indoorTemp', inOut='', windowGroupName='',flags='', value = 'N/A'),
    '0/2/3'  :  dict(typeOf='sensor', read_write='read', dptId='1.xxx', name='Presence', inOut='', windowGroupName='',flags='inactive', value = 'N/A'),#1.018
    '0/2/4'  :  dict(typeOf='sensor', read_write='read', dptId='7.013', name='indoorLight', inOut='', windowGroupName='',flags='', value = 'N/A'),#1.018

     #east
    #'1/0/1'  : dict(typeOf='b0', read_write='groupwrite', dptId='1.007', name='b0_Stop',   inOut='Blinds_inside',  windowGroupName='P1',flags='', value = 'N/A'),           ###ON OFF
    #'1/1/1'  :  dict(typeOf='b0', read_write='groupwrite', dptId='1.008', name='b0_Up_Down',inOut='Blinds_inside',  windowGroupName='P1',flags='', value = 'N/A'),         ###ON OFF
    '1/2/2'  :  dict(typeOf='b0', read_write='groupwrite', dptId='5.001', name='b0_Set_Pos',inOut='Blinds_inside',  windowGroupName='P1',flags='', value = 'N/A'),
    '1/3/2'  :  dict(typeOf='b0', read_write='groupwrite', dptId='5.001', name='b0_Set_Ang',  inOut='Blinds_inside',  windowGroupName='P1',flags='inactive', value = 'N/A'),
    '1/5/2'  :  dict(typeOf='b0', read_write='read', dptId='5.001', name='b0_Get_Pos',inOut='Blinds_inside',  windowGroupName='P1',flags=''),
    '1/6/2'  :  dict(typeOf='b0', read_write='read', dptId='5.001', name='b0_Get_Ang',  inOut='Blinds_inside',  windowGroupName='P1',flags='inactive', value = 'N/A'),
     #south
    #'1/0/2'  : dict(typeOf='b1', read_write='groupwrite', dptId='1.007', name='b1_Stop',   inOut='Blinds_outside',  windowGroupName='P1',flags='', value = 'N/A'),         ###ON OFF
    #'1/1/2'  :  dict(typeOf='b1', read_write='groupwrite', dptId='1.008', name='b1_Up_Down',inOut='Blinds_outside',  windowGroupName='P1',flags='', value = 'N/A'),        ###ON OFF
    '1/2/3'  :  dict(typeOf='b1', read_write='groupwrite', dptId='5.001', name='b1_Set_Pos',inOut='Blinds_outside', windowGroupName='P1',flags='', value = 'N/A'),
    '1/3/3'  :  dict(typeOf='b1', read_write='groupwrite', dptId='5.001', name='b1_Set_Ang',  inOut='Blinds_outside',  windowGroupName='P1',flags='inactive', value = 'N/A'),
    '1/5/3'  :  dict(typeOf='b1', read_write='read', dptId='5.001', name='b1_Get_Pos',inOut='Blinds_outside', windowGroupName='P1',flags='', value = 'N/A'),
    '1/6/3'  :  dict(typeOf='b1', read_write='read', dptId='5.001', name='b1_Get_Ang',  inOut='Blinds_outside',  windowGroupName='P1',flags='inactive', value = 'N/A'),
}
##IsUserControlGroup
#2/0/1
#2/1/1
#2/2/1
#2/3/1

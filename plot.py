import pandas as pd
import json
import matplotlib.pyplot as plt
from calendar import monthrange
from pandas import json_normalize

def cleanupJson():
    cols = ['time', 'sensor_values.radiationSky','sensor_values.radiationIndoor']
    data = []
    with open('logData2.log') as json_file:
        data = json.load(json_file)

    nycphil = json_normalize(data=data)
    #nycphil = json_normalize(data=data["sensor_values"],record_path=["sensor_values"],meta=["radiationSky", "radiationIndoor", "radiationFacade", "indoorTemp", "externalTemp", "Presence"])
    #nycphil.drop(columns=["get_controls","status"])
    #nycphil.head(3)
    print(nycphil[cols])
    pass



def getDATA():
    db = {}
    dayValues = []
    days = []
    months = []
    newDay = True
    newMonth = True
    currentYear = 2020
    currentMonth = 0
    currentDay = 0

    with open('logData2.log') as json_file:
        data = json.load(json_file)






        i = 0

        firstDateItem = list(data)[0]["time"]
        lastDateItem = list(data)[-1]["time"]
        firstMonth = firstDateItem.split(",")[0].split("/")[0]
        firstDay = firstDateItem.split(",")[0].split("/")[1]
        lastMonth = lastDateItem.split(",")[0].split("/")[0]
        lastDay = lastDateItem.split(",")[0].split("/")[1]
        
        for d in data:
            time = d["time"]
            
            date = time.split(",")[0]
            dateMonth,dateDay = int(date.split("/")[0]),int(date.split("/")[1])
            timeOfDay = time.split(",")[1]
            timeHH,timeMM = int(timeOfDay.split(":")[0]),int(timeOfDay.split(":")[1])

            if i == 0:
                currentDay = dateDay
                currentMonth = dateMonth
                i = 1

            if currentDay != dateDay:
                days.append({currentDay:dayValues})
                dayValues = []
                currentDay = currentDay + 1
                if currentDay > monthrange(2020,currentMonth)[1]:
                    currentDay = 1

            if currentMonth != dateMonth:
                months.append({currentMonth:days})
                days = []
                currentMonth = currentMonth + 1
                if currentMonth > 12:
                    currentMonth = 1
                    

            if timeHH >= 7 and timeHH <= 20:
                dayValues.append(dict(time=str("{}:{}".format(timeHH,timeMM)), radiationSky=d['sensor_values']['radiationSky'], radiationFacade=d['sensor_values']['radiationFacade']))
                        #dbCleaned.append
                        #(dict(time=str("{}:{}".format(timeHH,timeMM)),
                        #radiationSky=d['sensor_values']['radiationSky'],
                        #radiationIndoor=d['sensor_values']['radiationIndoor']))
                        #dbCleaned.append
                        #(dict(time=str("{}:{}".format(timeHH,timeMM)),
                        #externalTemp=d['sensor_values']['externalTemp'],
                        #indoorTemp=d['sensor_values']['indoorTemp']))
    
    return months

            #for p in d['sensor_values']:
            #    print('Name: ' + p['name'])
            #    print('Website: ' + p['website'])
            #    print('From: ' + p['from'])
            #    print('')
def plotData(months=None):
    d = {"sell": [{
                   "Rate": 0.001425,
                   "Quantity": 537.27713514
               },
               {
                   "Rate": 0.00142853,
                   "Quantity": 6.59174681
               }]}

    month = months[0]
    for day in month:
        values = month[day]
        var = day
        df = pd.DataFrame(values)
        df.plot(x='time')#, y='externalTemp')
        #df.plot()
                                 #plt.savefig("test_rasterization{}_{}.jpg".format(month[0],day[0]),
                                 #dpi=400)
        print(day)
        plt.show()


if __name__ == "__main__":
    cleanupJson()
    #data = getDATA()
    #plotData(data)





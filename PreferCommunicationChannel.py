import json
import logging
import requests
from datetime import date

"""
This will return a dictionary of each day and method
input = zipcode
output = {day:communication method} -- method = "By Phone","By Text" or "By Email"
        ex{"2021-07-28": "By Text"}
if can't get weather report . 
    output = {"Error", ""Can't Get the weather Report""}
"""
def GetCommunicationMethodByZipcode(zipCodeStr, countryStr=""):
    if countryStr == "":
        zipStr = zipCodeStr
    else:
        zipStr = zipCodeStr + "," + countryStr
    url = "https://api.openweathermap.org/data/2.5/forecast"
    headers = {'Content-Type': 'application/json'}
    parameters = {
        "zip": f'{zipStr}',
        "appid": 'f3c553170db141cf990b5b3580e7fbd2',
        "mode": '',
        "cnt": '',
        "units": 'Imperial',
        "lang": ''
    }
    weatherInfoByDayDict = {}
    retryCnt = 2
    while retryCnt != 0:
        weatherInfoByDayDict.clear()
        response = requests.get(url, headers=headers, params=parameters)
        if response.status_code == 200:
            jsonResponse = response.content.decode('utf-8')
            byDayDict = AggregateWeatherInfoByDay(jsonResponse)
            for day, weatherRec in byDayDict.items():
                method = GetCommunicationChannelMethod(weatherRec)
                weatherInfoByDayDict[day] = method
            break
        else:
            retryCnt = retryCnt - 1
            weatherInfoByDayDict["Error"] = 'Can\'t Get the weather Report for zip = "{0}", country = "{1}"'.format(
                zipCodeStr, countryStr)
    return weatherInfoByDayDict


"""
Parse and aggregate information from weather json report
input = json format from weather report for the next 6 days
output = {day:weatherConditions} --{2021-07-28: 
"""
def AggregateWeatherInfoByDay(jsonResponse):
    byDayDict = {}
    jsonNodes = json.loads(jsonResponse)
    lists = jsonNodes["list"]

    for listItem in lists:

        dt_txt = listItem["dt_txt"]
        dayStr = dt_txt.split(" ")[0]

        dayWeatherRec = {}
        if dayStr in byDayDict.items():
            # update existing day weather condition
            dayWeatherRec = byDayDict.get(dayStr)
            if dayWeatherRec["temp_min"] > listItem["main"]["temp_min"]:
                dayWeatherRec["temp_min"] = listItem["main"]["temp_min"]
            if dayWeatherRec["temp_max"] < listItem["main"]["temp_max"]:
                dayWeatherRec["temp_max"] = listItem["main"]["temp_max"]
            dayWeatherRec["temp"].append(listItem["main"]["temp"])
            weathers = listItem["weather"]
            for each in weathers:
                dayWeatherRec["weatherConditions"].append(each["main"])

            byDayDict[dayStr] = dayWeatherRec
        else:
            # new day
            dayWeatherRec["temp_min"] = listItem["main"]["temp_min"]
            dayWeatherRec["temp_max"] = listItem["main"]["temp_max"]
            weathers = listItem["weather"]
            dayWeatherRec["weatherConditions"] = []
            dayWeatherRec["temp"] = []
            dayWeatherRec["temp"].append(listItem["main"]["temp"])
            for each in weathers:
                dayWeatherRec["weatherConditions"].append(each["main"])

            byDayDict[dayStr] = dayWeatherRec
    return byDayDict


"""
Choose communication method by the requirement
input: dayWeatherRec
output: method = "By Phone","By Text" or "By Email"
"""
def GetCommunicationChannelMethod(dayWeatherRec):
    avgTemp = sum(dayWeatherRec["temp"]) / len(dayWeatherRec["temp"])

    if avgTemp < 55 or dayWeatherRec["weatherConditions"].count("Rain") > 1:
        return "By Phone"
    elif 55 < avgTemp < 75:
        return "By Email"
    elif avgTemp > 75 and dayWeatherRec["weatherConditions"].count("Rain") == 0:
        return "By Text"
    else:
        return "By Phone"


"""
format and print the result
"""
def PrintCommunicationMethod(weatherInfoByDayDict):
    for day, method in weatherInfoByDayDict.items():
        print('On {0}, recommended communication method "{1}"'.format(day, method))
        logging.info('On {0}, recommended communication method "{1}"'.format(day, method))
    print("Complete!!!")


"""
 Main Test
"""
if __name__ == '__main__':
    try:
        logging.basicConfig(filename='Test.log', level=logging.INFO)
        logging.info(f'Started ********{date.today()}*****************')

        zipCode = '55378'
        country = "us"
        logging.info('Test case # 1: Zipcode =  {0}'.format(zipCode))
        PrintCommunicationMethod(GetCommunicationMethodByZipcode(zipCode))

        logging.info('Test case # 2: Zipcode = {0}, Country = {1}'.format(zipCode, country))
        PrintCommunicationMethod(GetCommunicationMethodByZipcode(zipCode, country))

        zipCode = '553785'
        country = "us"
        logging.info('Test case # 3: Zipcode = {0}, Country = {1}'.format(zipCode, country))
        PrintCommunicationMethod(GetCommunicationMethodByZipcode(zipCode, country))

        zipCode = '55378'
        country = "usa"
        logging.info('Test case # 4: Zipcode = {0}, Country = {1}'.format(zipCode, country))
        PrintCommunicationMethod(GetCommunicationMethodByZipcode(zipCode, country))
        logging.info('Zipcode = {0}, Country = {1}'.format(zipCode, country))

    except Exception as e:
        print(e)
        logging.info(e)
    finally:
        print('*********** Finished ***********')
        logging.info('*********** Finished ***********')

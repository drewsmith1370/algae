import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv

def to_hr(x):
    res = np.empty(len(x))
    for i, str in enumerate(x):
        res[i] = str.split(':')[0]
    return res

def PopulateWeatherData(filename):
    """
    Reads weather data from a .csv file with the form
    (Date,Time,Light-avg,Light-std,Temp-avg,Temp-std)

    Returns:
        pd DataFrame populated with data
    """
    df = pd.DataFrame()
    data = []

    with open(filename,'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            # Skip headers and empty rows
            if (len(row)) <= 1:
                continue
            
            rowData = np.array(row)
            data.append(rowData)

    data = np.array(data)
    df = pd.DataFrame({
        'date'      : data[:,0],
        'time'      : data[:,1],
        'light avg' : data[:,2],
        'light std' : data[:,3],
        'temp avg'  : data[:,4],
        'temp std'  : data[:,5],
    })

    return df


    

def PlotYearWeather(df):
    """
    Print light and temperature versus time for every day 
    of the year on two plots

    Params:
        df: DataFrame populated via PopulateWeatherData()
    """
    fig, ax = plt.subplots(1,2)

    dateGroup = df.groupby('date')
    for date, group in dateGroup:
        if True:#date.startswith('01',3):
            time = group['time']
            hr = to_hr(time)
            lght = group['light avg'].astype(float)
            temp = group['temp avg'].astype(float)
            ax[0].plot(hr,lght,label=date)
            ax[1].plot(hr,temp,label=date)


    ax[0].set_ylabel('Light Intensity (umol / m^2 / s)')
    ax[0].set_title('Light Intensity vs Time in Key West, FL')
    ax[0].set_xlabel('Time (hr)')
    
    ax[1].set_ylabel('Temperature (C)')
    ax[1].set_title('Temperature vs Time in Key West, FL')
    ax[1].set_xlabel('time (hr)')

    plt.show()

class WeatherReporter:
    """
    Object class that is built to feed weather data into model-specific objects
    """
    def __init__ (self, filename):
        self.df = PopulateWeatherData(filename)

        # Group by date
        dateGroups = self.df.groupby('date')
        dates = []; groups = []
        for date, group in dateGroups:
            dates.append(date)
            groups.append(group)

        self.dateGroups = np.array(groups)


    def getDataFrame(self):
        return self.df
    
    def getDayForecast(self, day):
        return self.dateGroups[day][:,2:]

if __name__ == '__main__':
    weatherReport = WeatherReporter("./data/scott-lightTempData.csv")
    day = weatherReport.getDayForecast(28)
    print(day)
    
    PlotYearWeather(weatherReport.getDataFrame())
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv

# Project modules
import piCurves
import respiration
import weather


if __name__ == '__main__':
    # Initialize objects
    weatherReport = weather.WeatherReporter("./data/scott-lightTempData.csv")
    respTable = respiration.LookupResp()
    piTable = piCurves.LookupPI()

    growth_rates = np.zeros(24)

    for day in range(365):
        for hour in range(24):
            light, temp = weatherReport.getHourForecast(day, hour)
            resp_rate = respTable.lookup_resp(light, temp)
            pi_rate = piTable.lookup_pi(light, temp)

            growth_rates[hour] = pi_rate - resp_rate

        plt.plot(growth_rates)

    plt.show()
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv

# Project modules
import piCurves
import respiration
import weather

class GrowthLookup:
    """
    Abstraction wrapper for the two lookup tables. This class should be immutable
    """
    def __init__ (self):
        self.pi_lookup = piCurves.LookupPI()
        # self.resp_lookup = respiration.LookupResp()

    def getSpecGrowth(self, light, temp):
        """
        Get expected PI Rate - Resipration Rate (nmol O2 / mL / min)
        at a given light and temperature
        """
        pi = self.pi_lookup.lookup_pi(light, temp)
        # resp = self.resp_lookup.lookup_resp(light, temp)
        return pi
    

if __name__ == '__main__':
    # Initialize objects
    weatherReport = weather.WeatherReporter("./data/scott-lightTempData.csv")
    growTable = GrowthLookup()

    growth_rates = np.zeros(24)

    months = {
        "January"  : 31,
        "February" : 28,
        "March"    : 31,
        "April"    : 30,
        "May"      : 31,
        "June"     : 30,
        "July"     : 31,
        "August"   : 31,
        "September": 30,
        "October"  : 31,
        "November" : 30,
        "December" : 31
    }

    fig, ax = plt.subplots(3,4)
    def itr(i):
        return int(i/4), i%4

    i=0
    sum_days = 0
    for month, num_days in months.items():

        for day in range(sum_days, num_days + sum_days):
            for hour in range(24):
                # Get forecast
                light, temp = weatherReport.getHourForecast(day, hour)
                # Determine growth rate
                growth_rates[hour] = growTable.getSpecGrowth(light, temp)

            # Plot results for the day
            ax[itr(i)].plot(growth_rates)
        
        # Set chart parameters
        sum_days += num_days
        ax[itr(i)].set_title(month)
        ax[itr(i)].set_xlabel('Time of day (hr)')
        ax[itr(i)].set_ylabel('Biomass Growth Rate (M / s / OD750)')
        i += 1


    fig.suptitle("Specific growth rates over time")
    plt.show()
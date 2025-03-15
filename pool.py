import numpy as np
import matplotlib.pyplot as plt
import piCurves, weather, respiration
from scipy.integrate import solve_ivp

class GrowthLookup:
    """
    Abstraction wrapper for the two lookup tables
    """
    def __init__ (self):
        self.pi_lookup = piCurves.LookupPI()
        self.resp_lookup = respiration.LookupResp()

    def getSpecGrowth(self, light, temp):
        """
        Get expected PI Rate - Resipration Rate (nmol O2 / mL / min)
        at a given light and temperature
        """
        pi = self.pi_lookup.lookup_pi(light, temp)
        resp = self.resp_lookup.lookup_resp(light, temp)
        return (pi - resp)

class AlgaePool:
    """
    Pool class for simulating algae growth.
    """

    def __init__ (self, init_conc, init_growth, tsize, dt):
        """
        Initializer for Pool class. Time range and step are required to create 
        immutable sized arrays.

        Params:
            init_conc: Initial concentration of algae, in TODO: units
            init_growth: Initial growth rate, in TODO: units
            tsize: Range 
        """
        # Initialize arrays
        t_arr = np.linspace(0,dt*tsize, tsize+1)
        conc_arr = np.zeros(len(t_arr))
        conc_arr[0] = init_conc
        # Replace self
        self.deltaTime = dt
        self.time_arr = t_arr
        self.conc_arr = conc_arr
        self.spec_growth_rate = init_growth
    
    def getConcentrationData(self):
        """
        Returns the concentration array
        """
        return self.conc_arr

    def updateEnvironmentGrowthRate(self, newGrowth):
        """
        Update the specific growth rate from external factors for a new time
        """
        self.spec_growth_rate = newGrowth
    
    def _dconc_dtime(self, mu, conc):
        """
        Calculate the current rate of growth using kinetic expression
        Kinetics of this reaction follow the form:

            r_growth = mu * C_biomass (TODO: Get actual growth model and cite)
        """
        return mu * conc


    def runStep(self, index):
        """
        Run a single step of the algae reaction, following the form of the reaction:

            H2O + CO2 + NH3 + PO4 --> O2 + Biomass

        Kinetics of this reaction follow the form:

            r_growth = mu * C_biomass (TODO: Get actual growth model and cite)

        Params:
            index: current index of arrays to be calculated
        """
        conc = self.conc_arr[index]
        mu = self.spec_growth_rate
        dt = self.deltaTime

        # Kinetic equation
        dcdt = self._dconc_dtime(mu,conc)
        # Integrate forward
        conc = conc + dcdt * dt
        # Update datum
        self.conc_arr[index+1] = conc

    def emptyPool(self):
        """
        Empty the pool and return the amount of algae deliverred
        """
        # TODO

    def fillPool(self, amount):
        """
        """
        # TODO

if __name__ == '__main__':
    pool = AlgaePool(.01, .1, 100, .1)
    wreport = weather.WeatherReporter('./data/scott-lightTempData.csv')
    glookup = GrowthLookup()

    for i in range(100):
        t = i/10 + 50
        light, temp = wreport.getHourForecast(int(t/24), int(t%24))
        growth = glookup.getSpecGrowth(light, temp)
        pool.updateEnvironmentGrowthRate(growth)
        pool.runStep(i)

    data = pool.getConcentrationData()
    plt.plot(data)
    plt.show()

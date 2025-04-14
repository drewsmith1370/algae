import numpy as np
import matplotlib.pyplot as plt
import weather
from growthRatesKW import GrowthLookup
from scipy.integrate import solve_ivp

# Beer Lambert Constants
K = 500 # TODO: Units

class AlgaePool:
    """
    Pool class for simulating algae growth.
    """

    def __init__ (self, init_conc, growth_lookup: GrowthLookup, depth, depthStep):
        """
        Initializer for Pool class. Time range and step are required to create 
        immutable sized arrays.

        Params:
            init_conc: Initial concentration of algae, in TODO: units
            init_growth: Initial growth rate, in TODO: units
            tsize: Range 
        """
        # Concentration
        self.conc = init_conc
        # Supply with growth lookup
        self.growth_lookup = growth_lookup
        # Depth information
        self.depth = depth
        self.depthStep = depthStep
    
    def setConcentration(self, conc):
        """
        Returns the concentration array
        """
        self.conc = conc

    def _getEnvGrowthRate(self, light, temp):
        """
        Update the specific growth rate from external factors for a new time
        """
        return self.growth_lookup.getSpecGrowth(light, temp)
    
    def _dconc_dtime(self, mu, conc):
        """
        Calculate the current rate of growth using kinetic expression
        Kinetics of this reaction follow the form:

            r_growth = mu * C_biomass
        """
        return mu * conc
            
    def _beerLambert(self, i0, depth):
        """
        Beer Lambert's law. TODO: Update with corrected scattering
        """
        return i0 * np.exp(-K * depth * self.conc)
    
    def calcOverallGrowth(self, light, temp):
        """
        Calculate the specific growth rate by averaging over each depth
        """
        depth = self.depth
        depthStep = self.depthStep

        avg = 0 # Accumulator
        range = np.arange(0,depth+depthStep,depthStep)
        for d in range:
            # Use Beer-Lamberts law to calculate light intensity at the depth
            l = self._beerLambert(light, depth)
            # Use light and temp to determine the predicted growth rate
            mu = self._getEnvGrowthRate(l, temp)
            
            # Average the growth rate
            avg += mu
        
        avg = avg / (depth / depthStep + 1)
        return avg

    def runStep(self, light, temp):
        """
        Run a single step of the algae reaction, following the form of the reaction:

            H2O + CO2 + NH3 + PO4 --> O2 + Biomass
            items += 1

        Kinetics of this reaction follow the form:

            r_growth = mu * C_biomass

        Params:
            index: current index of arrays to be calculated
        """
        mu = self.calcOverallGrowth(light, temp) / 160.5
        conc = self.conc
        dcdt = self._dconc_dtime(mu, conc)

        return dcdt

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
    glookup = GrowthLookup()
    pool = AlgaePool(.01, glookup, 5, .01)
    wr = weather.WeatherReporter("./data/scott-lightTempData.csv")
    from scipy.integrate import solve_ivp

    # Solver function
    def func(t, c, weatherReport: weather.WeatherReporter, pool: AlgaePool):
        pool.setConcentration(c)

        # Calculate Time Point
        hour = t / 60 / 60                                      # Hours that have passed
        day = int(np.floor(hour / 24))                          # Days that have passed
        hour -= 24 * day                                        # Hour of the day

        # Fetch Weather Data
        light, temp = weatherReport.getHourForecast(day, hour)

        # Calculate time derivative
        dcdt = pool.runStep(light, temp)

        return dcdt
    
    ## Solver Params
    c0 = 1e-5 # M

    ##################
    ## Solver Setup ##
    ##################
    start_day = 0                                                                # Start day for data
    num_days = 10                                                                # Number of days to simulate
    start_time = start_day * 24 * 60 * 60                                        # Starting day of the year
    max_time = (num_days + start_day) * 24 * 60 * 60                             # Convert to seconds
    t_span = (start_time,max_time)                                               # Create time span
    t_eval = np.linspace(start_time,max_time,1000)                               # Create evaluation array

    # Function wrapper for solve_ivp
    def func_wrapper(t, c):
        return func(t, c, wr, pool)

    # Call solve_ivp with adjusted settings
    sol = solve_ivp(
        func_wrapper,
        t_span,
        [c0],
        t_eval = t_eval,
        method='RK45',  # RK45, BDF, Radau
    )

    c = sol.y[0]
    t = t_eval / 24 / 60 / 60       # Convert to days
    w = c * 3550
    plt.plot(t,w,'-m')
    plt.xlabel("Time (days)")
    plt.ylabel(r"Biomass Concentration ($\frac{g}{L}$)")
    plt.title("Biomass Concentration, January 1-10")
    plt.show()
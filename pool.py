import numpy as np
import matplotlib.pyplot as plt

class AlgaePool:
    """
    Pool class for simulating algae growth.
    """

    def __init__ (self, init_conc, init_growth, trange, tstep):
        """
        Initializer for Pool class. Time range and step are required to create 
        immutable sized arrays.

        Params:
            init_conc: Initial concentration of algae, in TODO: units
        """
        # Initialize arrays
        t_arr = np.arange(0,trange+tstep,tstep)
        conc_arr = np.zeros(len(t_arr))
        conc_arr[0] = init_conc
        # Replace self
        self.tstep = tstep
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
        dt = self.tstep

        # Kinetic equation
        dcdt = self._dconc_dtime(mu,conc)
        # Integrate forward
        conc = conc + dcdt * dt
        # Update datum
        self.conc_arr[index+1] = conc

if __name__ == '__main__':
    pool = AlgaePool(.01, .1, 100, 1)

    for i in range(100):
        pool.updateEnvironmentGrowthRate(.1)
        pool.runStep(i)

    data = pool.getConcentrationData()
    plt.plot(data)
    plt.show()

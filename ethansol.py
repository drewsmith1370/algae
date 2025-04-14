import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Project modules
import piCurves
import respiration
import weather

def func(t, c, k, lz, weatherReport, respTable, piTable, c0, empty, nd, acc, alpha, beta, v):
        #print(t / 60 /60 / 24)
        dz = lz / nd
        if c[0] > empty:
            acc[0] += c[0] - c0
            c[0] = c0

        # Calculate Time Point
        hour = t / 60 / 60                                      # Hours that have passed
        day = int(np.floor(hour / 24))                          # Days that have passed
        hour -= 24 * day                                        # Hour of the day

        # Fetch Weather Data
        light, temp = weatherReport.getHourForecast(day, hour)

        '''
        # Find average light intensity
        light = light * (1 - np.exp(-c*1000*k*lz)) / lz / k / c      # Integrated Beer-Lambert Law

        # Fetch Respiration and Photosynthetic Rate
        resp_rate = respTable.lookup_resp(light, temp)          # Respiration
        pi_rate = piTable.lookup_pi(light, temp)                # Photosynthesis

        # Calculate Growth Rate
        o2_rate = pi_rate - resp_rate
        mu = o2_rate / 160.5
        '''
       
        if c < 0:
            print(c)

        od = c[0] * 3550 * 0.859
        #kod = -1/(1/od + alpha*k)
        #kl = -1/beta/k*(1/od + 1/kod)

        mu_av = 0
        for i in range(nd+1):
            #ksa = k * (kod/(kod+od)) * (kl/(kl+i*dz))
            #print(ksa,k)
            l = light * np.exp(-od*k*(i*dz))

            pi_rate = piTable.lookup_pi(l, temp)                # Photosynthesis
            mu_av += pi_rate

        #print(mu_av, od)
        mu_av /= (nd+1)  

        # Calculate time derivative
        dcdt = mu_av*od

        return dcdt


def main():
    #####################
    ## Input Variables ##
    #####################
    k = 87.9       #                                                               # Beer Lambert Coefficient
    lz = 0.3       # m                                                             # Pool Depth
    c0 = 1e-1      # M                                                             # Initial Concentration
    alpha = -0.0187
    beta = -0.0536
    v = 1e7                                                                        # Volume in L

    ##############################
    ## Initialize Lookup Tables ##
    ##############################
    weatherReport = weather.WeatherReporter("./data/scott-lightTempData.csv")     # Weather Data
    respTable = respiration.LookupResp()                                          # Respiration Data
    piTable = piCurves.LookupPI()                                                 # Photosynthesis Data

    ##################
    ## Solver Setup ##
    ##################
    start_day = 0                                                                 # Start day for data
    num_days = 10                                                                # Number of days to simulate
    start_time = start_day * 24 * 60 * 60                                         # Starting day of the year
    max_time = (num_days + start_day) * 24 * 60 * 60                              # Convert to seconds
    t_span = (start_time,max_time)                                                # Create time span
    t_eval = np.linspace(start_time,max_time,10000)                               # Create evaluation array
    empty = 0.8
    empty /= 3550
    nd = 100
    acc = [0]

    # Function wrapper for solve_ivp
    def func_wrapper(t, c):
        nonlocal acc
        return func(t, c, k, lz, weatherReport, respTable, piTable, c0, empty, nd, acc, alpha, beta, v)

    # Call solve_ivp with adjusted settings
    sol = solve_ivp(
        func_wrapper,
        t_span,
        [c0],
        t_eval = t_eval,
        max_step = 7200,
        method='RK45',  # RK45, BDF, Radau
    )
    # print(sol.y[0,-1])
    print(sol)
    acc[0] += sol.y[0,-1]-c0
    print(f"g/m^2: {acc[0] * 3550 * 1000 * lz}")
    print(f"Tons Per Day: {acc[0] * 3550 * v / num_days / 1e6}")
    print(f"Tons Total: {acc[0] * 3550 * v / 1e6}")
    #print(f"Square Meters: {1000000 / (acc[0] * 3550 * lz)}" )
    #print(f"Hectares: {1000000 / (acc[0] * 3550 * lz) * 0.0001}")

    c = sol.y[0]
    t = t_eval / 24 / 60 / 60       # Convert to days
    w = c * 3550
    plt.plot(t,w,'-m')
    plt.xlabel("Time (days)")
    plt.ylabel(r"Biomass Concentration ($\frac{g}{L}$)")
    plt.title("Biomass Concentration, January 1-10")
    plt.show()

main()
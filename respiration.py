import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv

class LookupResp:
    def __init__(self):
        df = pd.DataFrame()

        with open('./data/respiration.csv','r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                # Skip headers and empty rows
                if (len(row)) <= 1:
                    continue
                # Parse lines
                name = row[0]
                vals = np.array(row[1:])
                df[name] = vals
                
                if (name == 'Temp'):
                    self.tempVals = vals.astype(float)

        self.df = df
        self.lightVals = np.array(df.keys())[1:].astype(float)
        self.arr = df.to_numpy()[:,1:].astype(float) # [tempIdx, lightIdx]
        self._correct_err_vals()

    def _correct_err_vals(self):
        """
        Corrects any -1 values in the array by averaging the three nearest values,
        since they are all in the last row.
        """
        arr = self.arr
        for i in range(len(arr)):
            for j in range(len(arr[i])):
                if arr[i][j] == -1:
                    val = 1/3 * (arr[i-1][j] + arr[i][j-1] + arr[i][j+1])
                    self.arr[i][j] = val


    def printTable(self):
        print(self.df)

    # Return the (lower_index, upper_index) surrounding light val for linear interp.
    def _find_light_indices(self, light):
        # Get light values
        light_vals = self.lightVals
        # find the lower index of the light value
        idx = 0
        for i, elem in enumerate(light_vals):
            if float(elem) < light:
                idx = i
        # Find lower and upper light vals
        light_lo = light_vals[idx]
        light_hi = light_vals[idx+1] if idx+1 < len(light_vals) else light_vals[idx]
        return idx, light_lo, light_hi
    
    # Return the (lower_index, upper_index) surrounding temp val for linear interp.
    def _find_temp_indices(self, temp):
        # Get light values
        temp_vals = self.tempVals
        # find the lower index of the light value
        idx = 0
        for i, elem in enumerate(temp_vals):
            if float(elem) < temp:
                idx = i
        # Find lower and upper light vals
        temp_lo = temp_vals[idx]
        temp_hi = temp_vals[idx+1] if idx+1 < len(temp_vals) else temp_vals[idx]
        return idx, temp_lo, temp_hi


    def lookup_resp(self, light, temp):
        """
        Use bilinear filtering to lookup PI value
        
        params:
            light - light intensity in umol/m2/s
            temp  - temperature in degrees Celsius
        
        returns:
            respiration rate in umol O2 per
        """

        # Get bounding light vals
        idx_lo, light_lo, light_hi = self._find_light_indices(light)
        idx_hi = idx_lo + 1 if idx_lo+1 < len(self.lightVals) else idx_lo
        alpha = (light_hi - light) / (light_hi - light_lo)

        # Get bounding temp vals
        jdx_lo, temp_lo, temp_hi = self._find_temp_indices(temp)
        jdx_hi = jdx_lo + 1 if jdx_lo+1 < len(self.tempVals) else jdx_lo
        beta = (temp_hi - temp) / (temp_hi - temp_lo)

        # Lookup each value
        arr = self.arr
        # bilinear interpolation
        pi = alpha * beta * arr[jdx_lo, idx_lo] + \
            (1-alpha) * beta * arr[jdx_lo, idx_hi] + \
            alpha * (1-beta) * arr[jdx_hi, idx_lo] + \
            (1-alpha) * (1-beta) * arr[jdx_hi, idx_hi]

        return pi

if __name__ == '__main__':
    lookup = LookupResp()
    
    l = np.arange(0,2000,40)
    t = np.arange(14.5,36.5,.5)
    X,Y = np.meshgrid(l, t)
    Z = np.zeros(X.shape)
    print(X.shape)
    for i, lght in enumerate(l):
        for j, tmp in enumerate(t):
            Z[j,i] = lookup.lookup_resp(lght,tmp)
    # Z = lookup.lookup_pi(l,t)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.plot_surface(X,Y,Z)
    ax.set_xlabel('Light Intensity (umol/m^2/s)')
    ax.set_ylabel('Temperature (degrees C)')
    ax.set_zlabel('Respiration rate (nmol O2/mL/min)')
    plt.show()

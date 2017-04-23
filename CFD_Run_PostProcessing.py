# -*- coding: utf-8 -*-
# CFD_Run_PostProcessing.py

#########################
# What this script does #
#########################

# Remove the folders from the Elevation folder such that it is just .vtk files
# Plot the water elevation at the last timestep - comparing pressure and alpha1 elevations. 
# Plot the development of the water elevation over time using the alpha1 elevations.
# Output the water elevations at the probe locations in a table.
# Output the flow rate through the outlet surface.  

# Written for the Plas Uchaf Reservoir project

########################
# CFD Run Requirements #
########################

# The script requires you to output an isoSurface of alpha1 = 0.5 for each output timestep. 
# Also required are pressure probes along the profile of the spillway that are 0.1m above the bottom surface. 

##############
# User Guide #
##############

# - Adjust the user input to the appropriate folder location. 

############
# Versions #
############

# 19/01/2017 - V01 - James Runnalls

##########################
# Package initialisation #
##########################
print("Initialising Packages")

# IMPORT PYTHON MODULES
#from paraview.simple import *
#from paraview import servermanager as sm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import os
import shutil
import time

###############
# USER INPUTS #
###############
print("Reading User Inputs")

# Input folder location
folder = r"V:\j24130900\OpenFoam\Run\PU_Final_DF"

# Plot timeseries data (very slow) (Y/N)
plotts = "N"

# Export output to csv (Y/N)
exportcsv = "Y"

# Plot critical level in reservior 

cl = 146.30

#############
# Functions #
#############

# This function recursively deletes folders if they are empty

def recursive_delete_if_empty(path):
    if not os.path.isdir(path):
        return False
    if all([recursive_delete_if_empty(os.path.join(path, filename))
            for filename in os.listdir(path)]):
        os.rmdir(path)
        return True
    else:
        return False

#############
# Main Code # 
#############
start = time.time()

# Remove the alpha1 vtk folders and make them more readable
print("Removing Elevation vtk's From Folders")

folder = folder+"\\"
ElevFolder = folder+"Elevation"
os.chdir(ElevFolder)
rt = os.listdir('.')
rt.sort()
rt = [ x for x in rt if "vtk" not in x ]

for t in rt:
    files = os.listdir(t)
    t2 = str(int(float(t)*1000))
    for file in files:
        shutil.move(t+'/'+file,t2+'_'+file)

        recursive_delete_if_empty(ElevFolder)
print("Time Elapsed: ", time.time()-start, "s")

# Importing probe co-ordinates & cleaning the data
print("Importing Probe Co-ordinates and Cleaning the Data")

input = folder+"probes\\"
probes = os.listdir(input)
for pb in os.listdir(input):
    probes = pb
pdir = input+probes+"\p."
coords = pd.read_table(pdir, header=None, delim_whitespace=True, engine='python', nrows=3)
coords = coords.set_index(1)
coords = coords.drop(0, 1)
coords = coords.transpose()
coords = coords.reset_index(drop=True)
coords['z'] -= 0.1
print("Time Elapsed: ", time.time()-start, "s")

# Calcualting the distance along the long section
print("Calcualting The Distance Along The Long Section")

coords['Distance (m)'] = 0.00
coords['Alpha1 Elevation (mAOD)'] = 0.00
coords['Velocity (m/s)'] = 0.00
for index, row in coords.iterrows():
    if index != 0:
        index1 = int(index) - 1
        x1 = coords.iat[index1,0]
        y1 = coords.iat[index1,1]
        x2 = coords.iat[index,0]
        y2 = coords.iat[index,1]
        dis = np.sqrt(((y2-y1)**2)+((x2-x1)**2))
        dis = coords.iat[index1,3] + dis
        coords.set_value(index, 'Distance (m)', dis)
print("Time Elapsed: ", time.time()-start, "s")

# Importing alpha1 and matching the alpha1 surface value to the probe location

# Check elevation files are in the right order
print("Ordering Elevation Files")    
    
numbers = re.compile('\d+(?:\.\d+)?')
Elevation = os.listdir(ElevFolder)
indexwl = []
for i in range(len(Elevation)):
    Elevation[i] = ''.join(numbers.findall(Elevation[i]))
Elevation.sort(key=int)
indexwl = Elevation.copy()
for i in range(len(Elevation)):
    Elevation[i] = Elevation[i]+"_U_freeSurface.vtk"
    indexwl[i] = float(indexwl[i])/1000
print("Time Elapsed: ", time.time()-start, "s")

# Create dataframe for the change in water level & change in velocity plot
wl = pd.DataFrame()
ut = pd.DataFrame()

# Loop for all of the elevtion vtk's
for i in range(len(Elevation)):
    
    # Control whether to do convergence output
    if plotts == "Y" or i == (len(Elevation)-1):
        
        # Import the data from the vtk and clean it
        print("Reading vtk File "+str(i+1)+" of "+str(len(Elevation)))
          
        wl[Elevation[i]] = 0.00
        ut[Elevation[i]] = 0.00
        vtk = ElevFolder+"\\"+Elevation[i]
        el = pd.read_table(vtk, header=None, delim_whitespace=True, engine='python')
        el = el.drop(el.index[[0,1,2,3,4]])
        el.drop(el.columns[[3, 4]], axis=1, inplace=True)
        el = el.reset_index(drop=True)
        el.columns = ['x', 'y', 'z']
        eln = el.loc[el['x'] == 'POLYGONS']
        elv = el.loc[el['x'] == 'U']
        x = int(eln.index[0])
        k = int(elv.index[0]) + 1
        l = len(el.index)
        elu = el[k:l]
        elu = elu.reset_index(drop=True)
        el = el[0:x]
        el = el.apply(pd.to_numeric)
        elu = elu.apply(pd.to_numeric)
        elu['U'] = ((elu['x']**2)+(elu['y']**2)+(elu['z']**2))**0.5
        el['U'] = elu['U']
        print("Time Elapsed: ", time.time()-start, "s")
        
        print("Extracting Elevation & Velocity from vtk File "+str(i+1)+" of "+str(len(Elevation)))
        # Extract the elevation values for the probes
        for index, row in coords.iterrows():
            elt = el.copy()
            xx2 = coords.iat[index,0]
            yy2 = coords.iat[index,1]
            elt['Probe'] = np.sqrt(((elt['y']-yy2)**2)+((elt['x']-xx2)**2))
            elt.sort_values('Probe',inplace=True)
            dif = elt.iloc[0]['Probe']
            # Take ground level (no water) if it has to go more than 0.5m to find a point
            if dif > 0.5:
                z = coords.iat[index,2]
                u = 0.00
            else:
                z = elt.iloc[0]['z']
                u = elt.iloc[0]['U']
            wl.set_value(index, Elevation[i], z)
            ut.set_value(index, Elevation[i], u)
            coords.set_value(index, 'Alpha1 Elevation (mAOD)', z)
            coords.set_value(index, 'Velocity (m/s)', u)
        #del el
        print("Time Elapsed: ", time.time()-start, "s")

# Calculate water depth
coords['Water Depth (m)'] = coords['Alpha1 Elevation (mAOD)'] - coords['z']  

# Calculate Froode Number
coords['Froude Number'] = coords['Velocity (m/s)']/((9.81*coords['Water Depth (m)'])**0.5)
        
###########
# Outputs #
###########

# Plotting the final water level
plt.plot(coords['Distance (m)'], coords['z'], '-o')
for index, row in coords.iterrows():
    X = coords.iat[index,3]
    Y = coords.iat[index,2]
    plt.annotate(index,xy=(X,Y), xytext=(5, 5), ha='right',
                textcoords='offset points')
plt.plot(coords['Distance (m)'], coords['Alpha1 Elevation (mAOD)'], '-')
plt.gca().set_aspect('equal', adjustable='box')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.title('Elevation at Probes')
plt.ylabel('Elevation (mAOD)')
plt.xlabel('Distance Along Centreline (m)')
plt.show()

# Plotting the change in water level
if plotts == "Y":
    wl = wl.transpose()
    wl = wl.set_index([indexwl])
    wl.plot()
    wl['Critical'] = cl
    wl['Critical'].plot(color="red", linewidth=2.5, linestyle="--")
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title('Convergence to Steady State')
    plt.ylabel('Elevation (mAOD)')
    plt.xlabel('Time (s)')
    plt.show()
    
# Plotting the change in velocity
if plotts == "Y":
    ut = ut.transpose()
    ut = ut.set_index([indexwl])
    ut.plot()
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title('Convergence to Steady State')
    plt.ylabel('Velocity (m/S)')
    plt.xlabel('Time (s)')
    plt.show()
    
# Outputting table of results for last time step
print(coords)

#Export to csv
if exportcsv == "Y":
    try:
        os.remove(folder+"Output.csv")
    except OSError:
        pass
    try:
        coords.to_csv(folder+"Output.csv",sep=',')
    except OSError:
        print("CSV file is open, please close and re-run the program.")

if plotts == "Y" and exportcsv == "Y":
    try:
        os.remove(folder+"WaterLevelTimeSeries.csv")
    except OSError:
        pass
    try:
        wl.to_csv(folder+"WaterLevelTimeSeries.csv",sep=',')
    except OSError:
        print("CSV file is open, please close and re-run the program.")
        
if plotts == "Y" and exportcsv == "Y":
    try:
        os.remove(folder+"VelocityTimeSeries.csv")
    except OSError:
        pass
    try:
        ut.to_csv(folder+"VelocityTimeSeries.csv",sep=',')
    except OSError:
        print("CSV file is open, please close and re-run the program.")

print("Run Successful")




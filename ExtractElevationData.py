# -*- coding: utf-8 -*-
# ExtractElevationData.py

#########################
# What this script does #
#########################

# Remove the folders from the Elevation folder such that it is just .vtk files
# Import the water elevation at probe locations and along right and left walls 

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
# 10/10/2017 - v02 - James Runnalls (Updated to allow wall water elevation plotting.)

##########################
# Package initialisation #
##########################
print("Initialising Packages")

# IMPORT PYTHON MODULES
#from paraview.simple import *
#from paraview import servermanager as sm
import pandas as pd
import numpy as np
import re
import os
import shutil
import time
import sys
start = time.time()
###############
# USER INPUTS #
###############

# Input folder location
folder = r"V:\j24130900\OpenFoam\Run\PU_Final_DF"

#Input wall file locations if desired
rightwall = r"V:\j24130900\OpenFoam\Run\PU_Final4\rightwall.csv"
leftwall = r"V:\j24130900\OpenFoam\Run\PU_Final4\leftwall.csv"

# Plot timeseries data (Y/N)
TimeSeries = "Y"

#############
# Functions #
#############

def DeleteEmptyFolders(path):
    if not os.path.isdir(path):
        return False
    if all([DeleteEmptyFolders(os.path.join(path, filename))
            for filename in os.listdir(path)]):
        os.rmdir(path)
        return True
    else:
        return False
 
def RemoveElevationVTKsFromFolders(folder):
    try:
        os.chdir(folder+"\\"+"Elevation")
        rt = os.listdir('.')
        rt.sort()
        rt = [ x for x in rt if "vtk" not in x ]
        for t in rt:
            files = os.listdir(t)
            t2 = str(int(float(t)*1000))
            for file in files:
                shutil.move(t+'/'+file,t2+'_'+file)
                DeleteEmptyFolders(folder+"\\"+"Elevation")
    except:
        print("Folder location or folder structure is incorrect, please check the inputs.")
        sys.exit()

def ImportProbeCoords(folder):
    try:
        probes = os.listdir(folder+"\\"+"probes\\")
        for pb in os.listdir(folder+"\\"+"probes\\"):
            probes = pb
        pdir = folder+"\\"+"probes\\"+probes+"\p."
        coords = pd.read_table(pdir, header=None, delim_whitespace=True, engine='python', nrows=3)
        coords = coords.set_index(1)
        coords = coords.drop(0, 1)
        coords = coords.transpose()
        coords = coords.reset_index(drop=True)
        coords['z'] -= 0.1
        print("Success")
        return coords
    except:
        print("No probe information found.")

def ImportPointCoords(file):
    try:
        df = pd.read_csv(file)
        print("Success")
        return df
    except:
        print("No points co-ordinates found.")

def PlanarDistanceBetweenPoints(points):
    try:
        points['Distance (m)'] = 0.00
        for index, row in points.iterrows():
            if index != 0:
                index1 = int(index) - 1
                x1 = points.iat[index1,0]
                y1 = points.iat[index1,1]
                x2 = points.iat[index,0]
                y2 = points.iat[index,1]
                dis = np.sqrt(((y2-y1)**2)+((x2-x1)**2))
                dis = points.iat[index1,3] + dis
                points.set_value(index, 'Distance (m)', dis)
        print("Success")
        return points
    except:
        print("Either points do not exist or have been formatted incorrectly")
 
def OrderedListofElevationFiles(folder):
    numbers = re.compile('\d+(?:\.\d+)?')
    Elevation = os.listdir(folder+"\\"+"Elevation")
    for i in range(len(Elevation)):
        Elevation[i] = ''.join(numbers.findall(Elevation[i]))
    Elevation.sort(key=int)
    for i in range(len(Elevation)):
        Elevation[i] = Elevation[i]+"_U_freeSurface.vtk"
    return Elevation

def PrintTime():
    print("Time Elapsed: ", time.time()-start, "s")
    
def LoadAlpha1VTK(VTKname,folder):
    vtk = folder+"\\"+"Elevation"+"\\"+VTKname
    df = pd.read_table(vtk, header=None, delim_whitespace=True, engine='python')
    df = df.drop(df.index[[0,1,2,3,4]])
    df.drop(df.columns[[3, 4]], axis=1, inplace=True)
    df = df.reset_index(drop=True)
    df.columns = ['x', 'y', 'z']
    dfn = df.loc[df['x'] == 'POLYGONS']
    dfv = df.loc[df['x'] == 'U']
    x = int(dfn.index[0])
    k = int(dfv.index[0]) + 1
    l = len(df.index)
    dfu = df[k:l]
    dfu = dfu.reset_index(drop=True)
    df = df[0:x]
    df = df.apply(pd.to_numeric)
    dfu = dfu.apply(pd.to_numeric)
    dfu['U'] = ((dfu['x']**2)+(dfu['y']**2)+(dfu['z']**2))**0.5
    df['U'] = dfu['U']
    return df

def ElevationAndVelocityAtPoints(VTK,pointse,pointsu,VTKname):
    try:
        pointse[VTKname] = 0.00
        pointsu[VTKname] = 0.00  
        for index, row in pointse.iterrows():
            df = VTK.copy()
            xx2 = pointse.iat[index,0]
            yy2 = pointse.iat[index,1]
            df['Point'] = np.sqrt(((df['y']-yy2)**2)+((df['x']-xx2)**2))
            df.sort_values('Point',inplace=True)
            # Take ground level (no water) if it has to go more than 0.5m to find a point
            if df.iloc[0]['Point'] > 0.5:
                z = pointse.iat[index,2]
                u = 0.00
            else:
                z = df.iloc[0]['z']
                u = df.iloc[0]['U']
            pointse.set_value(index, Elevation[i], z)
            pointsu.set_value(index, Elevation[i], u)
        print("Success")
        return pointse,pointsu
    except:
        print("No points co-ordinates found.")
        pointse = []
        pointsu = []
        return pointse,pointsu
    
def csvexport(folder,points,Name):
    if not os.path.exists(folder+"\\"+"Output"):
        os.makedirs(folder+"\\"+"Output")
    try:
        os.remove(folder+"\\"+"Output"+"\\"+Name+".csv")
    except OSError:
        pass
    try:
        points.to_csv(folder+"\\"+"Output"+"\\"+Name+".csv")
    except:
        print(Name+" failed to export to csv.")
 
###############################
# Extracting and Sorting Data # 
##############################

print("Removing Elevation vtk's From Folders")
RemoveElevationVTKsFromFolders(folder)
PrintTime()

print("Ordering Elevation Files") 
Elevation = OrderedListofElevationFiles(folder)
PrintTime()

print("Importing Probe Co-ordinates and Cleaning the Data")
coords = ImportProbeCoords(folder)
PrintTime()

print("Importing Wall Co-ordinates and Cleaning the Data")
rw = ImportPointCoords(rightwall)
lw = ImportPointCoords(leftwall)
PrintTime()

print("Calcualting Planar Distance Between Points")
coords = PlanarDistanceBetweenPoints(coords)
rw = PlanarDistanceBetweenPoints(rw)
lw = PlanarDistanceBetweenPoints(lw)
PrintTime()

# Split elevation and velocity into seperate variables
try:
    coordse = coords.copy()
    coordsu = coords.copy()
except:
    coordse = []
    coordsu = []
try:
    rwe = rw.copy()
    rwu = rw.copy()
except:
    rwe = []
    rwu = []   
try:
    lwe = lw.copy()
    lwu = lw.copy()
except:
    lwe = []
    lwu = [] 

print("Extracting elevation and velocity at points")
for i in range(len(Elevation)):
    # Control whether to do timeseries output
    if TimeSeries == "Y" or i == (len(Elevation)-1):
        print("Proccessing vtk File "+str(i+1)+" of "+str(len(Elevation)))
        VTK = LoadAlpha1VTK(Elevation[i],folder)
        coordse,coordsu = ElevationAndVelocityAtPoints(VTK,coordse,coordsu,Elevation[i])
        rwe,rwu = ElevationAndVelocityAtPoints(VTK,rwe,rwu,Elevation[i])
        lwe,lwu = ElevationAndVelocityAtPoints(VTK,lwe,lwu,Elevation[i])
        PrintTime()

#Export to csv
csvexport(folder,coordse,"coordse")
csvexport(folder,coordsu,"coordsu")
csvexport(folder,rwe,"rwe")
csvexport(folder,rwu,"rwu")
csvexport(folder,lwe,"lwe")
csvexport(folder,lwu,"lwu")

print("Run Successful")














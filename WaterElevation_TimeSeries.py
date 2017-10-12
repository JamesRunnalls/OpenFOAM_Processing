# -*- coding: utf-8 -*-
# WaterElevation_TimeSeries.py

#########################
# What this script does #
#########################

# Plot elevations and timeseries plots for CFD results. 

# Written for the Plas Uchaf Reservoir project

########################
# CFD Run Requirements #
########################

#  Requires Extract Elevation Data to be run first.

##############
# User Guide #
##############

# - Adjust the user input to the appropriate folder location. 

############
# Versions #
############

# 10/10/2017 - v01 - James Runnalls

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
import seaborn as sns
import os
import re
###############
# USER INPUTS #
###############

# Input folder location
folder = r"V:\j24130900\OpenFoam\Run\PU_Final4"

# Export images (Y/N)
Images = "Y"

# Number of vtk's to use for average, min and max values.
Number = 20

#############
# Functions #
#############

def MinMaxMean(Number,Elevation,points):
    df = points.iloc[:,-min(Number,len(Elevation)):].copy()
    points = points.iloc[:,0:4].copy()
    points['Mean'] = df.mean(axis=1)
    points['Max'] = df.max(axis=1)
    points['Min'] = df.min(axis=1)
    return points

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

def PlotWaterLevel(folder,points,Name,Images,Reverse):
    Elevation = os.listdir(folder+"\\"+"Elevation")
    df = MinMaxMean(Number,Elevation,points)
    if Reverse == 'Reverse':
        df = PlanarDistanceBetweenPoints(df.sort_values(['Distance (m)'],ascending=False).reset_index(drop=True))
    plt.plot(df['Distance (m)'], df['Max'], '-',color='r',linewidth=0.5)
    plt.plot(df['Distance (m)'], df['Mean'], '-',color='y',linewidth=0.5)
    plt.plot(df['Distance (m)'], df['Min'], '-',color='g',linewidth=0.5)
    plt.plot(df['Distance (m)'], df['z'], '-',label='Spillway',color='k')
    # Uncomment to add labels
    """for index, row in df.iterrows():
        X = df.iat[index,3]
        Y = df.iat[index,2]
        plt.annotate(index,xy=(X,Y), xytext=(5, 5), ha='right',
                    textcoords='offset points')"""
    plt.gca().set_aspect('equal', adjustable='box')
    lgd = plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title(Name)
    plt.ylabel('Elevation (mAOD)')
    plt.xlabel('Distance Along Line (m)')
    if Images == 'Y':
        print('Saving Image')
        plt.savefig(folder+"\\"+"Output"+"\\"+Name+'.png', dpi=2000, bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.show()
    #print(df)
    return df
    
def PlotWaterLevelChange(points,Name,critical,ylabel):
    Elevation = list(coordse)[4:]
    numbers = re.compile('\d+(?:\.\d+)?')
    wl = points.iloc[:,-len(Elevation):].copy()
    wl = wl.transpose()
    for i in range(len(Elevation)):
        Elevation[i] = float(''.join(numbers.findall(Elevation[i])))/1000
    Elevation.sort()
    wl = wl.set_index([Elevation])
    wl.plot()
    if type(critical) == int or type(critical) == float:
        wl['Critical'] = critical
        wl['Critical'].plot(color="red", linewidth=2.5, linestyle="--")
    #plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.legend([])
    plt.title(Name)
    plt.ylabel(ylabel)
    plt.xlabel('Time (s)')
    if Images == 'Y':
        print('Saving Image')
        plt.savefig(folder+"\\"+"Output"+"\\"+Name+'.png', dpi=2000, bbox_inches='tight',pad_inches=0.5)
    plt.show()

###########
# Outputs #
###########

# Plot water levels
coordse = pd.read_csv(folder+"\\"+"Output"+"\\"+"coordse"+".csv",index_col=0)
df = PlotWaterLevel(folder,coordse,"Centreline Water Elevation",Images,None)

rwe = pd.read_csv(folder+"\\"+"Output"+"\\"+"rwe"+".csv",index_col=0)
PlotWaterLevel(folder,rwe,"Right Wall Water Elevation",Images,"Reverse")

lwe = pd.read_csv(folder+"\\"+"Output"+"\\"+"lwe"+".csv",index_col=0)
PlotWaterLevel(folder,lwe,"Left Wall Water Elevation",Images,None)

coordse = pd.read_csv(folder+"\\"+"Output"+"\\"+"coordse"+".csv",index_col=0)
PlotWaterLevelChange(coordse,"Centreline Elevation Convergence",146.50,"Elevation (mAOD)")

coordsu = pd.read_csv(folder+"\\"+"Output"+"\\"+"coordsu"+".csv",index_col=0)
PlotWaterLevelChange(coordsu,"Centreline Velocity Convergence",None,"Velocity (m/s)")









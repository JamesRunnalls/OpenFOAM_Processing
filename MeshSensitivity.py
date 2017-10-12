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
coarse = r"V:\j24130900\OpenFoam\Run\PU_Combined_Coarse"
main = r"V:\j24130900\OpenFoam\Run\PU_Combined"
fine = r"V:\j24130900\OpenFoam\Run\PU_Combined_Fine"

# Export images (Y/N)
Images = "Y"

# Number of vtk's to use for average, min and max values.
Number = 50

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

def LoadFiles(folder,name,Number):
    x = pd.read_csv(folder+"\\"+"Output"+"\\"+name+".csv",index_col=0)
    y = os.listdir(folder+"\\"+"Elevation")
    x = MinMaxMean(Number,y,x)
    return x

def PlotMeshSensitivity(coarse,main,fine,Number):
    ce = LoadFiles(coarse,"coordse",Number)
    me = LoadFiles(main,"coordse",Number)
    fe = LoadFiles(fine,"coordse",Number)
    cu = LoadFiles(coarse,"coordsu",Number)
    mu = LoadFiles(main,"coordsu",Number)
    fu = LoadFiles(fine,"coordsu",Number)
    plt.figure()
    plt.subplot(211)
    plt.plot(ce['Distance (m)'], ce['Mean'], '-',label='Coarse',linewidth=0.5)
    plt.plot(me['Distance (m)'], me['Mean'], '-',label='Medium',linewidth=0.5)
    plt.plot(fe['Distance (m)'], fe['Mean'], '-',label='Fine',linewidth=0.5)
    plt.plot(fe['Distance (m)'], fe['z'], '-', label='Spillway', color='k')
    plt.gca().set_aspect('equal', adjustable='box')
    lgd = plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title("Centreline Water Elevation")
    plt.ylabel('Elevation (mAOD)')
    plt.xlabel('Distance Along Line (m)')
    plt.subplot(212)
    plt.plot(cu['Distance (m)'], cu['Mean'], '-',label='Coarse',linewidth=0.5)
    plt.plot(mu['Distance (m)'], mu['Mean'], '-',label='Medium',linewidth=0.5)
    plt.plot(fu['Distance (m)'], fu['Mean'], '-',label='Fine',linewidth=0.5)
    lgd = plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title('Centreline Water Velocity')
    plt.ylabel('Velocity (m/s)')
    plt.xlabel('Distance Along Line (m)')
    if Images == 'Y':
        print('Saving Image')
        plt.savefig(main+"\\"+"Output"+"\\"+"MeshSensitivity"+'.png', dpi=2000, bbox_extra_artists=(lgd,), bbox_inches='tight',pad_inches=0.5)
    plt.show()

#############
# Main Code # 
#############

font = {'family' : 'serif',
        'weight' : 'normal',
        'size'   : '8'}

plt.rc('font', **font)  # pass in the font dict as kwargs


PlotMeshSensitivity(coarse,main,fine,Number)

















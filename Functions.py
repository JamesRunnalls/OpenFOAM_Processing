
# coding: utf-8

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re

# Functions #

def LoadCSV(name,folder):
    return pd.read_csv(folder+"\\"+"Output"+"\\"+name+".csv",index_col=0)

def TimeSeriesStatistics(Number,points,sensitivity):
    df = points.iloc[:,-min(Number,len(list(points)[4:])):].copy()
    twl = pd.DataFrame(np.sort(df.values)[:,-3:], columns=['3','2','1'])
    points = points.iloc[:,0:4].copy()
    conditions = [
    ((twl['1'] - twl['2']) <= sensitivity),
    ((twl['1'] - twl['2']) > sensitivity) & ((twl['2'] - twl['3']) <= sensitivity),
    ((twl['1'] - twl['2']) > sensitivity) & ((twl['2'] - twl['3']) >= sensitivity)]                              
    choices = [twl['1'],twl['2'],twl['3']]
    points['Mean'] = df.mean(axis=1)
    points['Max'] = df.max(axis=1)
    points['Min'] = df.min(axis=1)
    points['75% Percentile'] = df.quantile(.75,1)
    points['25% Percentile'] = df.quantile(.25,1)
    points['Top Water Level'] = np.select(conditions, choices, default=twl['1'])
    points['Air Bulking Level'] = points['Top Water Level']+((points['Top Water Level']-points['z'])*0.2)
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
        return points
    except:
        print("Either points do not exist or have been formatted incorrectly")

def PlotWaterLevel(folder,points,Name,Images,Reverse,Number,dots,sensitivity):
    points = LoadCSV(points,folder)
    df = TimeSeriesStatistics(Number,points,sensitivity)
    if Reverse == 'Reverse':
        df = PlanarDistanceBetweenPoints(df.sort_values(['Distance (m)'],ascending=False).reset_index(drop=True))
        points = PlanarDistanceBetweenPoints(points.sort_values(['Distance (m)'],ascending=False).reset_index(drop=True))
    fig = plt.figure(figsize=(10, 5))
    #plt.plot(df['Distance (m)'], df['Max'], '-',color='r',linewidth=0.5)
    plt.plot(df['Distance (m)'], df['Top Water Level'], '-',color='r',linewidth=0.5)
    plt.plot(df['Distance (m)'], df['Air Bulking Level'], '--',color='k',linewidth=0.5)
    #plt.plot(df['Distance (m)'], df['75% Percentile'], '-',color='r',linewidth=0.5)
    #plt.plot(df['Distance (m)'], df['Mean'], '-',color='y',linewidth=0.5)
    #plt.plot(df['Distance (m)'], df['Min'], '-',color='g',linewidth=0.5)
    #plt.plot(df['Distance (m)'], df['25% Percentile'], '-',color='g',linewidth=0.5)
    plt.plot(df['Distance (m)'], df['z'], '-',label='Spillway',color='k')
    # Uncomment to add labels
    """for index, row in df.iterrows():
        X = df.iat[index,3]
        Y = df.iat[index,2]
        plt.annotate(index,xy=(X,Y), xytext=(5, 5), ha='right',
                    textcoords='offset points')"""
    lgd = plt.legend(loc='center left', bbox_to_anchor=(1, 0.5),framealpha=0)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.tight_layout(rect=[0.1,0,0.75,1])
    if (type(dots)==int) == True: 
        for x in list(points)[4:][-dots:]:
            plt.plot(df['Distance (m)'], points[x], '.')
    plt.title(Name)
    plt.ylabel('Elevation (mAOD)')
    plt.xlabel('Distance Along Line (m)')
    if Images == 'Y':
        print('Saving Image')
        plt.savefig(folder+"\\"+"Output"+"\\"+Name+'.png', dpi=2000, bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.show()
    return df,fig
    
def PlotWaterLevelChange(folder,points,Name,critical,ylabel,Images):
    points = LoadCSV(points,folder)
    Elevation = list(points)[4:]
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
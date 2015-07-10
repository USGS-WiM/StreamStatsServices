import sys
import traceback
#import datetime
import os
import argparse
import arcpy
#import shutil
import json
#from arcpy.sa import *
#import arcpy.cartography as CA
#import logging
#import re


##-------1---------2---------3---------4---------5---------6---------7---------8
##       Main
##-------+---------+---------+---------+---------+---------+---------+---------+
class DelineationWrapper(object):
    #region Constructor
    def __init__(self):
        regionID =""
        pourpoint= None
        simplification = 1
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument("-directory", help="specifies the projects working directory", type=str, default = r"D:\gistemp\ClientData")
            parser.add_argument("-stabbr", help="specifies the abbr state name to perform delineation", type=str, default="IA")
            parser.add_argument("-pourpoint", help="specifies the json representation of an esri point feature collection ", type=json.loads, 
                                default = '[-93.7364137172699,42.306129898064221]')
            parser.add_argument("-pourpointwkid", help="specifies the esri well known id of pourpoint ", type=str, 
                                default = '4326')
          
            parser.add_argument("-simplification", help="specifies the simplify method to, 1 = full, 2 = simplified", type=int, choices=[1,2], default = 1)
            parser.add_argument("-processSR", help="specifies the spatial ref to perform operation", type=int, default = 4326)
                
            args = parser.parse_args()

            Results={"Message": "INFO:Initialized_INFO:Delineation Started_INFO:creating workspace environment. D:\\gistemp\\ClientData\\IA20150709101147001000\\IA20150709101147001000.gdb_INFO:Starting Delineation_AHMSG:Executing: StreamstatsGlobalWatershedDelineation in memory\\FC D:\\gistemp\\ClientData\\IA20150709101147001000\\IA20150709101147001000.gdb\\Layers\\GlobalWatershed D:\\gistemp\\ClientData\\IA20150709101147001000\\IA20150709101147001000.gdb\\Layers\\GlobalWatershedPoint D:\\gistemp\\ClientData\\IA20150709101147001000\\Temp\\StreamStatsIA.xml CLEARFEATURES NO IA20150709101147001000 Start Time: Thu Jul 09 10:11:55 2015 Delineating global watershed for batchpoint 1 of 1.  dt=0.03s 1 global watershed(s) successfully delineated. Succeeded at Thu Jul 09 10:12:03 2015 (Elapsed Time: 8.00 seconds)_INFO:Finished_", "Workspace": "IA20150709101147001000"}
        
        except:
             tb = traceback.format_exc()
             Results = {
                       "error": {"message": traceback.format_exc()}
                       }

        finally:
            print "Results="+json.dumps(Results) 

if __name__ == '__main__':
    DelineationWrapper()

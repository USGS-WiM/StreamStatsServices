import sys
import traceback
import os
import argparse
import arcpy
import shutil
import json
import logging
#import ArcHydroTools
import xml.dom.minidom
import decimal

##-------1---------2---------3---------4---------5---------6---------7---------8
##       Main
##-------+---------+---------+---------+---------+---------+---------+---------+        
class BasinParametersWrapper(object):
    #region Constructor
        def __init__(self):
            try:
                parser = argparse.ArgumentParser()
                parser.add_argument("-stabbr", help="specifies the state abbreviation", type=str, default="IA")
                parser.add_argument("-workspaceID", help="specifies the working folder", type=str, default="IA20141112093901899000")
                parser.add_argument("-parameters", help="specifies the ';' separated list of parameters to be computed", type=str, default = "DRNAREA;KSATSSUR;I24H10Y;CCM;TAU_ANN;STREAM_VAR;PRECIP;HYSEP;RSD")
                parser.add_argument("-directory", help="specifies the projects working directory", type=str, default = r"D:\gistemp\ClientData")
                args = parser.parse_args()
                
                Results = {"Message": "INFO:D:\\gistemp\\ClientData\\ME20150616080458803000\\ME20150616080458803000.gdb\\Layers exists_INFO:workspace set: ME20150616080458803000_INFO:Stated calc params_AHMSG:Executing: StreamstatsGlobalParametersServer D:\\gistemp\\ClientData\\ME20150616080458803000\\ME20150616080458803000.gdb\\Layers\\GlobalWatershedRaw D:\\gistemp\\ClientData\\ME20150616080458803000\\ME20150616080458803000.gdb\\Layers\\GlobalWatershedPoint PRECIP;PRDECFEB90;SANDGRAVAP;COASTDIST D:\\gistemp\\ClientData\\ME20150616080458803000\\Temp\\parameterFile.xml D:\\gistemp\\ClientData\\ME20150616080458803000\\Temp\\parameterFile.htm D:\\gistemp\\ClientData\\ME20150616080458803000\\Temp\\StreamStatsME.xml # ME20150616080458803000 Start Time: Tue Jun 16 11:52:02 2015 Performing global parameters computation... Succeeded at Tue Jun 16 11:52:07 2015 (Elapsed Time: 5.00 seconds)_INFO:finished calc params_INFO:parsing xml_INFO:finished_", "Parameters": [{"code": "CENTROIDX", "value": "497971.18"}, {"code": "CENTROIDY", "value": "5099424.03"}, {"code": "PRECIP", "value": "43.7"}, {"code": "PRDECFEB90", "value": "8.56"}, {"code": "SANDGRAVAP", "value": "0.00"}, {"code": "COASTDIST", "value": "146"}]}

            except:
                Results = {"error":traceback.format_exc()}

            finally:
                print "Results="+json.dumps(Results)   
    #endregion 
   

# specifies that this class can be ran directly
if __name__ == '__main__':
    BasinParametersWrapper()

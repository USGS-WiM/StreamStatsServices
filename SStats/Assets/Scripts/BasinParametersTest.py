import sys
import traceback
import os
import argparse
import arcpy
import shutil
import json
import logging
import ArcHydroTools
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
                
                Results = {"Message": "INFO:D:\\gistemp\\ClientData\\IA20141201131238376000\\IA20141201131238376000.gdb\\Layers exists_INFO:workspace set: IA20141201131238376000_INFO:Stated calc params_AHMSG:Executing: StreamstatsGlobalParametersServer D:\\gistemp\\ClientData\\IA20141201131238376000\\IA20141201131238376000.gdb\\Layers\\GlobalWatershed D:\\gistemp\\ClientData\\IA20141201131238376000\\IA20141201131238376000.gdb\\Layers\\GlobalWatershedPoint DRNAREA;KSATSSUR;I24H10Y;CCM;TAU ANN;STREAM VAR;PRECIP;HYSEP;RSD D:\\gistemp\\ClientData\\IA20141201131238376000\\Temp\\parameterFile.xml D:\\gistemp\\ClientData\\IA20141201131238376000\\Temp\\parameterFile.htm D:\\gistemp\\ClientData\\IA20141201131238376000\\Temp\\StreamStatsIA.xml # IA20141201131238376000 Start Time: Mon Dec 01 14:14:22 2014 Performing global parameters computation... OID: 1\r Error when computing parameter FOS for the  watershed: \r E:\\ss data\\ia\\archydro\\07080105\\07080105.gdb\\Layers\\nhd fos\r D:\\gistemp\\ClientData\\IA20141201131238376000\\Temp\\IA20141201131238376000\\StreamsCountTmp\r ERROR 000210: Cannot create output C:\\Users\\JKNEWS~1\\AppData\\Local\\Temp\\4\\\\scratch.gdb\\DAStreamSJ\r Failed to execute (Spatial Join).\r Failed to execute (StreamsCount).. Succeeded at Mon Dec 01 14:14:26 2014 (Elapsed Time: 4.00 seconds)_INFO:finished calc params_INFO:parsing xml_INFO:finished_", "Parameters": [{"code": "DRNAREA", "value": "0.31"}, {"code": "STRMTOT", "value": "0.000"}, {"code": "FOS", "value": ""}, {"code": "KSATSSUR", "value": "4.61"}, {"code": "I24H10Y", "value": "4.44"}, {"code": "CCM", "value": "-99999.00"}, {"code": "TAU_ANN", "value": "20.39"}, {"code": "STREAM_VAR", "value": "0.66"}, {"code": "PRECIP", "value": "33.87"}, {"code": "HYSEP", "value": "53.95"}, {"code": "RSD", "value": ""}]}

            except:
                Results = {"error":traceback.format_exc()}

            finally:
                print "Results="+json.dumps(Results)   
    #endregion 
   

# specifies that this class can be ran directly
if __name__ == '__main__':
    BasinParametersWrapper()

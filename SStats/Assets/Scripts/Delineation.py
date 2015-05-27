#------------------------------------------------------------------------------
#----- Delineation.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2014 WiM - USGS

#    authors:  Jeremy K. Newson USGS Wisconsin Internet Mapping
# 
#   purpose:  GlobalDelineation <STABBR> <PourPoint> <GlobalWatershedPoint> <GlobalWatershed>
#          
#discussion:  Adapted from John Guthrie's GetGW12.py Global delineation script
#       

#region "Comments"
#11.05.2014 jkn - Created/ Adapted from John Guthrie's getGW12.py
#endregion

#region "Imports"
import sys
import traceback
import datetime
import os
import argparse
import arcpy
import shutil
import json
import ArcHydroTools
from arcpy.sa import *
import arcpy.cartography as CA
import logging
import re

import xml.dom.minidom
#endregion

class Delineation(object):
    #region Constructor
    def __init__(self, regionID, directory):
        
        self.Watershed = None
        self.PourPoint = None        
        self.Message =""
        self.__schemaPath__ = r"D:\ss_socs\ss_gp\schemas"
        self.__xmlPath__ = r"D:\ss_apps\XML" 

        self.__regionID__ = regionID
        self.__templatePath__ = os.path.join(self.__schemaPath__,self.__regionID__ + "_ss.gdb","Layers",'{0}' + self.__regionID__)
        self.WorkspaceID = self.__regionID__ + str(datetime.datetime.now()).replace('-','').replace(' ','').replace(':','').replace('.','')
        self.__WorkspaceDirectory__ = self.__getDirectory__(os.path.join(directory, self.WorkspaceID))

        self.__TempLocation__ = os.path.join(self.__WorkspaceDirectory__, "Temp")

        #set up logging
        logdir = os.path.join(self.__TempLocation__, 'delineation.log')
        logging.basicConfig(filename=logdir, format ='%(asctime)s %(message)s', level=logging.DEBUG)

        self.__sm__("Initialized")         
    #endregion   
        
    #region Methods   
    def Delineate(self, processSR, PourPoint, simplificationType):
        xmlPath =''
        datasetPath = ''
        featurePath=''

        sr = None
        GWP = None
        GW = None
        elimGW = None
        result = None

        try:
            arcpy.env.overwriteOutput = True
            arcpy.env.workspace = self.__TempLocation__
            arcpy.env.scratchWorkspace = self.__TempLocation__
            
            sr = arcpy.SpatialReference(int(processSR))

            self.__sm__("Delineation Started") 
            datasetPath = arcpy.CreateFileGDB_management(self.__WorkspaceDirectory__, self.WorkspaceID +'.gdb')[0]
            featurePath = arcpy.CreateFeatureDataset_management(datasetPath,'Layers', sr)[0]

            self.__sm__("creating workspace environment. "+ datasetPath)
            
            GWP = arcpy.CreateFeatureclass_management(featurePath, "GlobalWatershedPoint", "POINT", 
                                                      self.__templatePath__.format("GlobalWatershedPoint") , "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE", sr)
            GW = arcpy.CreateFeatureclass_management(featurePath, "GlobalWatershedRaw", "POLYGON", 
                                                     self.__templatePath__.format("GlobalWatershed"), "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE", sr)
            
            xmlPath = self.__SSXMLPath__("StreamStats{0}.xml".format(self.__regionID__), self.__TempLocation__, self.__TempLocation__)
                        
            arcpy.CheckOutExtension("Spatial")
            self.__sm__("Starting Delineation")
            ArcHydroTools.StreamstatsGlobalWatershedDelineation(PourPoint, GW, GWP, xmlPath , "CLEARFEATURES_NO", self.WorkspaceID)
            self.__sm__(arcpy.GetMessages(),'AHMSG')
            arcpy.CheckInExtension("Spatial")

            self.__sm__("finished Delineation., removing holes")
            #remove holes  
            result = self.__removePolygonHoles__(GW,featurePath,sr)

            if simplificationType == 2:
                result = self.__getSimplifiedPolygon__(result,featurePath)
                self.__sm__("Watershed simplified") 

            self.Watershed = self.__ToJSON__(result)
            self.PourPoint = self.__ToJSON__(GWP)

            self.__sm__("Finished")
        except:
            tb = traceback.format_exc()
            self.__sm__("Delineation Error "+tb,"ERROR")

        finally:
            #Local cleanup
            del result
            del elimGW
            del GWP
            del GW
            del sr            
            arcpy.Delete_management(PourPoint)
            #arcpy.Delete_management(self.__TempLocation__)
    #endregion  
      
    #region Helper Methods
    def __removePolygonHoles__(self, polyFC, path, sr):
        try:
            elimGW = arcpy.CreateFeatureclass_management(path, "GlobalWatershed", "POLYGON", 
                                                         self.__templatePath__.format("GlobalWatershed"), "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE", sr)

            result = arcpy.EliminatePolygonPart_management(polyFC, elimGW, "AREA_OR_PERCENT", "1000 squaremeters", 1, "CONTAINED_ONLY")

            self.__sm__(arcpy.GetMessages())
            return result
        except:
            tb = traceback.format_exc()
            self.__sm__("Error removing holes "+tb,"ERROR")
            return polyFC
            
    def __getDirectory__(self, subDirectory, makeTemp = True):
        try:
            if os.path.exists(subDirectory): 
                shutil.rmtree(subDirectory)
            os.makedirs(subDirectory);

            #temp dir
            if makeTemp:
                os.makedirs(os.path.join(subDirectory, "Temp"))
 

            return subDirectory
        except:
            x = arcpy.GetMessages()
            return subDirectory

    def __SSXMLPath__(self, xmlFileName, copyToDirectory="#", newTempWorkspace = "#"):
        file = None
        try:
            #move the file to tempDirectory
            xmlFile = os.path.join(self.__xmlPath__, xmlFileName)
            if copyToDirectory != "#":
                shutil.copy(xmlFile, copyToDirectory)
                xmlFile = os.path.join(copyToDirectory,xmlFileName)

            if newTempWorkspace == "#":
                return xmlFile

            #update tempworkspace
            xmlDoc = xml.dom.minidom.parse(xmlFile)
            xmlDoc.getElementsByTagName('TempLocation')[0].firstChild.data = newTempWorkspace
            file = open(xmlFile,"wb")
            xmlDoc.writexml(file)

            return xmlFile
        except:
             tb = traceback.format_exc()
             self.__sm__(tb,"ERROR")
        finally:
            if file != None and not file.closed: 
                file.close 
                file = None

    def __ToJSON__(self, fClass):
        featSet = None
        try:
            featSet = arcpy.FeatureSet()
            featSet.load(fClass)
            jsonStr = arcpy.Describe(featSet).json

            return json.loads(jsonStr)
        except:
            tb = traceback.format_exc()
            self.__sm__("Failed to serialize " + tb,"ERROR")

    def __getSimplifiedPolygon__(self, PolygonFC, directory):
        tolerance = 10
        try:
            
            self.__sm__("Simplifying Watershed")
            numVerts = self.__getVerticesCount__(PolygonFC)
            self.__sm__("Number of vertices: " + str(numVerts))            
            if numVerts < 100:      
                #no need to simplify
                return PolygonFC
            elif numVerts < 1000:
                tolerance = 10
            elif numVerts < 2000:
                tolerance = 20
            else:
                tolerance = 30
                      
            self.__sm__("Tolerance: "+str(tolerance))
            simplifiedGW = CA.SimplifyPolygon(PolygonFC, os.path.join(directory,"simplifiedGW"), "POINT_REMOVE", str(tolerance) +" Feet", 0, "RESOLVE_ERRORS", "KEEP_COLLAPSED_POINTS")
            self.__sm__(arcpy.GetMessages()) 
            return simplifiedGW[0]

        except:  
            tb = traceback.format_exc()                  
            self.__sm__("Error Simplifying: " + tb,"ERROR")

            return PolygonFC
        
    def __getVerticesCount__(self, polyFC):
        rtn = 0
        try:
            arcpy.AddField_management(polyFC, "numVert", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
            arcpy.CalculateField_management(polyFC, "numVert", "!shape.pointcount!", "PYTHON_9.3", "")
            with arcpy.da.SearchCursor(polyFC, ("numVert")) as cursor:
                for row in cursor:
                    if row[0] > rtn:
                        rtn= row[0]
            return rtn
        except:
            return -1

    def __sm__(self, msg, type = 'INFO'):
        self.Message += type +':' + msg.replace('_',' ') + '_'

        if type in ('ERROR'): logging.error(msg)
        else : logging.info(msg)
    #endregion


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

            regionID = args.stabbr
            if regionID == '#' or not regionID:
                raise Exception('Input Study Area required')
            
            ppoint = self.__JsonToFeature__(args.pourpoint,args.pourpointwkid);

            simplification = args.simplification
            if simplification == '#' or not simplification:
                simplification = 1

            ssdel = Delineation(regionID, args.directory)
            ssdel.Delineate(args.processSR, ppoint, simplification)

            Results = {
                       "Workspace": ssdel.WorkspaceID,
                       "Watershed":ssdel.Watershed,
                       "PourPoint": ssdel.PourPoint,
                       "Message": ssdel.Message.replace("'",'"').replace('\n',' ')
                      }

        except:
             tb = traceback.format_exc()
             Results = {
                       "error": {"message": traceback.format_exc()}
                       }

        finally:
            print "Results="+json.dumps(Results) 

    def __JsonToFeature__(self, ppt, wkid):
        rows = None
        try:
            #get spatial ref
            wkid = int(wkid)
            sr = arcpy.SpatialReference(wkid)
            pourPoint = {"type":"Point","coordinates":ppt}
            
            #Final result Feature Class
            #FC = arcpy.CreateFeatureclass_management("in_memory", "FC", "POINT", "", "DISABLED", "DISABLED", sr, "", "0", "0", "0")
            FC = arcpy.CreateFeatureclass_management("in_memory", "FC", "POINT", spatial_reference=sr)

            #add required attributes
            arcpy.AddField_management(FC, "Name", "TEXT", field_length=50)
            arcpy.AddField_management(FC, "Descript", "TEXT", field_length=200)
            arcpy.AddField_management(FC, "BatchDone", "SHORT")
            arcpy.AddField_management(FC, "SnapOn", "SHORT")
            arcpy.AddField_management(FC, "SrcType", "SHORT")
            # Create insert cursor for table

            rows = arcpy.InsertCursor(FC)            
            #add the json geometry to row
            row = rows.newRow()
            row.shape = arcpy.AsShape(pourPoint)

            #add value to field
            row.setValue("Name", "ags101")
            row.setValue("Descript", "")
            row.setValue("BatchDone", 0)
            row.setValue("SnapOn", 1)
            row.setValue("SrcType", 0)

            rows.insertRow(row)

            return FC
        except:
            tb = traceback.format_exc()
            print tb
        finally:
            #local cleanup
            del row
            del rows

if __name__ == '__main__':
    DelineationWrapper()


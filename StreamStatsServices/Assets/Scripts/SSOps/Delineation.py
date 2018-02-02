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
#08.19.2015 jkn - fixed hucid sync issue. By removing createfeature in __removePolygonHoles__
#08.07.2015 jkn - modified to store in local projection
#11.05.2014 jkn - Created/ Adapted from John Guthrie's getGW12.py
#endregion

#region "Imports"
import sys
import traceback
import datetime
import os
import arcpy
import ArcHydroTools
from arcpy.sa import *
#endregion

class Delineation(object):
    #region Constructor
    def __init__(self, regionID, directory):
        self.Message =""
        self.__schemaPath__ = r"D:\ss_socs\ss_gp\schemas"
        self.__xmlPath__ = r"D:\ss_apps\XML" 
        self.__regionID__ = regionID        
        self.__templatePath__ = os.path.join(self.__schemaPath__,self.__regionID__ + "_ss.gdb","Layers")
        self.WorkspaceID = self.__regionID__ + str(datetime.datetime.now()).replace('-','').replace(' ','').replace(':','').replace('.','')
        self.__WorkspaceDirectory__ = self.__getDirectory__(os.path.join(directory, self.WorkspaceID))

        self.__TempLocation__ = os.path.join(self.__WorkspaceDirectory__, "Temp")

        #set up logging
        logdir = os.path.join(self.__TempLocation__, 'delineation.log')
        logging.basicConfig(filename=logdir, format ='%(asctime)s %(message)s', level=logging.DEBUG)

        self.__sm__("Initialized")         
    #endregion   
        
    #region Methods   
    def Delineate(self, PourPoint):
        xmlPath =''
        datasetPath = ''
        featurePath=''
        templateFeaturePath=''
        sr = None
        GWP = None
        GW = None

        try:
            arcpy.env.overwriteOutput = True
            arcpy.env.workspace = self.__TempLocation__
            arcpy.env.scratchWorkspace = self.__TempLocation__

            templateFeaturePath=os.path.join(self.__templatePath__,'{0}' + self.__regionID__)

            sr = arcpy.Describe(self.__templatePath__).spatialReference
            self.__sm__("Template spatial ref: "+ sr.name)

            self.__sm__("Delineation Started") 
            datasetPath = arcpy.CreateFileGDB_management(self.__WorkspaceDirectory__, self.WorkspaceID +'.gdb')[0]
            featurePath = arcpy.CreateFeatureDataset_management(datasetPath,'Layers', sr)[0]

            self.__sm__("creating workspace environment. "+ datasetPath)
            
            GWP = arcpy.CreateFeatureclass_management(featurePath, "GlobalWatershedPoint", "POINT", 
                                                      templateFeaturePath.format("GlobalWatershedPoint") , "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE",sr)
            GW = arcpy.CreateFeatureclass_management(featurePath, "GlobalWatershedTemp", "POLYGON", 
                                                     templateFeaturePath.format("GlobalWatershed"), "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE",sr)
            
            xmlPath = self.__SSXMLPath__("StreamStats{0}.xml".format(self.__regionID__), self.__TempLocation__, self.__TempLocation__)
                        
            arcpy.CheckOutExtension("Spatial")
            self.__sm__("Starting Delineation")

            ArcHydroTools.StreamstatsGlobalWatershedDelineation(PourPoint, GW, GWP, xmlPath , "CLEARFEATURES_NO", self.WorkspaceID)
            self.__sm__(arcpy.GetMessages(),'AHMSG')

            #remove holes  
            self.__removePolygonHoles__(GW,featurePath)
            arcpy.CheckInExtension("Spatial")
            
            self.__sm__("Finished")
        except:
            tb = traceback.format_exc()
            self.__sm__("Delineation Error "+tb,"ERROR")

        finally:
            #Local cleanup
            del GWP
            del sr            
            arcpy.Delete_management(PourPoint)
            arcpy.Delete_management(GW)
            #arcpy.Delete_management(self.__TempLocation__)
    #endregion  
      
    #region Helper Methods
    def __removePolygonHoles__(self, polyFC, path):
        try:

            result = arcpy.EliminatePolygonPart_management(polyFC, os.path.join(path,"GlobalWatershed"), "AREA_OR_PERCENT", "90 squaremeters", 1, "ANY")#modified CONTAINED_ONLY

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
    def __sm__(self, msg, type = 'INFO'):
        self.Message += type +':' + msg.replace('_',' ') + '_'

        if type in ('ERROR'): logging.error(msg)
        else : logging.info(msg)
    #endregion

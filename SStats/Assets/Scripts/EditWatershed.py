#------------------------------------------------------------------------------
#----- Delineation.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2014 WiM - USGS

#    authors:  Jeremy K. Newson USGS Wisconsin Internet Mapping
# 
#   purpose:  edit watershed
#          
#discussion:  Steps
#               1) Clip edits to local huc, add message
#               2) Create new workspace
#               3) Add appended areas
#               4) Clip removed areas
#       

#region "Comments"
#11.24.2015 jkn - Created

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
from arcpy.sa import *
import logging
import re

#endregion


class EditWatershed(object):
    #region Constructor
    def __init__(self, directory, workspaceid):
        
        self.Features = []        
        self.FeaturesList=[]
        self.Message =""
        self.IsValid = False

        regionID = workspaceid[:-20].upper()
        self.__MainDirectory__ = os.path.join(directory,workspaceid)

        self.WorkspaceID = regionID + str(datetime.datetime.now()).replace('-','').replace(' ','').replace(':','').replace('.','')
        self.__WorkspaceDirectory__ = self.__getDirectory__(os.path.join(directory, self.WorkspaceID))

        self.__TempDirectory__ = os.path.join(self.__WorkspaceDirectory__, "Temp")

        #set up logging
        logdir = os.path.join(self.__TempDirectory__, 'EditWatershed.log')
        logging.basicConfig(filename=logdir, format ='%(asctime)s %(message)s', level=logging.DEBUG)

         #Test if workspace exists before run   
        if(not self.__workspaceExists__(os.path.join(self.__MainDirectory__, workspaceid+".gdb","Layers"))):   
            self.__sm__("workspace: "+ os.path.join(self.__MainDirectory__, self.WorkspaceID+".gdb","Layers") + " does not exist", "ERROR")
            return
        
        self.GlobalWatershed = os.path.join(os.path.join(self.__MainDirectory__, workspaceid+".gdb","Layers","GlobalWatershed"))
        
        if(arcpy.Exists(self.GlobalWatershed)):  
            sr = arcpy.Describe(os.path.join(self.__MainDirectory__, workspaceid+".gdb","Layers")).spatialReference    
            self.DatasetPath = arcpy.CreateFileGDB_management(self.__WorkspaceDirectory__, self.WorkspaceID +'.gdb')[0]
            self.FeaturePath =featurePath = arcpy.CreateFeatureDataset_management(self.DatasetPath,'Layers', sr)[0]
            self.IsValid = True
            arcpy.env.workspace =  self.DatasetPath
            self.__sm__("Initialized")     
    #endregion   
        
    #region Methods   
   
    def EditWatershed(self, featurelist, method = 'append', espg = 4326):
        list = []
        geometries = "in_memory\\lstHSUnionGeom"
        merged = "in_memory\\mergedFeature"
        try:
            for jobj in featurelist:
                list.append(self.__getPolygon__(jobj,espg))
            
            arcpy.Union_analysis(list,geometries)
           
            if(method =="append"):
                arcpy.Merge_management([self.GlobalWatershed, geometries],merged)
                arcpy.Dissolve_management(merged, os.path.join(self.__WorkspaceDirectory__, self.WorkspaceID+".gdb","Layers","GlobalWatershed"))   
            else:
                var = bla
                arcpy.Erase_analysis(os.path.join(self.__WorkspaceDirectory__, self.WorkspaceID+".gdb","Layers","GlobalWatershed"), list,os.path.join(self.__WorkspaceDirectory__, self.WorkspaceID+".gdb","Layers","GlobalWatershederase"))      
   
        except:
            tb = traceback.format_exc()
            self.__sm__("Failed to include feature " + tb,"ERROR") 
        finally:
            if(geometries != None): arcpy.Delete_management(geometries)
            if(merged != None): arcpy.Delete_management(merged)
   
    #endregion  
      
    #region Helper Methods
    def __getDirectory__(self, subDirectory, makeTemp = True, template=None):
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

    def __workspaceExists__(self, workspace):
         return arcpy.Exists(workspace)      
         
    def __toProjection__(self, inFeature, toCRS):
        sr = None  
        fromCRS = None
        desc = None  
        projectedFC = None        
        try:
            sr = arcpy.SpatialReference(int(toCRS))
            desc = arcpy.Describe(inFeature)
            fromCRS = desc.spatialReference.factoryCode
            projectFC = os.path.join(self.__TempDirectory__, desc.name +".shp")
            
            if arcpy.Exists(projectFC):
                self.__sm__("deleting old temp file")
                arcpy.Delete_management(projectFC)
            
            if sr.factoryCode == desc.spatialReference.factoryCode:
                return None
            self.__sm__("Projecting from: "+ str(fromCRS) + " To: " + str(toCRS))
            return arcpy.Project_management(inFeature,projectFC,sr)
        except:
            tb = traceback.format_exc()                  
            self.__sm__("Error Reprojecting: " + tb +" "+ arcpy.GetMessages(),"ERROR")
            return None
        finally:
            sr = None

    def __getPolygon__(self,jsonArray, crs):
        lst_part = []  
        for part in jsonArray["rings"]: 
            lst_pnt = []  
            for pnt in part:  
                lst_pnt.append(arcpy.Point(float(pnt[0]), float(pnt[1])))  
            lst_part.append(arcpy.Array(lst_pnt))  
        array = arcpy.Array(lst_part)  
        return arcpy.Polygon(array, crs)
                        
    def __sm__(self, msg, type = 'INFO'):
        self.Message += type +':' + msg.replace('_',' ') + '_'

        if type in ('ERROR'): logging.error(msg)
        else : logging.info(msg)
    #endregion


##-------1---------2---------3---------4---------5---------6---------7---------8
##       Main
##-------+---------+---------+---------+---------+---------+---------+---------+
class EditWatershedWrapper(object):
    #region Constructor
        def __init__(self):
            try:
                parser = argparse.ArgumentParser()
                parser.add_argument("-workspaceID", help="specifies the working folder", type=str, default="CO20151123081442060000")
                parser.add_argument("-directory", help="specifies the projects working directory", type=str, default = r"D:\gistemp\ClientData")
                parser.add_argument("-appendlist", help="specifies a list of polygons to append", type=json.loads, default =r'[{"rings":[[[-107.2679328918457,38.576604801999657],[-107.27145195007324,38.57647060127529],[-107.27173089981079,38.578248740526064],[-107.26780414581299,38.578835852310405],[-107.2679328918457,38.576604801999657]]]},{"rings":[[[-107.26870536804199,38.579708123814271],[-107.27303981781006,38.580546836424418],[-107.27003574371338,38.580999737161612],[-107.27181673049927,38.582157137181547],[-107.26756811141968,38.581217799460909],[-107.26870536804199,38.579708123814271]]]}]')
                parser.add_argument("-removelist", help="specifies a list of polygons to remove", type=json.loads, default = r'[{"rings":[[[-107.26634502410887,38.582056494441964],[-107.26722478866577,38.577779047643375],[-107.25879192352294,38.577342901502213],[-107.26149559020996,38.58120102546139],[-107.26634502410887,38.582056494441964]]]}]')#r'[{"rings":[[[-107.26634502410887,38.582056494441964],[-107.26722478866577,38.577779047643375],[-107.25879192352294,38.577342901502213],[-107.26149559020996,38.58120102546139],[-107.26634502410887,38.582056494441964]]],"spatialReference":{"wkid":4326}}]')
                parser.add_argument("-wkid", help="specifies the esri well known id of pourpoint ", type=str, default = '4326')
                args = parser.parse_args()

                ssedit = EditWatershed(args.directory, args.workspaceID)
                if(ssedit.IsValid):
                    ssedit.EditWatershed(args.appendlist,'append', args.wkid)
                    ssedit.EditWatershed(args.removelist,'remove', args.wkid)

                Results = {
                       "Workspace": ssedit.WorkspaceID,
                       "Message": ssedit.Message.replace("'",'"').replace('\n',' ')
                      }

            except:
                Results = {"Workspace": "Error", "Message":traceback.format_exc()}

            finally:
                print "Results="+json.dumps(Results)   
    #endregion    

# specifies that this class can be ran directly
if __name__ == '__main__':
    EditWatershedWrapper()




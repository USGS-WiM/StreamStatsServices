#------------------------------------------------------------------------------
#----- Features.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2018 WiM - USGS

#    authors:  Jeremy K. Newson USGS Wisconsin Internet Mapping
# 
#   purpose:  read/parse features and return as json
#          
#discussion:  
#       

#region "Comments"
#02.01.2018 jkn - Created
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
from SSOps.StreamStatsOpsBase import StreamStatsOpsBase as SSOpsBase
import arcpy.cartography as CA
import logging
import re

#endregion

class Features(SSOpsBase):
    #region Constructor
    def __init__(self,workspacePath,id):
        SSOpsBase.__init__(self,workspacePath)
        self.isValid = False
        self.WorkspaceID = id
        self.BoundingBox =[None,None,None,None]
        featurePath = os.path.join(self._WorkspaceDirectory, self.WorkspaceID+".gdb","Layers") 
        
        if(not arcpy.Exists(featurePath)):   
            self._sm("workspace: "+ featurePath + " does not exist", "ERROR")
            return
        arcpy.env.workspace=featurePath

        self.FeaturesList = self._getFeaturesList()
        self.isValid = True
        self._sm("initialized Features")
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        SSOpsBase.__exit__(self, exc_type, exc_value, traceback) 
    #endregion   
        
    #region Methods   
   
    def GetFeatures(self, featurelist='', crs = 4326, simplificationType=1):
        gwcopied = None
        features =[]
        try:
            if featurelist == '':
                raise Exception("List of desired features are required.")

            else:
                for f in map(lambda s: s.strip(), re.split("[,;\-!?:]+",featurelist)):
                    if f.lower() in self.FeaturesList:
                        feature = self._simplify(f,crs, simplificationType)
                        feature["id"] = f
                        features.append(feature)
                        #endif
                    #endif
                #next f
            return features
        except:
            tb = traceback.format_exc()
            self._sm("Failed to include feature " + tb,"ERROR") 
        finally:
            if gwcopied != None: arcpy.Delete_management(gwcopied)  
    def GetAvailableFeatures(self):
        availablefeatures =[]
        try:
            for fname in self.FeaturesList:
                availablefeatures.append(fname) 

            return availablefeatures
        except:
            tb = traceback.format_exc()
            self._sm("Failed to include available features " + tb,"ERROR") 
        finally:
            if gwcopied != None: arcpy.Delete_management(gwcopied)  
    #endregion  
      
    #region Helper Methods
    def _getFeaturesList(self):
        try:
            fl = []
            #open feature/ loop through and add to array
            for fc in arcpy.ListFeatureClasses():
                fl.append(fc.lower()) 
            return fl
        except:
            tb = traceback.format_exc()
            self._sm("Featurelist Error "+tb,"ERROR")
         
    def _toJSON(self, fClass, toGeojson=True):
        featSet = None
        file = None
        try:
            if(toGeojson):
                desc = arcpy.Describe(fClass)
                file = arcpy.FeaturesToJSON_conversion(fClass,os.path.join(self._WorkspaceDirectory,desc.name+".json"),None,None,None,"GEOJSON")[0]
                return json.load(open(file))['features'][0]
               
            else:
                featSet = arcpy.FeatureSet()
                featSet.load(fClass)
                jsonStr = arcpy.Describe(featSet).json
                return json.loads(jsonStr)
        except:
            tb = traceback.format_exc()
            self._sm("Failed to serialize " + tb,"ERROR")
        finally:
            if file != None: os.remove(file)
    
    def _toProjection(self, inFeature, toCRS):
        sr = None  
        fromCRS = None
        desc = None  
        projectedFC = None        
        try:
            sr = arcpy.SpatialReference(int(toCRS))
            desc = arcpy.Describe(inFeature)
            fromCRS = desc.spatialReference.name
            projectFC = os.path.join(self._TempLocation, desc.name +".shp")
            
            if arcpy.Exists(projectFC):
                self._sm("deleting old temp file")
                arcpy.Delete_management(projectFC)
            
            if sr.name == desc.spatialReference.name:
                return None
            self._sm("Projecting from: "+ str(fromCRS) + " To: " + str(sr.name))
            return arcpy.Project_management(inFeature,projectFC,sr)
        except:
            tb = traceback.format_exc()                  
            self._sm("Error Reprojecting: " + tb +" "+ arcpy.GetMessages(),"ERROR")
            return None
        finally:
            sr = None

    def _simplify(self, fc, crs, simplificationType):
        tolerance = 10
        simplifiedfc = None
        reprojectedFC = None
        outputFC = None                        
        try:
            desc = arcpy.Describe(fc)
            type = desc.shapeType
            reprojectedFC = self._toProjection(fc,crs)

            if reprojectedFC != None:
                outputFC = reprojectedFC
            else:
                outputFC = fc

            if simplificationType == 1 or type == "Point" : 
                self._updateBoundingBox(outputFC)
                return self._toJSON(outputFC)
        
            numVerts = self._getVerticesCount(outputFC)
            self._sm("Number of vertices: " + str(numVerts))
                        
            if numVerts < 100:      
                #no need to simplify
                return self._toJSON(outputFC)
            elif numVerts < 1000:
                tolerance = 10
            elif numVerts < 2000:
                tolerance = 20
            else:
                tolerance = 30

            self._sm("Simplifying feature with tolerance: "+str(tolerance))

            if type == 'Polygon':
                self._updateBoundingBox(outputFC)
                simplifiedfc = CA.SimplifyPolygon(outputFC,  os.path.join(self._TempLocation, "simplified"), "POINT_REMOVE", str(tolerance) +" Meters", 0, "RESOLVE_ERRORS", "KEEP_COLLAPSED_POINTS")
            else:
                self._updateBoundingBox(outputFC)
                simplifiedfc = CA.SimplifyLine(outputFC, os.path.join(self._TempLocation, "simplified"), "POINT_REMOVE", str(tolerance) +" Meters", "RESOLVE_ERRORS", "KEEP_COLLAPSED_POINTS")
                
            self._sm(arcpy.GetMessages()) 
            return self._toJSON(simplifiedfc)

        except:  
            tb = traceback.format_exc()                  
            self._sm("Error Simplifying: " + tb,"ERROR")

            return self._toJSON(fc)
        finally:
            outputFC = None
            if reprojectedFC != None: arcpy.Delete_management(reprojectedFC)            
            if simplifiedfc != None: arcpy.Delete_management(simplifiedfc)
        
    def _getVerticesCount(self, polyFC):
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
    def _updateBoundingBox(self, feature):        
        try:
            extent = arcpy.Describe(feature).Extent
            if(self.BoundingBox[0] == None or extent.XMin < self.BoundingBox[0]): self.BoundingBox[0]= extent.XMin
            if(self.BoundingBox[1] == None or extent.YMin < self.BoundingBox[1]): self.BoundingBox[1]= extent.YMin

            if(self.BoundingBox[2] == None or extent.XMax > self.BoundingBox[2]): self.BoundingBox[2]= extent.XMax
            if(self.BoundingBox[3] == None or extent.YMax > self.BoundingBox[3]): self.BoundingBox[3]= extent.YMax
   
        except:
            tb = traceback.format_exc()

    def _copyandRemoveFeature(self, polyFC, fieldName, whereclause):
        try:
            delimitedField = arcpy.AddFieldDelimiters(polyFC, "GlobalWshd")
            expression = delimitedField + " = 1"
            coppiedFC = arcpy.FeatureClassToFeatureClass_conversion(polyFC, arcpy.Describe(polyFC).path, polyFC+"copied", expression)
          

            return coppiedFC
        except:
            tb = traceback.format_exc()
            return null
    
    def _resetEnvironments(self): 
        try:
            arcpy.ClearEnvironment("workspace")
            arcpy.ResetEnvironments()
            
        except:
            tb = traceback.format_exc()
            self._sm("resetting environments "+tb, "ERROR")

    def _setEnvironments(self):        
        arcpy.env.workspace = self._TempLocation
    #endregion
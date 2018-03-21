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
#06.01.2015 jkn - Created/ Adapted from John Guthrie's getDerivedFeats.py
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
import arcpy.cartography as CA
import logging

#endregion

class Features(object):
    #region Constructor
    def __init__(self, directory, workspaceid):
        
        self.Features = []        
        self.FeaturesList=[]
        self.Message =""


        self.WorkspaceID = workspaceid
        self.__MainDirectory__ = os.path.join(directory,self.WorkspaceID)
        self.__TempDirectory__ = os.path.join(self.__MainDirectory__,"Temp")

        #set up logging
        logdir = os.path.join(self.__TempDirectory__, 'Feature.log')
        logging.basicConfig(filename=logdir, format ='%(asctime)s %(message)s', level=logging.DEBUG)

         #Test if workspace exists before run   
        if(not self.__workspaceExists__(os.path.join(self.__MainDirectory__, self.WorkspaceID+".gdb","Layers"))):   
            self.__sm__("workspace: "+ os.path.join(self.__MainDirectory__, self.WorkspaceID+".gdb","Layers") + " does not exist", "ERROR")
            return
        
        arcpy.env.overwriteOutput = True
        arcpy.env.workspace =  os.path.join(self.__MainDirectory__, self.WorkspaceID+".gdb","Layers")
        self.__sm__("Initialized")

        self.__getFeaturesList__()
                 
    #endregion   
        
    #region Methods   
   
    def GetFeatures(self, featurelist='', crs = 4326, simplificationType=1):
        gwcopied = None
        try:
            if featurelist == '':
                for fname in self.FeaturesList:
                    self.Features.append({"name" : fname})
                return

            else:
                for f in map(lambda s: s.strip(), featurelist.split(';')):
                    if f.lower() in self.FeaturesList:
                        if f.lower() == "globalwatershed":
                            expression = arcpy.AddFieldDelimiters(f, "GlobalWshd") + " = 1"
                            gwcopied = arcpy.FeatureClassToFeatureClass_conversion(f, arcpy.Describe(f).path, f+"copied", expression)
                            self.Features.append({
                                                "name" : f,                                  
                                                "feature": self.__simplify__(gwcopied,crs, simplificationType)
                                              })
                        else:
                            self.Features.append({
                                                "name" : f,                                  
                                                "feature": self.__simplify__(f,crs, simplificationType)
                                              })
        except:
            tb = traceback.format_exc()
            self.__sm__("Failed to include feature " + tb,"ERROR") 
        finally:
            if gwcopied != None: arcpy.Delete_management(gwcopied)  
   
    #endregion  
      
    #region Helper Methods
    def __workspaceExists__(self, workspace):
         return arcpy.Exists(workspace)

    def __getFeaturesList__(self):
        try:           
            #open feature/ loop through and add to array
            for fc in arcpy.ListFeatureClasses():
                self.FeaturesList.append(fc.lower())  
        except:
            tb = traceback.format_exc()
            self.__sm__("Featurelist Error "+tb,"ERROR")
         
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

    def __simplify__(self, fc, crs, simplificationType):
        tolerance = 10
        simplifiedfc = None
        reprojectedFC = None
        outputFC = None                        
        try:
            desc = arcpy.Describe(fc)
            type = desc.shapeType
            reprojectedFC = self.__toProjection__(fc,crs)

            if reprojectedFC != None:
                outputFC = reprojectedFC
            else:
                outputFC = fc

            if simplificationType == 1 or type == "Point" : 
                 return self.__ToJSON__(outputFC)
        
            numVerts = self.__getVerticesCount__(outputFC)
            self.__sm__("Number of vertices: " + str(numVerts))
                        
            if numVerts < 100:      
                #no need to simplify
                return self.__ToJSON__(outputFC)
            elif numVerts < 1000:
                tolerance = 10
            elif numVerts < 2000:
                tolerance = 20
            else:
                tolerance = 30
                                          
            self.__sm__("Simplifying feature with tolerance: "+str(tolerance))

            if type == 'Polygon':
                simplifiedfc = CA.SimplifyPolygon(outputFC,  arcpy.Describe(outputFC).path+"simplified", "POINT_REMOVE", str(tolerance) +" Meters", 0, "RESOLVE_ERRORS", "KEEP_COLLAPSED_POINTS")
            else:
                simplifiedfc = CA.SimplifyLine(outputFC, arcpy.Describe(outputFC).path+"simplified", "POINT_REMOVE", str(tolerance) +" Meters", "RESOLVE_ERRORS", "KEEP_COLLAPSED_POINTS")
                
            self.__sm__(arcpy.GetMessages()) 
            return self.__ToJSON__(simplifiedfc)

        except:  
            tb = traceback.format_exc()                  
            self.__sm__("Error Simplifying: " + tb,"ERROR")

            return self.__ToJSON__(fc)
        finally:
            outputFC = None
            if reprojectedFC != None: arcpy.Delete_management(reprojectedFC)            
            if simplifiedfc != None: arcpy.Delete_management(simplifiedfc)
        
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

    def __copyandRemoveFeature__(self, polyFC, fieldName, whereclause):
        try:
            delimitedField = arcpy.AddFieldDelimiters(polyFC, "GlobalWshd")
            expression = delimitedField + " = 1"
            coppiedFC = arcpy.FeatureClassToFeatureClass_conversion(polyFC, arcpy.Describe(polyFC).path, polyFC+"copied", expression)
          

            return coppiedFC
        except:
            tb = traceback.format_exc()
            return null

    def __sm__(self, msg, type = 'INFO'):
        self.Message += type +':' + msg.replace('_',' ') + '_'

        if type in ('ERROR'): logging.error(msg)
        else : logging.info(msg)
    #endregion


##-------1---------2---------3---------4---------5---------6---------7---------8
##       Main
##-------+---------+---------+---------+---------+---------+---------+---------+
class FeaturesWrapper(object):
    #region Constructor
    def __init__(self):
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument("-workspaceID", help="specifies the working folder", type=str, default="CO20160523080051087000")
            parser.add_argument("-directory", help="specifies the projects working directory", type=str, default = r"D:\gistemp\ClientData")              
            parser.add_argument("-includefeatures", help="specifies the features", type=str, default = r"")
            parser.add_argument("-simplification", help="specifies the simplify method to, 1 = full, 2 = simplified", type=int, choices=[1,2], default = 2)
            parser.add_argument("-outputcrs", help="specifies the output projection to use",type=int, default=4326)             
            args = parser.parse_args()

            simplification = args.simplification
            if simplification == '#' or not simplification:
                simplification = 1

            ssfeature = Features(args.directory, args.workspaceID)
    
            ssfeature.GetFeatures(args.includefeatures, args.outputcrs, simplification)
            
            Results = {
                       "Workspace": ssfeature.WorkspaceID,
                       "Features":ssfeature.Features,
                       "Message": ssfeature.Message.replace("'",'"').replace('\n',' ')
                      }

        except:
             tb = traceback.format_exc()
             Results = {
                       "error": {"message": traceback.format_exc()}
                       }

        finally:
            print "Results="+json.dumps(Results) 

if __name__ == '__main__':
    FeaturesWrapper()

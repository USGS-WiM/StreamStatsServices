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
        self._MainDirectory = os.path.join(directory,workspaceid)

        self.WorkspaceID = regionID + str(datetime.datetime.now()).replace('-','').replace(' ','').replace(':','').replace('.','')
        self._WorkspaceDirectory = self._getDirectory(os.path.join(directory, self.WorkspaceID),True)

        self._TempDirectory = os.path.join(self._WorkspaceDirectory, "Temp")

        #set up logging
        logdir = os.path.join(self._TempDirectory, 'EditWatershed.log')
        logging.basicConfig(filename=logdir, format ='%(asctime)s %(message)s', level=logging.DEBUG)

         #Test if workspace exists before run   
        if(not self._workspaceExists(os.path.join(self._MainDirectory, workspaceid+".gdb","Layers"))):   
            self._sm("workspace: "+ os.path.join(self._MainDirectory, self.WorkspaceID+".gdb","Layers") + " does not exist", "ERROR")
            return
        
        self.GlobalWatershed = os.path.join(os.path.join(self._MainDirectory, workspaceid+".gdb","Layers","GlobalWatershed"))
        self.GlobalWatershedPoint = os.path.join(os.path.join(self._MainDirectory, workspaceid+".gdb","Layers","GlobalWatershedPoint"))
        
        if(arcpy.Exists(self.GlobalWatershed)):  
            sr = arcpy.Describe(os.path.join(self._MainDirectory, workspaceid+".gdb","Layers")).spatialReference    
            self.DatasetPath = arcpy.CreateFileGDB_management(self._WorkspaceDirectory, self.WorkspaceID +'.gdb')[0]
            self.FeaturePath =featurePath = arcpy.CreateFeatureDataset_management(self.DatasetPath,'Layers', sr)[0]
            self.IsValid = True
            arcpy.env.workspace =  self.DatasetPath
            self._sm("Initialized")     
    #endregion   
        
    #region Methods   
    def Execute(self, add, remove, espg):
        appendlist = None
        removelist = None
        outname =""
        appendedFeature = self.GlobalWatershed
        resultgdb = os.path.join(self._WorkspaceDirectory, self.WorkspaceID+".gdb","Layers","GlobalWatershed")
        try:
            self._sm("Executing")
            appendlist = self._jsonToPolygonArray(add, espg)
            removelist = self._jsonToPolygonArray(remove,espg)
   
            if(len(appendlist)>0): 
                if(len(removelist)<1):outname = resultgdb    
                appendedFeature = self._editWatershed(appendlist,self.GlobalWatershed,'append',outname)
            if(len(removelist)>0):
                self._editWatershed(removelist, appendedFeature,'remove', resultgdb )
   
            self._addFields(resultgdb, arcpy.ListFields(self.GlobalWatershed))  
            
            #copy pourpoint over
            arcpy.Copy_management(self.GlobalWatershedPoint, os.path.join(self._WorkspaceDirectory, self.WorkspaceID+".gdb","Layers","GlobalWatershedPoint"))         
            self._sm("finished")
        except:
            tb = traceback.format_exc()
            self._sm("Failed to include feature " + tb,"ERROR") 
        finally:
            appendlist = None
            removelist = None
            appendedFeature = None
            outname = None
            
    #endregion  
      
    #region Helper Methods
    def _addFields(self, feature, fieldList):
        # field.name , field.type , field.precision , field.scale, field.length, field.aliasName , field.isNullable , field.required
        try:
            self._sm("updating fields")
            includeList = list(set([f.name for f in fieldList])-set([f.name for f in arcpy.ListFields(feature)]))
            if(len(includeList)>0):
                rows = arcpy.da.SearchCursor(self.GlobalWatershed,includeList)
                for row in rows:
                    for field in fieldList:
                        if(field.name in includeList):
                            arcpy.AddField_management(feature, field.name , field.type , field.precision , field.scale, field.length, field.aliasName , field.isNullable , field.required)
                            val = row[includeList.index(field.name)]
                            if(val):                            
                                arcpy.CalculateField_management(feature,field.name,'"'+str(val)+'"',"PYTHON")
                            if(field.name == "Edited"):
                                arcpy.CalculateField_management(feature,field.name,'"'+str(1)+'"',"PYTHON")
                    break

            rows = arcpy.da.SearchCursor(self.GlobalWatershed,"Edited")
            for row in rows:
                for field in fieldList:
                    if(field.name == "Edited"):
                        arcpy.CalculateField_management(feature,field.name,'"'+str(1)+'"',"PYTHON")
                        break
                    
        except:
            tb = traceback.format_exc()
            self._sm("Failed to include fields " + tb,"ERROR") 
    def _fieldExist(self, featureclass, fieldname):
        fieldList = arcpy.ListFields(featureclass, fieldname)

        fieldCount = len(fieldList)

        if (fieldCount == 1):
            return True
        else:
            return False
    def _editWatershed(self, featurelist, infeature, method = 'append', out = ""):

        geometries = "in_memory\\lstHSUnionGeom"
        merged = "in_memory\\mergedFeature"
        try:     
            self._sm(method+"ing "+ "changes")
            if(out ==""): out = "in_memory\\"+ method      
            arcpy.Union_analysis(featurelist,geometries)
           
            if(method =="append"):
                arcpy.Merge_management([infeature, geometries],merged) 
                return arcpy.Dissolve_management(merged, out)   
            else:
                return arcpy.Erase_analysis(infeature, featurelist,out)      
   
        except:
            tb = traceback.format_exc()
            self._sm("Failed to include feature " + tb,"ERROR") 
            raise Exception(tb)
        finally:
            if(geometries != None): arcpy.Delete_management(geometries)
            if(merged != None): arcpy.Delete_management(merged)
    def _getDirectory(self, subDirectory, makeTemp = True, template=None):
        try:
            if os.path.exists(subDirectory): 
                shutil.rmtree(subDirectory)
            os.makedirs(subDirectory)

            #temp dir
            if makeTemp:
                os.makedirs(os.path.join(subDirectory, "Temp"))
 

            return subDirectory
        except:
            x = arcpy.GetMessages()
            return subDirectory
    def _jsonToPolygonArray(self, jsonlist, espg):
        list = []
        for jobj in jsonlist:
                list.append(self._getPolygon(jobj,espg))
        return list
    def _workspaceExists(self, workspace):
         return arcpy.Exists(workspace)      
    def _getPolygon(self,jsonArray, crs):
        lst_part = []  
        for part in jsonArray["rings"]: 
            lst_pnt = []  
            for pnt in part:  
                lst_pnt.append(arcpy.Point(float(pnt[0]), float(pnt[1])))  
            lst_part.append(arcpy.Array(lst_pnt))  
        array = arcpy.Array(lst_part)  
        return arcpy.Polygon(array, crs)                       
    def _sm(self, msg, type = 'INFO'):
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
                parser.add_argument("-workspaceID", help="specifies the working folder", type=str, default="OK20160418144755086000")
                parser.add_argument("-directory", help="specifies the projects working directory", type=str, default = r"D:\gistemp\ClientData")
                parser.add_argument("-appendlist", help="specifies a list of polygons to append", type=str, default = r'[]')
                parser.add_argument("-removelist", help="specifies a list of polygons to remove", type=str, default = r'[{rings:[[[-99.492187499999986,36.366424946584353],[-99.4508171081543,36.349144422302807],[-99.4928741455078,36.336700069393174],[-99.4973373413086,36.349559199818209],[-99.492187499999986,36.366424946584353]]]}]')
                parser.add_argument("-wkid", help="specifies the esri well known id of pourpoint ", type=str, default = '4326')
                args = parser.parse_args()

                ssedit = EditWatershed(args.directory, args.workspaceID)
                if(not ssedit.IsValid): raise Exception("Invalid Exception was thrown. Workspace may be invalid")
                
                ssedit.Execute(json.loads(args.appendlist.replace('rings','"rings"')),json.loads(args.removelist.replace('rings','"rings"')),args.wkid)                    
                
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




#------------------------------------------------------------------------------
#----- mainwrapper.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2018 WiM - USGS

#    authors:  Jeremy K. Newson USGS Wisconsin Internet Mapping
# 
#   purpose:  StormWaterDelineation <STABBR> <PourPoint> <GlobalWatershedPoint> <GlobalWatershed>
#          
#discussion:
#       

#region "Comments"
#01.30.2018 jkn - Created
#endregion

#region "Imports"
import sys
import os
import traceback
import datetime
import time
import argparse
import arcpy
import shutil
from SSOps.Stormwater import Stormwater as Stormwater
from SSOps.Features import Features as Features
from WiMPy import WiMLogging
from WiMPy import Shared
from WiMPy.Config import Config
import json

#endregion
#-------1---------2---------3---------4---------5---------6---------7---------8
##       Main
##-------+---------+---------+---------+---------+---------+---------+---------+
class mainWrapper(object):
    #region Constructor
    def __init__(self):
        self._startTime = time.time()        
        self.Results ={}
        self._args = self._getargs()
        self.workspaceID = self._args.workspaceID
        config = Config(json.load(open(os.path.join(os.path.dirname(__file__), 'config.json')))) 
        self._workingDir = Shared.GetWorkspaceDirectory(config["workingdirectory"],self._args.rcode,self.workspaceID) 
        WiMLogging.init(os.path.join(self._workingDir,"Temp"),"StreamStats.log")
    #endregion    
    #region Methods
    def Run(self):
        try:
            self._sm("Started StreamStats script routine")
            
            regionID = self._args.rcode
            ppoint = self._args.pourpoint          
            crs = self._args.pourpointwkid
            print(ppoint, regionID, crs)

            self.workspaceID = self._args.workspaceID
            parameters = self._args.parameters
            features = self._args.includefeatures
            simplification = self._args.simplification
            outCRS = self._args.outputcrs
            toType = self._args.totype

            appendList = self._args.appendlist
            removelist = self._args.removelist

            if(regionID and ppoint and crs): 
                self._computeWatershed(ppoint, crs)            
            
            if(self.workspaceID and parameters):
                self._loadParameters(parameters)

            if(self.workspaceID):
                self._loadFeatures(features, outCRS,simplification)

            if(self.workspaceID and toType):
                self._getDownload(toType)

            if(self.workspaceID and (appendList or removelist)):
                self._editWatershed(appendList,removelist)
        except:
            tb = traceback.format_exc()
            self._sm("Error executing Main wrapper "+tb, "ERROR")
        finally:
            print("messages=" + ';'.join(WiMLogging.LogMessages).replace('\n',' '))
            print (json.dumps(self.Results))
    #endregion
    #region Helper Methods 
    def _computeWatershed(self, ppoint, crs):
        wshed = None
        try:
            #create inmemory ppoint
            pourpoint = self._buildAHPourpoint(ppoint,crs)
            id = os.path.basename(self._workingDir)
            #call StreamStatsOps Watershed
            with Stormwater(self._workingDir,id) as sw:
                wshed = sw.Delineate(pourpoint)
            #sets the workspaceID
            self.workspaceID = id
            self.Results["WorkspaceID"] = id
            self._sm("Delineated watershed elapse: "+ str(round((time.time()- self._startTime), 2))+'sec')

        except:
            tb = traceback.format_exc()
            self._sm("Error executing delineation wrapper "+tb)
    def _loadParameters(self, parameters):
        try:
            #create inmemory ppoint
            #call StreamStatsOps Watershed
            #sets the workspaceID
            print("Loading Parameters elapse: "+ str(round((time.time()- self._startTime), 2))+'sec')
        except:
            tb = traceback.format_exc()
            self._sm("Error executing delineation wrapper "+tb)
    def _loadFeatures(self, features, outCRS, simplification=1):
        try:
            #create inmemory ppoint
            with Features(self._workingDir,self.workspaceID) as ftr:
                if (not ftr.isValid): raise Exception("features are invalid") 
                features = ftr.GetFeatures(features, outCRS, simplification)
                fc = {
                      "type": "FeatureCollection",
                      "bbox":ftr.BoundingBox,
                      "features":features
                      }
                self.Results["Layers"]=fc
                
            #call StreamStatsOps Watershed
            #sets the workspaceID
            self._sm("Loading features elapse: "+ str(round((time.time()- self._startTime), 2))+'sec')
        except:
            tb = traceback.format_exc()
            self._sm("Error loading Features "+tb, "ERROR")
    def _getDownload(self, toType ):
        try:
            #create inmemory ppoint
            #call StreamStatsOps Watershed
            #sets the workspaceID
            self._sm("Nothing to download elapse: "+ str(round((time.time()- self._startTime), 2))+'sec')
        except:
            tb = traceback.format_exc()
            self._sm("Error executing delineation wrapper "+tb)
    def _editWatershed(self, appendList,removelist):
        try:
            #create inmemory ppoint
            #call StreamStatsOps Watershed
            #sets the workspaceID
            self._sm("Editing watershed")
        except:
            tb = traceback.format_exc()
            self._sm("Error executing delineation wrapper "+tb)
    def _getargs(self):
        try:
            parser = argparse.ArgumentParser()
            #for delineation
            parser.add_argument("-rcode", help="specifies the abbr state name to perform delineation", type=str, default="MO_STLouis")
            parser.add_argument("-pourpoint", help="specifies the json representation of an esri point feature collection ", type=str, default = '[-90.24313151836395,38.63352941107537]')
            parser.add_argument("-pourpointwkid", help="specifies the esri well known id of pourpoint ", type=str, default = '4326')
        
            #required for all below
            parser.add_argument("-workspaceID", help="specifies the working folder", type=str, default= "")
         
            #for parameters
            parser.add_argument("-parameters", help="specifies the list of parameters to be computed", type=str, default = "")
       
            #for features
            parser.add_argument("-includefeatures", help="specifies the features, if blank, you'll get a list of features available", type=str, default = r"GlobalWatershedPoint,GlobalWatershed")
            parser.add_argument("-simplification", help="specifies the simplify method to, 1 = full, 2 = simplified", type=int, choices=[1,2], default = 2)
            parser.add_argument("-outputcrs", help="specifies the output projection to use",type=int, default=4326)             
       
            #for download
            parser.add_argument("-totype", help="specifies the type to convert to, 2 = .gdb, 1 = .shp", type=int, choices=[None, 1,2], default = None)
            #for editing
            parser.add_argument("-appendlist", help="specifies a list of polygons to append", type=str, default = None)
            parser.add_argument("-removelist", help="specifies a list of polygons to remove", type=str, default = None)

            return parser.parse_args()
        except:
            tb = traceback.format_exc()
            print(tb)
    def _sm(self,msg,type="INFO", errorID=0): 
        try:
            WiMLogging.sm(msg,type="INFO", errorID=0)
        except:
            print(msg)
    def _buildAHPourpoint(self, ppt, wkid):
        try:
            arcpy.env.workspace = os.path.join(self._workingDir,"Temp")
            arcpy.env.overwriteOutput = True
            #get spatial ref
            wkid = int(wkid)
            sr = arcpy.SpatialReference(wkid)
            pourPoint = {"type":"Point","coordinates":json.loads(ppt)}
            arcpy.env.overwriteOutput = True
            FC = arcpy.CreateFeatureclass_management("in_memory", "FC", "POINT", spatial_reference=sr)
            #add required attributes
            t_fields = (  
                         ("Name", "TEXT"),
                         ("Descript", "TEXT"), 
                         ("SnapOn", "SHORT"),
                         ("SrcType", "SHORT")                        
                        )
            for t_field in t_fields:  
                arcpy.AddField_management(FC, *t_field)  

            # Create insert cursor for table
            fields = [i[0] for i in t_fields]
            fields.insert(0,'SHAPE@')

            with arcpy.da.InsertCursor(FC,fields) as cursor:
                cursor.insertRow([arcpy.AsShape(pourPoint),"ags101","",1,0])
            #next cursor

            return FC
        except:
            tb = traceback.format_exc()
            print tb
    #endregion

if __name__ == '__main__':
    mw = mainWrapper()
    mw.Run()

        
        

    


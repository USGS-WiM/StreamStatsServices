﻿#-------------------------------------------------------------------
#----- Stormwater.py -----------------------------------------------
#-------------------------------------------------------------------
#
#  copyright:  2016 WiM - USGS
#
#    authors:  Jeremy K. Newson - USGS Web Informatics and Mapping (WiM)
#              
#    purpose:  Delineate using mask using ArcGIS's Python library (arcpy)
#
#      usage:  THIS SECTION NEEDS TO BE UPDATED
#
# discussion:  Intial code was created by Jeremy K. Newson. Some minor edits were done
#                   by John Wall (NC State University).
#
#              See:
#                   https://github.com/GeoJSON-Net/GeoJSON.Net/blob/master/src/GeoJSON.Net/Feature/Feature.cs
#                   http://pro.arcgis.com/en/pro-app/tool-reference/spatial-analyst/watershed.htm
#                   geojsonToShape: http://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy-functions/asshape.htm
#
#      dates:   19 AUG 2016 jkn - Created / Date notation edited by jw
#               03 APR 2017 jw - Modified
#
#------------------------------------------------------------------------------

#region "Imports"
import traceback
import os
import arcpy
from arcpy import env
from arcpy.sa import *
import json
import sys
from stormwaterdelineation import *
from SSOps.StreamStatsOpsBase import StreamStatsOpsBase as SSOpsBase
from WiMPy.Config import Config
from WiMPy.MapLayer import *
from arcpy.geoprocessing._base import gp

#endregion

class Stormwater(SSOpsBase):
    #region Constructor and Dispose
    def __init__(self, workspacePath,id):     
        SSOpsBase.__init__(self,workspacePath) 
        self.WorkspaceID = id        
        self._sm("initialized hydroops")
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        SSOpsBase.__exit__(self, exc_type, exc_value, traceback) 
    #endregion   
        
    #region Methods   
    def Delineate(self, PourPoint):
        fdr = None
        strlnk = None
        cat = None
        adjCat = None
        pipe= None
        strm = None
        sink= None
        hydrJct = None
        sr = None
        datasetPath = None
        featurePath = None
        netTrace = None

        try:
            datasetName = Config()["datasetNames"]
            self._sm("Delineating catchment")
            fdr = MapLayer(MapLayerDef("fdr"), "", PourPoint)
            if not fdr.Activated:
                raise Exception("Flow direction could not be activated.")

            strlnk = self._getActiveLayer("strlnk", fdr.TileID)            
            cat = self._getActiveLayer("Catchment",fdr.TileID,fdr.TileID+".gdb\\Layers")       
            adjCat = self._getActiveLayer("AdjointCatchment",fdr.TileID,fdr.TileID+".gdb\\Layers")
            pipe = self._getActiveLayer("Pipe",fdr.TileID,fdr.TileID+".gdb\\Layers", True)
            strm =self._getActiveLayer("Stream",fdr.TileID,fdr.TileID+".gdb\\Layers", True)
            sink =self._getActiveLayer("SinkWatershed",fdr.TileID,fdr.TileID+".gdb\\Layers")
            hydrJct =self._getActiveLayer("HydroJunction",fdr.TileID,fdr.TileID+".gdb\\Layers") 

            sr = fdr.spatialreference
      

            datasetPath = arcpy.CreateFileGDB_management(self._WorkspaceDirectory, self.WorkspaceID +'.gdb')[0]
            featurePath = arcpy.CreateFeatureDataset_management(datasetPath, 'Layers', sr )[0]

            self._sm("creating workspace environment. "+ datasetPath)
            arcpy.CheckOutExtension("Spatial")
            self._sm("Starting Delineation")
            netTrace = StormNetTraceOp()
            result=netTrace.GetWatershedViaNetTrace(PourPoint,2,fdr.Dataset, strlnk,strlnk,
                                                               cat, adjCat, sink, pipe, strm, hydrJct, 
                                                               os.path.join(featurePath,datasetName["basin"]),
                                                               os.path.join(featurePath,datasetName["point"]), False)

            self._sm(arcpy.GetMessages(), 'AHMSG')
            self._sm("Finished")
            return featurePath
        except:
            tb = traceback.format_exc()
            self._sm("Delineation Error "+tb, "ERROR")

        finally:
            arcpy.CheckInExtension("Spatial")
            #Local cleanup
            if fdr != None: del fdr
            if strlnk != None: del strlnk
            if cat != None: del cat
            if adjCat != None: del adjCat
            if pipe != None: del pipe
            if strm != None: del strm
            if sink != None: del sink
            if hydrJct != None: del hydrJct
            if sr != None: del sr
            if netTrace != None: netTrace = None
            if datasetPath != None: del datasetPath
            if featurePath != None: del featurePath
    def _resetEnvironments(self): 
        try:
            arcpy.ClearEnvironment("workspace")
            arcpy.ResetEnvironments()
            
        except:
            tb = traceback.format_exc()
            self._sm("resetting environments "+tb, "ERROR")

    def _setEnvironments(self):        
        arcpy.env.workspace = self._TempLocation

    def _getActiveLayer(self, name, tileID="", datasetname ="", returnAsLayer = False):
        try:
            ml = MapLayerDef(name)
            ml.DataSetName = datasetname
            layer = MapLayer(ml, tileID)
            if not layer.Activated:
                raise Exception(name +" could not be activated.")
            if(returnAsLayer):
                return arcpy.MakeFeatureLayer_management(layer.Dataset, name)
            else:
                return layer.Dataset
        except :
            tb = traceback.format_exc()
            raise Exception(name +" error "+tb)
#------------------------------------------------------------------------------
#----- ToSHP.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2014 WiM - USGS

#    authors:  Jeremy K. Newson USGS Wisconsin Internet Mapping
# 
#   purpose:  converts .gdb to .shp files
#          
#discussion:  
#

#region "Comments"
#11.05.2014 jkn - Created
#endregion

#region "Imports"
import sys
import traceback
import os
import argparse
import arcpy
import shutil
import json
import logging

import xmltodict

import ArcHydroTools
import xml.dom.minidom
import decimal
#endregion


##-------1---------2---------3---------4---------5---------6---------7---------8
##       ConvertToSHP
##-------+---------+---------+---------+---------+---------+---------+---------+

class FlowStatistics(object):
    #region Constructor
    def __init__(self,directory, workspaceID, regionID):  
        self.isInitialized = False
        self.WorkspaceID = workspaceID
        self.RegionID = regionID
        self.isComplete = False
        self.Message =""  
        self.FlowReport = None  
        self.__MainDirectory__ = os.path.join(directory,self.WorkspaceID)

        logdir = os.path.join(os.path.join(self.__MainDirectory__,"Temp"), 'FlowStats.log')
        logging.basicConfig(filename=logdir, format ='%(asctime)s %(message)s', level=logging.DEBUG)
        #Test if workspace exists before run   
        if(self.__workspaceExists__(os.path.join(self.__MainDirectory__, self.WorkspaceID+".gdb","Layers"))):
           self.isInitialized = True
        else:
            self.__sm__("workspace doesn't exist",'ERROR')
    #endregion  
         
    #Methods
    def Compute(self, flowsStatisticsList):
        workspace = ''
        try:
            # Set overwrite option
            arcpy.env.overwriteOutput = True
            arcpy.env.scratchWorkspace = self.__setScratchWorkspace__(os.path.join(self.__MainDirectory__, "Temp"))

            self.__sm__('workspace set: '+self.WorkspaceID)
            workspace = os.path.join(self.__MainDirectory__, self.WorkspaceID+".gdb","Layers")

            outputFile = os.path.join(self.__MainDirectory__, "Temp","flowStatisticsFile{0}")
            
            arcpy.CheckOutExtension("Spatial")
            self.__sm__("Stated calc flow statistics")

            ArcHydroTools.ComputeFlows(os.path.join(workspace,"GlobalWatershed"), 
                                       os.path.join(workspace,"GlobalWatershedPoint"), 
                                       outputFile.format(".xml"), outputFile.format(".htm"), 
                                       self.__getXMLPath__(),
                                       flowsStatisticsList, "", 
                                       self.WorkspaceID )

            self.__sm__(arcpy.GetMessages(),'AHMSG')
            arcpy.CheckInExtension("Spatial")

            self.FlowReport = self.__parseXML__( outputFile.format(".xml"))

            self.__sm__("finished calc flow statistics")

            self.isComplete = True
        except:
            tb = traceback.format_exc() 
            self.__sm__("Error computing Flow Statistics "+tb,"ERROR")
            self.isComplete = False     
       
    #Helper Methods
    def __setScratchWorkspace__(self, directory):
        if (arcpy.Exists(os.path.join(directory,"scratch.gdb"))):
            arcpy.Delete_management(os.path.join(directory,"scratch.gdb"))
        arcpy.CreateFileGDB_management(directory,'scratch.gdb')
        return os.path.join(directory,"scratch.gdb")  
    def __getDirectory__(self, subDirectory):
        if os.path.exists(subDirectory): 
            shutil.rmtree(subDirectory)
        os.makedirs(subDirectory);

        return subDirectory
    def __sm__(self, msg, type = ''):
        self.Message += type +':' + msg.replace('_',' ') + '_'

        if type in ('ERROR'): logging.error(msg)
        else : logging.info(msg)
    def __workspaceExists__(self, workspace):
         return arcpy.Exists(workspace)
    def __getXMLPath__(self):
        #check tempdir
        tempDir = os.path.join(self.__MainDirectory__,"Temp")
        if os.path.exists(os.path.join(tempDir, "StreamStats{0}.xml".format(self.RegionID))):
            return os.path.join(tempDir, "StreamStats{0}.xml".format(self.RegionID))
        else:
            #default location
            return r"D:\ss_apps\XML\StreamStats{0}.xml".format(self.RegionID)
    
    def __parseXML__(self, file):
        try:
            self.__sm__("parsing xml")
            xmlDoc = self.__readFile__(file)
            obj = xmltodict.parse(xmlDoc)
            return obj

        except:
            tb = traceback.format_exc() 
            self.__sm__("Error computing Flow Statistics "+tb,"ERROR")

    def __readFile__(self, file):
        f = None
        try:
            f = open(file, 'r')
            return "".join(map(lambda s: s.strip(), f.readlines()))
        except:
            tb = traceback.format_exc()
            self.__sm__("file " + file + ' failed' + tb, 0.180, 'ERROR')
        finally:
            if not f == None or not f.closed :
                f.close();
    #endregion


##-------1---------2---------3---------4---------5---------6---------7---------8
##       Main
##-------+---------+---------+---------+---------+---------+---------+---------+        
class FlowStatisticsWrapper(object):
    #region Constructor
        def __init__(self):
            try:
                stabbr = arcpy.GetParameterAsText(0)
                workspaceID = arcpy.GetParameterAsText(1)
                directory = r"D:\gistemp\ClientData"
                flowtype = arcpy.GetParameterAsText(2)

                #set defaults
                if stabbr == '#' or not stabbr:
                   stabbr = 'IA'
                if workspaceID == '#' or not workspaceID:
                   workspaceID = 'IA'
                if flowtype == '#' or not flowtype:
                   flowtype = ''


                flowStats = FlowStatistics(directory, workspaceID, stabbr)
                if flowStats.isInitialized:
                    flowStats.Compute(flowtype)
                    Results = {"Statisitcs": flowStats.FlowReport,"Message":flowStats.Message.replace("'",'"').replace('\n',' ')}
                else:
                    Results = {"Workspace": "","Message":flowStats.Message.replace("'",'"').replace('\n',' ')}
            except:
                Results = {"Workspace": "Error", "Message":traceback.format_exc()}

            finally:
                arcpy.SetParameter(3, "Results="+json.dumps(Results))   
    #endregion    

# specifies that this class can be ran directly
if __name__ == '__main__':
    FlowStatisticsWrapper()

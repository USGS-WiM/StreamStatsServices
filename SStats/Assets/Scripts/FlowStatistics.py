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
        self.__xmlPath__ = r"D:\ss_apps\XML" 
        self.WorkspaceID = workspaceID
        self.RegionID = regionID
        self.isComplete = False
        self.Message =""  
        self.FlowReport = None  
        self.__MainDirectory__ = os.path.join(directory,self.WorkspaceID)
        self.__TempLocation__ = os.path.join(self.__MainDirectory__, "Temp")

        logdir = os.path.join(self.__TempLocation__, 'FlowStats.log')
        logging.basicConfig(filename=logdir, format ='%(asctime)s %(message)s', level=logging.DEBUG)
        #Test if workspace exists before run   
        if(self.__workspaceExists__(os.path.join(self.__MainDirectory__, self.WorkspaceID+".gdb","Layers"))):
           self.isInitialized = True
    #endregion  
         
    #Methods
    def Compute(self, flowsStatisticsList):
        workspace = ''
        xmlfile = ''
        try:
            # Set overwrite option
            arcpy.env.overwriteOutput = True
            arcpy.env.scratchWorkspace = self.__setScratchWorkspace__(os.path.join(self.__MainDirectory__, "Temp"))

            self.__sm__('workspace set: '+self.WorkspaceID)
            workspace = os.path.join(self.__MainDirectory__, self.WorkspaceID+".gdb","Layers")

            outputFile = os.path.join(self.__TempLocation__,"flowStatisticsFile{0}")
            xmlfile = self.__SSXMLPath__("StreamStats{0}.xml".format(self.RegionID),self.__TempLocation__)
            arcpy.CheckOutExtension("Spatial")
            self.__sm__("Stated calc flow statistics")

            ArcHydroTools.ComputeFlows(os.path.join(workspace,"GlobalWatershed"), 
                                       os.path.join(workspace,"GlobalWatershedPoint"), 
                                       outputFile.format(".xml"), outputFile.format(".htm"), 
                                       xmlfile,
                                       flowsStatisticsList, 
                                       os.path.join(os.path.join(self.__MainDirectory__,"Temp"), "", 'cfwrkspce.gdb') )

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
    def __SSXMLPath__(self, xmlFileName, newTempWorkspace = "#"):
        file = None
        xmlFile =''
        try:
            #return self.__SSXMLPath__("StreamStats{0}.xml".format(self.RegionID),'#',self.__TempLocation__)
            #move the file to tempDirectory
            if os.path.exists(os.path.join(self.__TempLocation__, xmlFileName)):
                xmlFile = os.path.join(self.__TempLocation__, xmlFileName)
                self.__sm__("Using existing xmlFile "+xmlFile);
            else:
            #default location
                xmlFile = os.path.join(self.__xmlPath__,xmlFileName)  
                self.__sm__("Using default xmlFile "+xmlFile);          
                shutil.copy(xmlFile, self.__TempLocation__)
                xmlFile = os.path.join(self.__TempLocation__,xmlFileName)
                self.__sm__("moved default xmlFile to temp "+xmlFile);  
                if newTempWorkspace == "#":
                    return xmlFile

                #update tempworkspace
                xmlDoc = xml.dom.minidom.parse(xmlFile)
                xmlDoc.getElementsByTagName('TempLocation')[0].firstChild.data = newTempWorkspace
                file = open(xmlFile,"wb")
                xmlDoc.writexml(file)
                self.__sm__("renamed temp location");  

            return xmlFile
        except:
             tb = traceback.format_exc()
             self.__sm__(tb,"ERROR")
             return os.path.join(self.__xmlPath__,xmlFileName)
        finally:
            if file != None and not file.closed: 
                file.close 
                file = None

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
                parser = argparse.ArgumentParser()
                parser.add_argument("-stabbr", help="specifies the abbr state name to perform delineation", type=str, default="NY")
                parser.add_argument("-workspaceID", help="specifies the working folder", type=str, default="NY20151116065555747000")
                parser.add_argument("-directory", help="specifies the projects working directory", type=str, default = r"C:\gistemp\ClientData")
                parser.add_argument("-flowtype", help="specifies the ';' separated list of flow types to computed", type=str, default = r"")
                args = parser.parse_args()


                flowStats = FlowStatistics(args.directory, args.workspaceID, args.stabbr)
                if flowStats.isInitialized:
                    flowStats.Compute(args.flowtype)
                    Results = {"Statisitcs": flowStats.FlowReport,"Message":flowStats.Message.replace("'",'"').replace('\n',' ')}
                else:
                    Results = {"Workspace": "","Message":flowStats.Message.replace("'",'"').replace('\n',' ')}
            except:
                Results = {"Workspace": "Error", "Message":traceback.format_exc()}

            finally:
                print "Results="+json.dumps(Results)   
    #endregion    

# specifies that this class can be ran directly
if __name__ == '__main__':
    FlowStatisticsWrapper()

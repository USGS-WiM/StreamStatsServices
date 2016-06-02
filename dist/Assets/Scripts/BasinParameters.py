#------------------------------------------------------------------------------
#----- BasinParameters.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2014 WiM - USGS

#    authors:  Jeremy K. Newson USGS Wisconsin Internet Mapping
# 
#   purpose:  Calculates ss parameters for a given watershed
#          
#discussion:  Adapted from John Guthrie's GetBC7.py basin characteristics script
#

#region "Comments"
#11.12.2014 jkn - Created
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
import ArcHydroTools
import xml.dom.minidom
import decimal
from arcpy import env
#endregion


##-------1---------2---------3---------4---------5---------6---------7---------8
##       BasinParameters
##-------+---------+---------+---------+---------+---------+---------+---------+

class BasinParameters(object):
    #region Constructor
    def __init__(self, regionID, directory, workspaceID, pList): 
        self.RegionID = regionID
        self.__xmlPath__ = r"D:\ss_apps\XML" 
        self.WorkspaceID = workspaceID
        self.isComplete = False
        self.Message =""    
        self.__MainDirectory__ = os.path.join(directory,self.WorkspaceID)
        self.__TempLocation__ = os.path.join(self.__MainDirectory__, "Temp")
        self.ParameterList = None

        logdir = os.path.join(self.__TempLocation__, 'parameter.log')
        logging.basicConfig(filename=logdir, format ='%(asctime)s %(message)s', level=logging.DEBUG)
         
        #Test if workspace exists before run   
        if(not self.__workspaceValid__(os.path.join(self.__MainDirectory__, self.WorkspaceID+".gdb","Layers"))):
            return

        self.__run__(pList)  
            
    #endregion  
         
    #Private Methods
    def __run__(self, parameters):
        workspace = ''
        plist = None
        xmlfile =''
        try:
            # Set overwrite option
            arcpy.env.overwriteOutput = True
            arcpy.env.scratchWorkspace = self.__setScratchWorkspace__(os.path.join(self.__MainDirectory__, "Temp"))

            workspace = os.path.join(self.__MainDirectory__, self.WorkspaceID+".gdb","Layers")
            self.__sm__('workspace set: '+self.WorkspaceID)
            outputFile = os.path.join(self.__MainDirectory__, "Temp","parameterFile{0}")

            xmlfile = self.__SSXMLPath__("StreamStats{0}.xml".format(self.RegionID), self.__TempLocation__)
           
            arcpy.CheckOutExtension("Spatial")
            self.__sm__("Stated calc params")
            ArcHydroTools.StreamstatsGlobalParametersServer(os.path.join(workspace,"GlobalWatershed"), 
                                                            os.path.join(workspace,"GlobalWatershedPoint"), 
                                                            parameters, outputFile.format(".xml"), outputFile.format(".htm"), 
                                                            xmlfile,"", self.WorkspaceID )

            self.__sm__(arcpy.GetMessages(),'AHMSG')
            arcpy.CheckInExtension("Spatial")
            self.__sm__("finished calc params")

            plist = self.__parseParameterXML__(outputFile.format(".xml"))
            if (len(plist) < 1):
                raise Exception("No parameters returned")
           
            self.ParameterList = plist
            self.isComplete = True

            self.__sm__("finished")
        except:
            tb = traceback.format_exc() 
            self.__sm__("Error calculating parameters "+tb,"ERROR")
            self.isComplete = False     
    def __parseParameterXML__(self, xmlfile):
        paramList = []
        try:
            self.__sm__("parsing xml")
            xmlDoc = xml.dom.minidom.parse(xmlfile)
            parameters = xmlDoc.getElementsByTagName("PARAMETER")         
            for param in parameters:
                code = param.getAttribute("name")
                value = param.getAttribute("value")
                paramList.append({"code":code,"value":value})
            #next param

            return paramList
        except:
             tb = traceback.format_exc()
             self.__sm__("Error reading parameters "+tb,"ERROR")
    def __getDirectory__(self, subDirectory):
        if os.path.exists(subDirectory): 
            shutil.rmtree(subDirectory)
        os.makedirs(subDirectory);

        return subDirectory
    def __workspaceValid__(self, workspace):
        if not arcpy.Exists(workspace):
            self.__sm__("Workspace " + workspace + " does not exist")
            return False
        if not arcpy.TestSchemaLock(workspace):
            self.__sm__("Workspace " + workspace + " has a schema lock","AHMSG")
            return False
        self.__sm__("Workspace " + workspace + " is valid")
        return True
    def __setScratchWorkspace__(self, directory):
        if (arcpy.Exists(os.path.join(directory,"scratch.gdb"))):
            arcpy.Delete_management(os.path.join(directory,"scratch.gdb"))
        arcpy.CreateFileGDB_management(directory,'scratch.gdb')
        return os.path.join(directory,"scratch.gdb")  
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
    def __sm__(self, msg, type = 'INFO'):
        self.Message += type +':' + msg.replace('_',' ') + '_'

        if type in ('ERROR'): logging.error(msg)
        else : logging.info(msg)
    #endregion

##-------1---------2---------3---------4---------5---------6---------7---------8
##       Main
##-------+---------+---------+---------+---------+---------+---------+---------+        
class BasinParametersWrapper(object):
    #region Constructor
        def __init__(self):
            try:
                parser = argparse.ArgumentParser()
                parser.add_argument("-stabbr", help="specifies the state abbreviation", type=str, default="NY")
                parser.add_argument("-workspaceID", help="specifies the working folder", type=str, default="NY20151116065555747000")
                parser.add_argument("-parameters", help="specifies the ';' separated list of parameters to be computed", type=str, default = "DRNAREA;KSATSSUR;I24H10Y;CCM;TAU_ANN;STREAM_VAR;PRECIP;HYSEP;RSD")
                parser.add_argument("-directory", help="specifies the projects working directory", type=str, default = r"C:\gistemp\ClientData")
                args = parser.parse_args()
                
                ssBp = BasinParameters(args.stabbr,args.directory, args.workspaceID, args.parameters)

                if ssBp.isComplete:
                    Results = {"Parameters": ssBp.ParameterList, "Message": ssBp.Message.replace("'",'"').replace('\n',' ')}
                else:
                    Results = {"Parameters": [],"Message": ssBp.Message.replace("'",'"').replace('\n',' ')}

            except:
                Results = {"error":traceback.format_exc()}

            finally:
                print "Results="+json.dumps(Results)   
    #endregion 
   

# specifies that this class can be ran directly
if __name__ == '__main__':
    BasinParametersWrapper()

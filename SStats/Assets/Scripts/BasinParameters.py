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
        self._xmlPath = r"C:\Users\kjacobsen\Documents\wim_projects\docs\new-data\vt" 
        self.WorkspaceID = workspaceID
        self.isComplete = False
        self.Message =""    
        self.directory = directory
        self._MainDirectory = os.path.join(directory,self.WorkspaceID)
        self._TempLocation = os.path.join(self._MainDirectory, "Temp")
        self.ParameterList = None

        logdir = os.path.join(self._TempLocation, 'parameter.log')
        logging.basicConfig(filename=logdir, format ='%(asctime)s %(message)s', level=logging.DEBUG)
         
        #Test if workspace exists before run   
        if(not self._workspaceValid(os.path.join(self._MainDirectory, self.WorkspaceID+".gdb","Layers"))):
            return

        self._run(pList)  
            
    #endregion  
         
    #Private Methods
    def _run(self, parameters):
        workspace = ''
        plist = None
        xmlfile =''
        try:
            # Set overwrite option
            arcpy.env.overwriteOutput = True
            arcpy.env.scratchWorkspace = self._setScratchWorkspace(os.path.join(self._MainDirectory, "Temp"))

            workspace = os.path.join(self._MainDirectory, self.WorkspaceID+".gdb","Layers")
            self._sm('workspace set: '+self.WorkspaceID)
            outputFile = os.path.join(self._MainDirectory, "Temp","parameterFile{0}")

            xmlfile = self._SSXMLPath("StreamStats{0}.xml".format(self.RegionID), self._TempLocation)
           
            arcpy.CheckOutExtension("Spatial")
            self._sm("Stated calc params")
            ArcHydroTools.StreamstatsGlobalParametersServer(os.path.join(workspace,"GlobalWatershed"), 
                                                            os.path.join(workspace,"GlobalWatershedPoint"), 
                                                            parameters, outputFile.format(".xml"), outputFile.format(".htm"), 
                                                            xmlfile,"", self.WorkspaceID )

            self._sm(arcpy.GetMessages(),'AHMSG')
            arcpy.CheckInExtension("Spatial")
            self._sm("finished calc params")

            plist = self._parseParameterXML(outputFile.format(".xml"), parameters)
            if (len(plist) < 1):
                raise Exception("No parameters returned")
           
            self.ParameterList = plist
            self.isComplete = True

            self._sm("finished")
        except:
            tb = traceback.format_exc() 
            self._sm("Error calculating parameters "+tb,"ERROR")
            self.isComplete = False     
    def _parseParameterXML(self, xmlfile, params):
        paramList = []
        try:
            self._sm("parsing xml")
            xmlDoc = xml.dom.minidom.parse(xmlfile)
            parameters = xmlDoc.getElementsByTagName("PARAMETER")         
            for param in parameters:
                code = param.getAttribute("name")
                value = param.getAttribute("value")
                paramList.append({"code":code,"value":value})
            #next param

            paramList = self._checkGlobals(params, paramList)
            return paramList
        except:
             tb = traceback.format_exc()
             self._sm("Error reading parameters "+tb,"ERROR")
    def _checkGlobals(self, parameters, plist):
        try:
            self._sm("Opening search cursor")
            afeature = os.path.join(self.directory, self.WorkspaceID, self.WorkspaceID+".gdb","Layers","GlobalWatershed")
            requestedlist = parameters.split(';')
            globalwshdAttr = [row[0] for row in arcpy.da.SearchCursor(afeature, 'GLOBALWSHD')]
            if len(globalwshdAttr) > 1:
                attrIndex = globalwshdAttr.index(1) # find index of global row (where GLOBALWSHD = 1)
                for attr in requestedlist:
                    plistItem = [item for item in plist if item['code'] == attr][0]
                    try:
                        values = [row[0] for row in arcpy.da.SearchCursor(afeature, attr)]
                        # if the global value == None, send None back to services
                        if (values[attrIndex] == None):
                            plistItem["value"] = None
                    except:
                        # if searchCursor fails to find the parameter, send None back to services
                        plistItem["value"] = None

            return plist
        except:
            tb = traceback.format_exc() 
            self._sm("Error reading attributes "+tb,"ERROR")
    def _getDirectory(self, subDirectory):
        if os.path.exists(subDirectory): 
            shutil.rmtree(subDirectory)
        os.makedirs(subDirectory)

        return subDirectory
    def _workspaceValid(self, workspace):
        if not arcpy.Exists(workspace):
            self._sm("Workspace " + workspace + " does not exist")
            return False

        self._sm("Workspace " + workspace + " is valid")
        return True
    def _setScratchWorkspace(self, directory):
        if (arcpy.Exists(os.path.join(directory,"scratch.gdb"))):
            arcpy.Delete_management(os.path.join(directory,"scratch.gdb"))
        arcpy.CreateFileGDB_management(directory,'scratch.gdb')
        return os.path.join(directory,"scratch.gdb")  
    def _SSXMLPath(self, xmlFileName, newTempWorkspace = "#"):
        file = None
        xmlFile =''
        try:
            #return self._SSXMLPath("StreamStats{0}.xml".format(self.RegionID),'#',self._TempLocation)
            #move the file to tempDirectory
            if os.path.exists(os.path.join(self._TempLocation, xmlFileName)):
                xmlFile = os.path.join(self._TempLocation, xmlFileName)
                self._sm("Using existing xmlFile "+xmlFile)
            else:
            #default location
                xmlFile = os.path.join(self._xmlPath,xmlFileName)  
                self._sm("Using default xmlFile "+xmlFile);          
                shutil.copy(xmlFile, self._TempLocation)
                xmlFile = os.path.join(self._TempLocation,xmlFileName)
                self._sm("moved default xmlFile to temp "+xmlFile);  
                if newTempWorkspace == "#":
                    return xmlFile

                #update tempworkspace
                xmlDoc = xml.dom.minidom.parse(xmlFile)
                xmlDoc.getElementsByTagName('TempLocation')[0].firstChild.data = newTempWorkspace
                file = open(xmlFile,"wb")
                xmlDoc.writexml(file)
                self._sm("renamed temp location");  

            return xmlFile
        except:
             tb = traceback.format_exc()
             self._sm(tb,"ERROR")
             return os.path.join(self._xmlPath,xmlFileName)
        finally:
            if file != None and not file.closed: 
                file.close 
                file = None
    def _sm(self, msg, type = 'INFO'):
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
                parser.add_argument("-stabbr", help="specifies the state abbreviation", type=str, default="VT")
                parser.add_argument("-workspaceID", help="specifies the working folder", type=str, default="VT20201112110902682000")
                parser.add_argument("-parameters", help="specifies the ';' separated list of parameters to be computed", type=str, default = "CENTROIDX;CENTROIDY;DRNAREA;EL1200;LC06STOR;LC11DEV;LC11IMP;OUTLETX;OUTLETY;PRECPRIS10")
                parser.add_argument("-directory", help="specifies the projects working directory", type=str, default = r"C:\Users\kjacobsen\Documents\wim_projects\docs\new-data\vt")
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


#------------------------------------------------------------------------------
#----- Delineation.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2016 WiM - USGS

#    authors:  Jeremy K. Newson USGS Wisconsin Internet Mapping
# 
#   purpose:  wrapper around archydro's navigation methods
#          
#discussion:  
#       

#region "Comments"
#06.01.2016 jkn - Created
#06.01.2016 jkn - initial navigation: Find network path
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
import ArcHydroTools
import arcpy.cartography as CA
import logging
import xml.dom.minidom

#endregion

class NetworkNav(object):
    #region Constructor
    def __init__(self, directory, rcode,workspaceID):
        self.__xmlPath = r"D:\ss_apps\XML"
        self.__schemaPath = r"D:\ss_socs\ss_gp\schemas"
        self.__rccode = rcode
        self.__globalWatershed = None
        if (workspaceID != None): self.__globalWatershed = os.path.join(directory,workspaceID,workspaceID+".gdb","Layers","GlobalWatershed") 
        
        self.WorkspaceDirectory = self.__getDirectory(os.path.join(directory, "NN_"+rcode + str(datetime.datetime.now()).replace('-','').replace(' ','').replace(':','').replace('.','')))
        self.__templatePath = os.path.join(self.__schemaPath,rcode + "_ss.gdb","Layers")
        self.Features = []
        self.NHDTraceReport=""
        self.Message =""
        self.IsInitialized=False
        self.__TempDirectory = os.path.join(self.WorkspaceDirectory,"Temp")
        
        #set up logging
        logdir = os.path.join(self.__TempDirectory, 'NetworkNavigation.log')
        logging.basicConfig(filename=logdir, format ='%(asctime)s %(message)s', level=logging.DEBUG)

        arcpy.env.overwriteOutput = True
        arcpy.env.workspace = self.__TempDirectory
        arcpy.env.scratchWorkspace = self.__TempDirectory

        self.IsInitialized = True
        self.__sm("Initialized for "+str(rcode))                 
    #endregion   
    def dispose(self):
        arcpy.Delete_management(self.__TempDirectory)
        arcpy.Delete_management(self.WorkspaceDirectory) 
    #region Methods  
    def Execute(self, pointlist, method, incrs = 4326, traceDirectionOption=None, traceLayersOption=None):
        sr = None
        pFC = None
        datasr = None
        pFCprojected = None
        result = None
        resultreprojected = None
        drainID = None
        try:
            if pointlist == None: raise Exception('At least one point must be passed in.');    
            #self.__sm("pointList:"+ json.dumps(result=[e.serialize() for e in pointlist]) +" Method: "+ str(method)) 
            
            if self.__workspaceExists(self.__globalWatershed):
                drainID = self.__getFeatureValue("DrainID")


            self.__sm("Processing input points.")   
            sr = arcpy.SpatialReference(int(incrs))
            pFC = self.__JsonToFeature(pointlist,sr,"", drainID)

            self.__sm("Loading Template workspace and reprojecting to match workspace.")
            datasr = arcpy.Describe(self.__templatePath).spatialReference
            pFCprojected = self.__toProjection(pFC,datasr)
            
            self.__sm("Navigation method Started") 
            datasetPath = arcpy.CreateFileGDB_management(self.__TempDirectory, "NN" +'.gdb')[0]
            featurePath = arcpy.CreateFeatureDataset_management(datasetPath,'Layers', datasr)[0]           

            xmlPath = self.__SSXMLPath("StreamStats{0}.xml".format(self.__rccode), self.__TempDirectory, self.__TempDirectory)

            arcpy.CheckOutExtension("Spatial")
            self.__sm("Started computations")
            if method == 1:
                self.__sm("Selecting find network path") 
                result = ArcHydroTools.StreamstatsFindNetworkPath(pFCprojected,'HYDRO_NET',os.path.join(featurePath,'networkpath'),xmlPath)
                self.__sm(arcpy.GetMessages(),'AHMSG')
                self.Features.append({
                                    "name" : "networkpath",                                  
                                    "feature": self.__ToJSON(self.__toProjection(result,sr))
                                    })
                
            elif method == 2:
                self.__sm("Selecting Flow Path Trace") 
                result = ArcHydroTools.StreamstatsFlowPathTrace(pFCprojected,os.path.join(featurePath,'raindroptrace'),self.__globalWatershed, xmlPath)  
                self.__sm(arcpy.GetMessages(),'AHMSG')
                self.Features.append({
                                    "name" : "raindroptrace",                                  
                                    "feature": self.__ToJSON(self.__toProjection(result,sr))
                                    })   
            elif method == 3:
                self.__sm("Selecting Trace to network") 
                networktraceds = os.path.join(featurePath,'networktrace')
                pathtonetwork = os.path.join(featurePath,'pathtonetwork')
                intersectpoint = os.path.join(featurePath,'intersectpoint')
                ArcHydroTools.StreamstatsTracetoNetwork(pFCprojected,'HYDRO_NET',networktraceds,pathtonetwork,intersectpoint, xmlPath)  
                self.__sm(arcpy.GetMessages(),'AHMSG')  
                self.Features.append({
                                    "name" : "networktrace",                                  
                                    "feature": self.__ToJSON(self.__toProjection(networktraceds,sr))
                                    })
                self.Features.append({
                                    "name" : "pathtonetwork",                                  
                                    "feature": self.__ToJSON(self.__toProjection(pathtonetwork,sr))
                                    }) 
                self.Features.append({
                                    "name" : "intersectpoint",                                  
                                    "feature": self.__ToJSON(self.__toProjection(intersectpoint,sr))
                                    })  
            elif method == 4:
                self.__sm("Selecting NHD Trace") 
                #get optional trace methods
                direction = traceDirectionOption if traceDirectionOption != None else "Both"
                layers = traceLayersOption if traceLayersOption != None else "NHDFlowline"
                result = ArcHydroTools.StreamstatsDoNHDTrace(pFCprojected,'HYDRO_NET',direction,layers,os.path.join(self.__TempDirectory,"nhdsearch.htm"), xmlPath)  
                self.__sm(arcpy.GetMessages(),'AHMSG')
                with open(os.path.join(self.__TempDirectory,"nhdsearch.htm")) as f:
                          self.NHDTraceReport = f.read()
                
            else:
                return false  

            return True          
        except:
            tb = traceback.format_exc()
            self.__sm("Failed to include feature " + tb,"ERROR") 
        finally:
            arcpy.CheckInExtension("Spatial")
            self.__sm("finished calc params")
            sr = None
            pFC = None
            datasr = None
            pFCprojected = None
            result = None            
    #endregion  
      
    #region Helper Methods
    def __getDirectory(self, subDirectory, makeTemp = True):
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

    def __JsonToFeature(self, pptArray, spatialRef, fcpath = '', drainAttr=None):
        rows = None
        FC = None
        try:
            #get spatial ref
            
            #Final result Feature Class
            #FC = arcpy.CreateFeatureclass_management("in_memory", "FC", "POINT", "", "DISABLED", "DISABLED", sr, "", "0", "0", "0")
            if(fcpath == ''):
                FC = arcpy.CreateFeatureclass_management("in_memory", "FC", "POINT", spatial_reference=spatialRef)
            else:
                FC = arcpy.CreateFeatureclass_management(fcpath, "FC", "POINT", spatial_reference=spatialRef)

            #add required attributes
            arcpy.AddField_management(FC, "Name", "TEXT", field_length=50)
            arcpy.AddField_management(FC, "Descript", "TEXT", field_length=200)
            arcpy.AddField_management(FC, "BatchDone", "SHORT")
            arcpy.AddField_management(FC, "SnapOn", "SHORT")
            arcpy.AddField_management(FC, "SrcType", "SHORT")
            if drainAttr: arcpy.AddField_management(FC, "DrainID", "LONG")
            # Create insert cursor for table
            for item in pptArray:
                rows = arcpy.InsertCursor(FC)            
                #add the json geometry to row

                row = rows.newRow()

                row.shape = arcpy.AsShape({"type":"Point","coordinates":item.point})

                #add value to field
                row.setValue("Name", item.name)
                row.setValue("Descript", "")
                row.setValue("BatchDone", 0)
                row.setValue("SnapOn", 1)
                row.setValue("SrcType", item.srctype)
                if drainAttr: row.setValue("DrainID", drainAttr)
                rows.insertRow(row)

            return FC
        except:
            tb = traceback.format_exc()
            print tb
        finally:
            #local cleanup
            del row
            del rows

    def __workspaceExists(self, workspace):
         if workspace == None: return False
         return arcpy.Exists(workspace)

    def __getFeaturesList(self):
        try:           
            #open feature/ loop through and add to array
            for fc in arcpy.ListFeatureClasses():
                self.FeaturesList.append(fc.lower())  
        except:
            tb = traceback.format_exc()
            self.__sm("Featurelist Error "+tb,"ERROR")
         
    def __ToJSON(self, fClass):
        featSet = None
        try:
            featSet = arcpy.FeatureSet()
            featSet.load(fClass)
            jsonStr = arcpy.Describe(featSet).json

            return json.loads(jsonStr)
        except:
            tb = traceback.format_exc()
            self.__sm("Failed to serialize " + tb,"ERROR")
    
    def __toProjection(self, inFeature, sr):
        fromCRS = None
        desc = None  
        projectedFC = None        
        try:

            desc = arcpy.Describe(inFeature)
            fromCRS = desc.spatialReference.name
            projectFC = os.path.join(self.__TempDirectory, desc.name +".shp")
            
            if arcpy.Exists(projectFC):
                self.__sm("deleting old temp file")
                arcpy.Delete_management(projectFC)
            
            if sr.name == desc.spatialReference.name:
                return inFeature
            self.__sm("Projecting from: "+ str(fromCRS) + " To: " + str(sr.name))
            return arcpy.Project_management(inFeature,projectFC,sr)
        except:
            tb = traceback.format_exc()                  
            self.__sm("Error Reprojecting: " + tb +" "+ arcpy.GetMessages(),"ERROR")
            return None
        finally:
            sr = None

    def __SSXMLPath(self, xmlFileName, copyToDirectory="#", newTempWorkspace = "#"):
        file = None
        try:
            #move the file to tempDirectory
            xmlFile = os.path.join(self.__xmlPath, xmlFileName)
            if copyToDirectory != "#":
                shutil.copy(xmlFile, copyToDirectory)
                xmlFile = os.path.join(copyToDirectory,xmlFileName)

            if newTempWorkspace == "#":
                return xmlFile

            #update tempworkspace
            xmlDoc = xml.dom.minidom.parse(xmlFile)
            xmlDoc.getElementsByTagName('TempLocation')[0].firstChild.data = newTempWorkspace
            file = open(xmlFile,"wb")
            xmlDoc.writexml(file)

            return xmlFile
        except:
             tb = traceback.format_exc()
             self.__sm__(tb,"ERROR")
        finally:
            if file != None and not file.closed: 
                file.close 
                file = None
    def __getFeatureValue(self, fieldName):
        try:           
            #open feature/ loop through and add to array
            self.__sm("Opening search cursor")
            with arcpy.da.SearchCursor(self.__globalWatershed,fieldName,"GlobalWshd = 1") as cursor:
                for row in cursor: 
                    #should only be 1
                    val = row[0]
                    return val
                #next row
            #end with
        except:
            tb = traceback.format_exc()
            self.__sm("Featurelist Error "+tb,"ERROR")
            return None
    def __sm(self, msg, type = 'INFO'):
        self.Message += type +':' + msg.replace('_',' ') + '_'

        if type in ('ERROR'): logging.error(msg)
        else : logging.info(msg)
    #endregion


##-------1---------2---------3---------4---------5---------6---------7---------8
##       Main
##-------+---------+---------+---------+---------+---------+---------+---------+
class NetworkNavWrapper(object):
    #region Constructor
    def __init__(self):
        dodelete = False
        try:
            #http://stackoverflow.com/questions/8107713/using-argparse-argumenterror-in-python
            parser = argparse.ArgumentParser()
            parser.add_argument("-workspaceID", help="specifies the working folder", type=str, default=None)
            parser.add_argument("-directory", help="specifies the projects working directory", type=str, default = r"D:\gistemp\ClientData")  
            parser.add_argument("-rcode", help="specifies the abbr state name", type=str, default="RRB")          
            parser.add_argument("-method", help="specifies the method 1 = find network path", type=int, choices=[1,2,3,4], default = 2)
            parser.add_argument("-startpoint", help="specifies the array of point", type=json.loads, default = '[-94.719923,48.47219]') 
            parser.add_argument("-endpoint", help="specifies the array of point", type=json.loads, default = None)  
            parser.add_argument("-inputcrs", help="specifies the input projection use",type=int, default=4326)    
            parser.add_argument("-tracedirection", help="specifies Navigation Options",type=str, default=None)   
            parser.add_argument("-tracelayers", help="specifies Navigation Options",type=str, default=None)                 
            args = parser.parse_args()

            pointArray = []
            pointArray.append(NavPoint("startpoint",1,args.startpoint))
            optionalEndpoint = args.endpoint
            if(optionalEndpoint != None):pointArray.append(NavPoint("endpoint",0,optionalEndpoint )) 
            
            networkNav = NetworkNav(args.directory, args.rcode, args.workspaceID)
            if(networkNav.IsInitialized):
                if(networkNav.Execute(pointArray, args.method, args.inputcrs, args.tracedirection, args.tracelayers)):
                    
                    Results = {
                               "Features":networkNav.Features,
                               "NHDTraceReport":networkNav.NHDTraceReport,
                               "Message": networkNav.Message.replace("'",'"').replace('\n',' ')
                              }
                else:
                    Results = {
                       "error": {"message": "Failed to execute." + networkNav.Message}
                       }
            #Only dispose if successful
            doDelete= True
        except:
             tb = traceback.format_exc()
             Results = {
                       "error": {"message": traceback.format_exc() + str(parser.error)}
                       }
        finally:
            print "Results="+json.dumps(Results)
            if doDelete: networkNav.dispose()
            
            
    def validJson (self, string ):
        value = string
        try:
            if value is not None and value != '':
                print value
                return json.loads(value)
            else:
                print "json point is None"
                return None
        except:
             tb = traceback.format_exc()
             print tb
  
class NavPoint:
    def __init__(self, name, stype, pnt):
        self.name = name
        self.srctype = stype
        self.point = pnt
class NavOptions:
    def __init__(self, name, value):
        self.name = name
        self.value = value
                     
if __name__ == '__main__':
    NetworkNavWrapper()


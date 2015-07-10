#------------------------------------------------------------------------------
#----- Feature.py ----------------------------------------------------
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
#import arcpy.cartography as CA
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

        #set up logging
        logdir = os.path.join(self.__MainDirectory__, 'Feature.log')
        logging.basicConfig(filename=logdir, format ='%(asctime)s %(message)s', level=logging.DEBUG)

         #Test if workspace exists before run   
        if(not self.__workspaceExists__(os.path.join(self.__MainDirectory__, self.WorkspaceID+".gdb","Layers"))):   
            self.__sm__("workspace: "+ os.path.join(self.__MainDirectory__, self.WorkspaceID+".gdb","Layers") + " does not exist", "ERROR")
            return
         
        arcpy.env.workspace =  os.path.join(self.__MainDirectory__, self.WorkspaceID+".gdb","Layers")
        self.__sm__("Initialized")

        self.__getFeaturesList__()
                 
    #endregion   
        
    #region Methods   
   
    def GetFeatures(self, featurelist=''):
        
        try:
            if featurelist == '':
                for fname in self.FeaturesList:
                    self.Features.append({"name" : fname})
                return

            else:
                for f in map(lambda s: s.strip(), featurelist.split(';')):
                    if f.lower() in self.FeaturesList:
                        self.Features.append({
                                                "name" : f,                                  
                                                "feature": self.__ToJSON__(f)
                                              })
        except:
            tb = traceback.format_exc()
            self.__sm__("Failed to include feature " + tb,"ERROR") 
   
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
            parser.add_argument("-workspaceID", help="specifies the working folder", type=str, default="IA20150619101449524000")
            parser.add_argument("-directory", help="specifies the projects working directory", type=str, default = r"D:\gistemp\ClientData")              
            parser.add_argument("-includefeatures", help="specifies the projects working directory", type=str, default = r"")            
            args = parser.parse_args()

            
            Results = {"Message": "INFO:Initialized_", "Features": [{"name": "globalwatershedpoint"}, {"name": "globalwatershedraw"}, {"name": "globalwatershed"}], "Workspace": "IA20150619101449524000"}


        except:
             tb = traceback.format_exc()
             Results = {
                       "error": {"message": traceback.format_exc()}
                       }

        finally:
            print "Results="+json.dumps(Results) 

if __name__ == '__main__':
    FeaturesWrapper()


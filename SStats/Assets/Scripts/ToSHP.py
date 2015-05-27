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
#endregion


##-------1---------2---------3---------4---------5---------6---------7---------8
##       ConvertToSHP
##-------+---------+---------+---------+---------+---------+---------+---------+

class ConvertToSHP(object):
    #region Constructor
    def __init__(self,directory, workspaceID):  
        self.WorkspaceID = workspaceID
        self.isComplete = False
        self.Message =""    
        self.__MainDirectory__ = os.path.join(directory,self.WorkspaceID)

        logdir = os.path.join(os.path.join(self.__MainDirectory__,"Temp"), 'ToShape.log')
        logging.basicConfig(filename=logdir, format ='%(asctime)s %(message)s', level=logging.DEBUG)
        #Test if workspace exists before run   
        if(not self.__workspaceExists__(os.path.join(self.__MainDirectory__, self.WorkspaceID+".gdb","Layers"))):   
            self.__sm__("workspace: "+ os.path.join(self.__MainDirectory__, self.WorkspaceID+".gdb","Layers") + " does not exist", "ERROR")
            return
               
        self.__run__()    
    #endregion  
         
    #Private Methods
    def __run__(self):
        newdirname = "Layers"
        inFeatures = None
        FtoShp = None
        try:
            arcpy.env.workspace =  os.path.join(self.__MainDirectory__, self.WorkspaceID+".gdb","Layers")
            self.__sm__('workspace set: '+self.WorkspaceID)
            outLocation = self.__getDirectory__(os.path.join(self.__MainDirectory__,newdirname))
            inFeatures = arcpy.ListFeatureClasses() #This will perform this on the listed workspace from above.
            self.__sm__('Found '+ str(len(inFeatures)) +' features')
            FtoShp = arcpy.FeatureClassToShapefile_conversion (inFeatures, outLocation,)
            self.WorkspaceID= os.path.join(self.WorkspaceID, newdirname)
            self.__sm__(arcpy.GetMessages(),'arcmsg')
            self.isComplete = True
        except:
            tb = traceback.format_exc() 
            self.__sm__("Error converting shape "+tb,"ERROR")
            self.isComplete = False     
        finally:
            del inFeatures
            del FtoShp
    def __getDirectory__(self, subDirectory):
        if os.path.exists(subDirectory): 
            shutil.rmtree(subDirectory)
        os.makedirs(subDirectory);

        return subDirectory
    def __sm__(self, msg, type = ''):
        self.Message += type +' ' + ' ' + msg + '_'

        if type in ('ERROR'): logging.error(msg)
        else : logging.info(msg)
    def __workspaceExists__(self, workspace):
         return arcpy.Exists(workspace)

    #endregion


##-------1---------2---------3---------4---------5---------6---------7---------8
##       Main
##-------+---------+---------+---------+---------+---------+---------+---------+        
class ConversionWrapper(object):
    #region Constructor
        def __init__(self):
            try:
                parser = argparse.ArgumentParser()
                parser.add_argument("-workspaceID", help="specifies the working folder", type=str, default="IA20141112093901899000")
                parser.add_argument("-directory", help="specifies the projects working directory", type=str, default = r"D:\gistemp\ClientData")
                parser.add_argument("-toType", help="specifies the type to convert to, 2 = .gdb, 1 = .shp", type=int, choices=[1,2], default = 1)
                args = parser.parse_args()

                if args.toType == 1:
                    cShp = ConvertToSHP(args.directory, args.workspaceID)
                    if cShp.isComplete:
                        Results = {"Workspace": cShp.WorkspaceID,"Message":cShp.Message}
                    else:
                        Results = {"Workspace": "","Message":cShp.Message}
            except:
                Results = {"Workspace": "Error", "Message":traceback.format_exc()}

            finally:
                print "Results="+json.dumps(Results)   
    #endregion    

# specifies that this class can be ran directly
if __name__ == '__main__':
    ConversionWrapper()

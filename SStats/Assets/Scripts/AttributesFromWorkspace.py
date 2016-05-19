#------------------------------------------------------------------------------
#----- BasinParameters.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2014 WiM - USGS

#    authors:  Jeremy K. Newson USGS Wisconsin Internet Mapping
# 
#   purpose:  Gets ss parameters from a given watershed
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
import decimal
#endregion


##-------1---------2---------3---------4---------5---------6---------7---------8
##       BasinParameters
##-------+---------+---------+---------+---------+---------+---------+---------+

class AttributesFromWorkspace(object):
    #region Constructor
    def __init__(self, directory, workspaceID, aList):
        self.WorkspaceID = workspaceID
        self.isComplete = False
        self.Message =""    
        self.__MainDirectory__ = os.path.join(directory,self.WorkspaceID)
        self.AttributeList = None

        logdir = os.path.join(os.path.join(self.__MainDirectory__,"Temp"), 'attribute.log')
        logging.basicConfig(filename=logdir, format ='%(asctime)s %(message)s', level=logging.DEBUG)
         
        #Test if workspace exists before run   
        if(not self.__workspaceExists__(os.path.join(self.__MainDirectory__, self.WorkspaceID+".gdb","Layers"))):
            return
        self.__run__(aList)  
            
    #endregion  
         
    #Private Methods
    def __run__(self, attributes):
        alist = []
        try:
            self.__sm__("Opening search cursor")
            afeature = os.path.join(self.__MainDirectory__, self.WorkspaceID+".gdb","Layers","GlobalWatershed")
            requestedlist = attributes.split(';')
            with arcpy.da.SearchCursor(afeature,requestedlist) as cursor:
                for row in cursor:
                    for i in range(0,len(row)):
                        val = row[i]
                        nm = requestedlist[i]
                        alist.append({"name" : nm, "value":val})
                    #next i
                #next row
            #end with

            if (len(alist) < 1):
                raise Exception("No parameters returned")          


            self.AttributeList = alist
            self.isComplete = True

            self.__sm__("finished")
        except:
            tb = traceback.format_exc() 
            self.__sm__("Error reading attributes "+tb,"ERROR")
            self.isComplete = False     
    def __getDirectory__(self, subDirectory):
        if os.path.exists(subDirectory): 
            shutil.rmtree(subDirectory)
        os.makedirs(subDirectory);

        return subDirectory
    def __workspaceExists__(self, workspace):
        if arcpy.Exists(workspace):
            self.__sm__(workspace + " exists")
            return True
        else:
            self.__sm__(workspace + " does not exists")
            return False
    def __sm__(self, msg, type = 'INFO'):
        self.Message += type +':' + msg.replace('_',' ') + '_'

        if type in ('ERROR'): logging.error(msg)
        else : logging.info(msg)
    #endregion

##-------1---------2---------3---------4---------5---------6---------7---------8
##       Main
##-------+---------+---------+---------+---------+---------+---------+---------+        
class AttributesFromWorkspaceWrapper(object):
    #region Constructor
        def __init__(self):
            try:
                parser = argparse.ArgumentParser()
                parser.add_argument("-workspaceID", help="specifies the working folder", type=str, default="OH20160517094142993000")
                parser.add_argument("-attributes", help="specifies the ';' separated list of attributes to be return", type=str, default = "LC92STOR;Q10")
                parser.add_argument("-directory", help="specifies the projects working directory", type=str, default = r"D:\gistemp\ClientData")
                args = parser.parse_args()
                
                ssBp = AttributesFromWorkspace(args.directory, args.workspaceID, args.attributes)

                if ssBp.isComplete:
                    Results = {"Attributes": ssBp.AttributeList, "Message": ssBp.Message.replace("'",'"').replace('\n',' ')}
                else:
                    Results = {"Attributes": [],"Message": ssBp.Message.replace("'",'"').replace('\n',' ')}

            except:
                Results = {"error":traceback.format_exc()}

            finally:
                print "Results="+json.dumps(Results)   
    #endregion 
   

# specifies that this class can be ran directly
if __name__ == '__main__':
    AttributesFromWorkspaceWrapper()


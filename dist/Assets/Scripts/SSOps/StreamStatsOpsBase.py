#------------------------------------------------------------------------------
#----- StreamStatsOpsBase.py --------------------------------------------------
#------------------------------------------------------------------------------
#
#  copyright:  2018 WiM - USGS
#
#    authors:  Jeremy K. Newson - USGS Web Informatics and Mapping (WiM)
#              
#    purpose:  Contains reusable global Streamstats methods
#
#      usage:  THIS SECTION NEEDS TO BE UPDATED
#
# discussion:  
#
#      dates:   31 JAN 2018 jkn - Created 
#
#------------------------------------------------------------------------------

#region "Imports"
import shutil
import sys
import os
import tempfile
import traceback
import json
from  WiMPy import WiMLogging
from abc import ABCMeta, abstractmethod

#endregion

##-------1---------2---------3---------4---------5---------6---------7---------8
##       StreamStatsOpsBase
##-------+---------+---------+---------+---------+---------+---------+---------+
class StreamStatsOpsBase(object):

    #region Constructor
    def __init__(self, workspacePath):
        __metaclass__ = ABCMeta
        #public properties
        
        #protected properties
        self._WorkspaceDirectory = workspacePath
        self._TempLocation = tempfile.mkdtemp(dir=os.path.join(self._WorkspaceDirectory,"Temp"))  
        self._setEnvironments()

        self._sm("initialized StreamStatsOpsBase")
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self._resetEnvironments()
            shutil.rmtree(self._TempLocation, True)
                        
        except:
            self._sm("Failed to remove temp space on close StreamstatsOpsBase","ERROR",50)
    
    #endregion 
    #region Helper methods
    def _workspaceExists(workspaceID):
        try:
            return True
        except:
            return False

    @abstractmethod
    def _resetEnvironments(self):
        '''To override'''
        pass
    @abstractmethod
    def _setEnvironments(self):
        '''To override'''
        pass
    def _sm(self,msg,type="INFO", errorID=0):        
        WiMLogging.sm(msg,type="INFO", errorID=0)
    #endregion
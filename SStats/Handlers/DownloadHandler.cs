﻿//------------------------------------------------------------------------------
//----- FileHandler -----------------------------------------------------------
//------------------------------------------------------------------------------

//-------1---------2---------3---------4---------5---------6---------7---------8
//       01234567890123456789012345678901234567890123456789012345678901234567890
//-------+---------+---------+---------+---------+---------+---------+---------+

// copyright:   2012 WiM - USGS

//    authors:  Jon Baier USGS Wisconsin Internet Mapping
//              Jeremy K. Newson USGS Wisconsin Internet Mapping
//              
//  
//   purpose:   Handles File resources through the HTTP uniform interface.
//              Equivalent to the controller in MVC.
//
//discussion:   Handlers are objects which handle all interaction with resources in 
//              this case the resources are POCO classes derived from the EF. 
//              https://github.com/openrasta/openrasta/wiki/Handlers
//
//     

#region Comments
// 02.14.13 - JKN - created
#endregion

using OpenRasta.IO;
using OpenRasta.Web;


using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Runtime.InteropServices;
using System.Configuration;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Web;
using System.Xml.Serialization;

using WiM.Exceptions;

using SStats.Utilities;
using SStats.Utilities.ServiceAgent;

namespace SStats.Handlers
{
    public class DownloadHandler
    {
        [HttpOperation(HttpMethod.GET, ForUriName = "DownloadZipFile")]
        public OperationResult DownloadZipFile(string workspaceID,[Optional] string f)
        {

            InMemoryFile fileItem;
            fileTypeEnum fType = fileTypeEnum.e_geodatabase;
            SSServiceAgent sAgent = null;
            try
            {
                //Return BadRequest if there is no ID 
                if (string.IsNullOrEmpty(workspaceID)) return new OperationResult.BadRequest() { ResponseResource = "no filename specified" };
               
                fType = getFileTypeByName(f);             
                sAgent = new SSServiceAgent(workspaceID);

                fileItem = new InMemoryFile(sAgent.GetFileItem((Int32)fType));                
                fileItem.FileName = "SS_"+workspaceID + ".zip";
          
                return new OperationResult.OK { ResponseResource = fileItem };

            }
            catch (BadRequestException ex)
            {
                return new OperationResult.BadRequest { ResponseResource = ex.Message.ToString(), Title = "What" };
            }
            catch (Exception ex)
            {

                return new OperationResult.InternalServerError { ResponseResource = "Item: " + workspaceID + ex.Message };
            }
        }//end HttpMethod.GET

        #region Helper Methods
        private fileTypeEnum getFileTypeByName(string filetypeName)
        {
            try
            {
                switch (filetypeName.ToUpper())
                {
                    case "SHAPE":
                    case "SHP":
                        return fileTypeEnum.e_shape;
                    default:
                        return fileTypeEnum.e_geodatabase;
                }
            }
            catch (Exception)
            {
                return fileTypeEnum.e_geodatabase;
            }
        }
        #endregion

        #region Enumerations
        private enum fileTypeEnum
        {
            e_shape = 1,
            e_geodatabase = 2
        }
        #endregion
    }//end class
}//end namespace
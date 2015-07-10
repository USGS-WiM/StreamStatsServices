//------------------------------------------------------------------------------
//----- HttpHandler ---------------------------------------------------------
//------------------------------------------------------------------------------

//-------1---------2---------3---------4---------5---------6---------7---------8
//       01234567890123456789012345678901234567890123456789012345678901234567890
//-------+---------+---------+---------+---------+---------+---------+---------+

// copyright:   2014 WiM - USGS

//    authors:  Jeremy K. Newson USGS Wisconsin Internet Mapping
//              
//  
//   purpose:   Handles Site resources through the HTTP uniform interface.
//              Equivalent to the controller in MVC.
//
//discussion:   Handlers are objects which handle all interaction with resources in 
//              this case the resources are POCO classes derived from the EF. 
//              https://github.com/openrasta/openrasta/wiki/Handlers
//
//     

#region Comments
// 02.21.14 - JKN - Created
#endregion
using OpenRasta.Web;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Runtime.InteropServices;

using SStats.Resources;
using SStats.Utilities.ServiceAgent;
using WiM.Resources.Spatial;
namespace SStats.Handlers
{
    public class FeatureHandler
    {
        [HttpOperation(HttpMethod.GET)]
        public OperationResult Get(string workspaceID, [Optional] string featureList, [Optional] String simplificationOption)
        {
            List<FeatureWrapper> result = null;
            SSServiceAgent agent = null;
            try
            {
                if (string.IsNullOrEmpty(featureList)) featureList = string.Empty;
                  //1 = full, 2 = simplified
                Int32 simplifyID = includeMethod(ref simplificationOption) ? 2 : 1;

                agent = new SSServiceAgent(workspaceID);
                result = agent.GetFeatures(featureList, simplifyID);

                

                return new OperationResult.OK { ResponseResource = new Features() { FeatureList = result, Messages = agent.Messages } };
            }
            catch (Exception ex)
            {
                return new OperationResult.InternalServerError { ResponseResource = ex.Message.ToString() };
            }
            finally
            {
                result = null;
                agent = null;

            }//end try
        }//end Get

        #region Helper Methods
        private Boolean includeMethod(ref string boolean)
        {
            try
            {
                switch (boolean.ToLower().Trim())
                {
                    case"false":
                    case "f":
                    case"0":
                    case"no":
                        return false;
                    case "true":
                    case "t":
                    case "1":
                    case "yes":
                        boolean = string.Empty;
                        return true;

                    default:
                        return true;
                }

            }
            catch (Exception)
            {
                return true;
            }
        }
        #endregion
    }//end class HttpHandler
}//end namespace
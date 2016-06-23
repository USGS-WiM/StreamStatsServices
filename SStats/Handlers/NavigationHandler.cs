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
using WiM.Exceptions;
namespace SStats.Handlers
{
    public class NavigationHandler
    {
        [HttpOperation(HttpMethod.GET)]
        public OperationResult Get(String regioncode, Int32 navmethod, string startpoint, Int32 espg, [Optional] string endpoint, [Optional] String workspaceID)
        {
            List<FeatureWrapper> result = null;
            SSServiceAgent agent = null;
            try
            {
                if (string.IsNullOrEmpty(regioncode) || string.IsNullOrEmpty(startpoint) || espg < 0) throw new BadRequestException("rcode, startpoint or espg are required and maybe invalid");
                //  //1 = FindNetworkPath, 2 = FlowPathTrace
                Int32 navCode = (navmethod < 1 || navmethod > 2) ? 1 : navmethod;

                agent = new SSServiceAgent();
                result = agent.GetNavigationFeatures(regioncode, navCode, startpoint, espg, endpoint, workspaceID);                

                return new OperationResult.OK { ResponseResource = new Features() { FeatureList = result, Messages = agent.Messages } };
            }
            catch (BadRequestException ex)
            {
                return new OperationResult.BadRequest { ResponseResource = ex.Message.ToString() };
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
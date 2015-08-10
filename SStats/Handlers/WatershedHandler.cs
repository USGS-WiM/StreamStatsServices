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
using WiM.Exceptions;

namespace SStats.Handlers
{
    public class WatershedHandler
    {
        [HttpOperation(HttpMethod.GET)]
        public OperationResult GetWatershed(String regioncode, Double X, Double Y, Int32 espg, [Optional] String simplificationOption,
                                            [Optional] String parameterList, [Optional] String flowtypeList,
                                            [Optional] String featureList)
        {
            //watershed?state=IA&xlocation=-10347402.453276031&ylocation=5174977.1176704019&wkid=102100
            Watershed SSresults = null;
            SSServiceAgent agent = null;
            try
            {
                if (espg < 0) throw new BadRequestException("spatial ref invalid");
                agent = new SSServiceAgent();
                SSresults = new Watershed();
                //1 = full, 2 = simplified
                Int32 simplifyID = includeMethod(ref simplificationOption) ? 2 : 1;

               //delineation
                agent.Delineate(X, Y, espg, regioncode);

                SSresults.workspaceID = agent.WorkspaceString;
                SSresults.Messages = agent.Messages;
                
                if (includeMethod(ref parameterList))
                    SSresults.Parameters = agent.GetParameters(regioncode, parameterList);

                if (includeMethod(ref featureList) && !String.IsNullOrEmpty(agent.WorkspaceString))
                {
                    if (string.IsNullOrEmpty(featureList)) featureList = "globalwatershedpoint;globalwatershed";
                    SSresults.FeatureList = agent.GetFeatures(featureList,espg,simplifyID);
                }//end if
                                
                return new OperationResult.OK { ResponseResource = SSresults };
            }
            catch (Exception ex)
            {
                return new OperationResult.InternalServerError { ResponseResource = ex.Message.ToString() + " path "+ agent.BasePath + " exe " + agent.BaseEXE };
            }
            finally
            {
                SSresults = null;
                agent = null;

            }//end try
        }//end Get

        [HttpOperation(HttpMethod.GET, ForUriName = "GetWatershedFromWorkspaceID")]
        public OperationResult GetWatershedFromWorkspaceID(String regioncode, string workspaceID, Int32 espg, [Optional] String simplificationOption,
                                                           [Optional] String parameterList, [Optional] String flowtypeList,
                                                           [Optional] String featureList)
        {
            Watershed SSresults = null;
            SSServiceAgent agent = null;
            try
            {
                if (string.IsNullOrEmpty(workspaceID) || string.IsNullOrEmpty(regioncode)) return new OperationResult.BadRequest { ResponseResource = "workspace and/or state cannot be null" };
                if (espg < 200) throw new BadRequestException("spatial ref invalid");

                //1 = full, 2 = simplified
                Int32 simplifyID = includeMethod(ref simplificationOption) ? 2 : 1;

                agent = new SSServiceAgent(workspaceID);
                SSresults = new Watershed();

                SSresults.workspaceID = agent.WorkspaceString;

                if (includeMethod(ref parameterList))
                    SSresults.Parameters = agent.GetParameters(regioncode, parameterList);

                if (includeMethod(ref featureList))
                {
                    if (string.IsNullOrEmpty(featureList)) featureList = "globalwatershedpoint;globalwatershed";
                    SSresults.FeatureList = agent.GetFeatures(featureList, espg, simplifyID);
                }//end if

                return new OperationResult.OK { ResponseResource = SSresults };
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
                SSresults = null;
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
                boolean = string.Empty;
                return true;
            }
        }
        #endregion
    }//end class HttpHandler
}//end namespace
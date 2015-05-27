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
namespace SStats.Handlers
{
    public class WatershedHandler
    {
        [HttpOperation(HttpMethod.GET)]
        public OperationResult GetWatershed(String regioncode, Double X, Double Y, Int32 espg, [Optional] String doSimplify,
                                            [Optional] String parameterList, [Optional] String flowtypeList,
                                            [Optional] String boolean)
        {
            //watershed?state=IA&xlocation=-10347402.453276031&ylocation=5174977.1176704019&wkid=102100
            Watershed SSresults = null;
            SSServiceAgent agent = null;
            try
            {
                
                agent = new SSServiceAgent();
                SSresults = new Watershed();
                //1 = full, 2 = simplified
                Int32 simplifyID = includeMethod(ref doSimplify) ? 2 : 1;

               //delineation

                agent.GetDelineation(X, Y, espg, simplifyID, regioncode);

                SSresults.workspaceID = agent.WorkspaceString;
                SSresults.Messages = agent.Messages;

                if (includeMethod(ref boolean) && agent.HasGeometry)
                {
                    SSresults.FeatureList.Add("delineatedbasin", agent.DelineationResultList[ResultType.e_basin]);
                    SSresults.FeatureList.Add("pourpoint", agent.DelineationResultList[ResultType.e_pourpoint]);
                }//end if

                if (includeMethod(ref parameterList))
                    SSresults.Parameters = agent.GetParameters(regioncode, parameterList);
                
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
        public OperationResult GetWatershedFromWorkspaceID(String regioncode, string workspaceID,
                                                           [Optional] String parameterList, [Optional] String flowtypeList, 
                                                           [Optional] String boolean)
        {
            Watershed SSresults = null;
            SSServiceAgent agent = null;
            try
            {
                agent = new SSServiceAgent();
                SSresults = new Watershed();

                if (string.IsNullOrEmpty(parameterList)) parameterList = string.Empty;
                if (string.IsNullOrEmpty(workspaceID)||string.IsNullOrEmpty(regioncode)) return new OperationResult.BadRequest { ResponseResource = "workspace and/or state cannot be null" };
                agent.WorkspaceString = workspaceID;
                
                SSresults.workspaceID = agent.WorkspaceString;

                if (includeMethod(ref boolean))
                {
                   //SSresults.DelineatedBasin = agent.DelineationResultList[SSServiceAgent.ResultType.e_basin];
                   // SSresults.PourPoint = agent.DelineationResultList[SSServiceAgent.ResultType.e_pourpoint];
                }//end if

                if (includeMethod(ref parameterList))
                    SSresults.Parameters = agent.GetParameters(regioncode, parameterList);

                return new OperationResult.OK { ResponseResource = SSresults };
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
                return true;
            }
        }
        #endregion
    }//end class HttpHandler
}//end namespace
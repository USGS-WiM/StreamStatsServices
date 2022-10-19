using Microsoft.AspNetCore.Mvc;
using OpenRasta.Web;
using SStats.Resources;
using SStats.Utilities.ServiceAgent;
using System.Runtime.InteropServices;
using System;
using WiM.Exceptions;

namespace SStats.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class WatershedController : Controller
    {
        [HttpGet(Name = "Watershed")]
        public OperationResult GetWatershed(String regioncode, Double X, Double Y, Int32 espg, [Optional] String simplificationOption,
                                            [Optional] String parameterList, [Optional] String flowtypeList,
                                            [Optional] String featureList)
        {
            //watershed?state=IA&xlocation=-10347402.453276031&ylocation=5174977.1176704019&wkid=102100
            //watershed?regioncode=IA&x=-10347402.453276031&y=5174977.1176704019&epsg=102100
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
                    SSresults.FeatureList = agent.GetFeatures(featureList, espg, simplifyID);
                }//end if

                return new OperationResult.OK { ResponseResource = SSresults };
            }
            catch (Exception ex)
            {
                return new OperationResult.InternalServerError { ResponseResource = ex.Message.ToString() + " path " + agent.BasePath + " exe " + agent.BaseEXE };
            }
            finally
            {
                SSresults = null;
                agent = null;

            }//end try
        }//end Get



        /*[HttpGet(Name = "GetWatershedFromWorkspaceID")]
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
        }//end Get*/



        [HttpPut(Name = "EditWatershed")]
        public OperationResult EditWatershed(WatershedEditDecisionList watershedEDL, String regioncode, string workspaceID, Int32 espg, [Optional] String simplificationOption,
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

                //edit watershed
                if (!agent.EditWatershed(watershedEDL, espg)) throw new Exception();

                SSresults = new Watershed();
                SSresults.Messages = agent.Messages;
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
                return new OperationResult.InternalServerError { ResponseResource = ex.Message.ToString() + " messages: " + agent.Messages };
            }
            finally
            {
                SSresults = null;
                agent = null;

            }//end try
        }//end Get




        private Boolean includeMethod(ref string boolean)
        {
            try
            {
                switch (boolean.ToLower().Trim())
                {
                    case "false":
                    case "f":
                    case "0":
                    case "no":
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



    }
}

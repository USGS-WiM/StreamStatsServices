//------------------------------------------------------------------------------
//----- FileHandler -----------------------------------------------------------
//------------------------------------------------------------------------------

//-------1---------2---------3---------4---------5---------6---------7---------8
//       01234567890123456789012345678901234567890123456789012345678901234567890
//-------+---------+---------+---------+---------+---------+---------+---------+

// copyright:   2012 WiM - USGS

//    authors:  Jeremy K. Newson USGS Wisconsin Internet Mapping
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

using WiM.Utilities.Storage;

using SStats.Utilities;
using SStats.Utilities.ServiceAgent;
using SStats.Resources;

namespace SStats.Handlers
{
    public class StatisticsHandler
    {
        [HttpOperationAttribute(HttpMethod.GET)]
        public OperationResult Get(String regioncode)
        {
            SSServiceAgent agent = null;
            try
            {
                agent = new SSServiceAgent();

                return new OperationResult.OK { ResponseResource = new FlowStatistics() { Messages = agent.Messages, FlowStatsList = agent.GetStateFlowStatistics(regioncode) } };
            }
            catch (Exception ex)
            {
                return new OperationResult.InternalServerError { ResponseResource = "Flow Statistic Service Error: " + ex.Message.ToString() };
            }
            finally
            {
                agent = null;

            }//end try
        }//end Get
        [HttpOperation(HttpMethod.GET, ForUriName = "GetParametersFromWorkspaceID")]
        public OperationResult GetFlowStatsFromWorkspaceID(String state, string workspaceID, [Optional] String flowtypeList)
        {
            Object flows;
            SSServiceAgent agent = null;
            string src = string.Empty;
            try
            {
                //Return BadRequest if there is no ID 
                if (string.IsNullOrEmpty(state)|| string.IsNullOrEmpty(workspaceID)) return new OperationResult.BadRequest() { ResponseResource = "no state or workspace specified" };
                if (string.IsNullOrEmpty(flowtypeList)) flowtypeList ="";

                agent = new SSServiceAgent();
                agent.WorkspaceString = workspaceID;

                flows = agent.GetFlowStatistics(state, flowtypeList);                   
          
                return new OperationResult.OK { ResponseResource = flows };

            }
            catch (Exception ex)
            {
                return new OperationResult.InternalServerError { ResponseResource = "error" };
            }
        }//end HttpMethod.GET
    }
}
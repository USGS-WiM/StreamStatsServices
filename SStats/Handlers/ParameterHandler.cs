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
//   purpose:   Handles basin charactersitic resources through the HTTP uniform interface.
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
    public class ParameterHandler
    {
        [HttpOperationAttribute(HttpMethod.GET)]
        public OperationResult Get(String regioncode, [Optional] String group)
        {
            SSServiceAgent agent = null;
            try
            {
                agent = new SSServiceAgent();        
                
                return new OperationResult.OK { ResponseResource = new Parameters(){ Messages = agent.Messages, ParameterList= agent.GetStateAvailableParameters(regioncode, group)} };
            }
            catch (Exception ex)
            {
                return new OperationResult.InternalServerError { ResponseResource = "Parameter Service Error: " + ex.Message.ToString() };
            }
            finally
            {
                agent = null;

            }//end try
        }//end Get

        [HttpOperation(HttpMethod.GET, ForUriName = "GetParametersFromWorkspaceID")]
        public OperationResult GetParametersFromWorkspaceID(String regioncode, String workspaceID, String parameterList)
        {
            SSServiceAgent agent = null;
            Parameters wp = new Parameters();
            try
            {
                agent = new SSServiceAgent();
                agent.WorkspaceString = workspaceID;
                wp.ParameterList = agent.GetParameters(regioncode, parameterList);
                wp.Messages = agent.Messages;                          

                return new OperationResult.OK { ResponseResource = wp };
            }
            catch (Exception ex)
            {
                return new OperationResult.InternalServerError { ResponseResource = "Parameter Service Error: " + ex.Message.ToString() };
            }
            finally
            {
                agent = null;

            }//end try
        }//end Get
    }//end class
}//end namespace
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
    public class ParameterGroupHandler
    {
        [HttpOperationAttribute(HttpMethod.GET)]
        public OperationResult Get(String regioncode)
        {
            SSServiceAgent agent = null;
            try
            {
                agent = new SSServiceAgent();

                return new OperationResult.OK { ResponseResource = new ParameterGroups() { Messages = agent.Messages, GroupList = agent.GetRegionAvailableGroups(regioncode) } };
            }
            catch (Exception ex)
            {
                return new OperationResult.InternalServerError { ResponseResource = "Region Group Service Error: " + ex.Message.ToString() };
            }
            finally
            {
                agent = null;

            }//end try
        }//end Get
    
    }//end class
}//end namespace
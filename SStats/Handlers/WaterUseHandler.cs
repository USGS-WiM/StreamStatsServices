//------------------------------------------------------------------------------
//----- WaterUseHandler -----------------------------------------------------------
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
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

using WiM.Utilities.Storage;

using SStats.Utilities;
using SStats.Utilities.ServiceAgent;
using SStats.Resources;

namespace SStats.Handlers
{
    public class WaterUseHandler
    {
        [HttpOperationAttribute(HttpMethod.GET)]
        public OperationResult Get()
        {
            List<string> availableRegions = null; 
            try
            {
                //return implemented regions
                availableRegions = JsonConvert.DeserializeObject<JObject>(ConfigurationManager.AppSettings["WaterUseRegions"]).Properties().Select(p => 
                    p.Name).ToList(); 

                return new OperationResult.OK { ResponseResource = availableRegions };
            }
            catch (Exception ex)
            {
                return new OperationResult.InternalServerError { ResponseResource = "Capabilities Service Error: " + ex.Message.ToString() };
            }
            finally
            {
                //agent = null;

            }//end try
        }//end Get
        [HttpOperationAttribute(HttpMethod.GET, ForUriName = "GetWateruseConfigSettings")]
        public OperationResult GetWateruseConfigSettings(String regioncode)
        {
            try
            {
                if (string.IsNullOrEmpty(regioncode)) return new OperationResult.BadRequest { ResponseResource = "region code or workspaceID cannot be empty" };
                
                JToken wuCode = JsonConvert.DeserializeObject<JToken>(ConfigurationManager.AppSettings["WaterUseRegions"])[regioncode.ToUpper()];
                if (wuCode == null) return new OperationResult.BadRequest { ResponseResource = "invalid region code" };
                wuCode["name"] = regioncode;

                return new OperationResult.OK { ResponseResource = wuCode.ToObject(typeof(Object)) };
            }
            catch (Exception ex)
            {
                return new OperationResult.InternalServerError { ResponseResource = "Capabilities Service Error: " + ex.Message.ToString() };
            }
            finally
            {
                //agent = null;

            }//end try
        }//end Get
        [HttpOperationAttribute(HttpMethod.GET)]
        public OperationResult Get(String regioncode, string workspaceID, Int32 startyear, [Optional] Int32 endyear)
        {
            ServiceAgent agent = null;
            try
            {
                if (string.IsNullOrEmpty(regioncode) || string.IsNullOrEmpty(workspaceID)) return new OperationResult.BadRequest { ResponseResource = "region code or workspaceID cannot be empty" };
                if (startyear < 1900) return new OperationResult.BadRequest { ResponseResource = "invalid start year" };

                string wuCode = JsonConvert.DeserializeObject<JToken>(ConfigurationManager.AppSettings["WaterUseRegions"])[regioncode.ToUpper()].ToString();
                if (string.IsNullOrEmpty(wuCode)) throw new Exception("invalid region code");

                agent = new ServiceAgent(ConfigurationManager.AppSettings["WaterUseServer"]);               

                return new OperationResult.OK { ResponseResource = agent.GetWaterUse(wuCode, workspaceID, startyear, endyear) };
            }
            catch (Exception ex)
            {
                return new OperationResult.InternalServerError { ResponseResource = "Capabilities Service Error: " + ex.Message.ToString() };
            }
            finally
            {
                //agent = null;

            }//end try
        }//end Get

    }
}
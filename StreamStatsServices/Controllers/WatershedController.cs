//------------------------------------------------------------------------------
//----- HttpController ---------------------------------------------------------
//------------------------------------------------------------------------------

//-------1---------2---------3---------4---------5---------6---------7---------8
//       01234567890123456789012345678901234567890123456789012345678901234567890
//-------+---------+---------+---------+---------+---------+---------+---------+

// copyright:   2017 WiM - USGS

//    authors:  Jeremy K. Newson USGS Web Informatics and Mapping
//              
//  
//   purpose:   Handles resources through the HTTP uniform interface.
//
//discussion:   Controllers are objects which handle all interaction with resources. 
//              
//
// 

using Microsoft.AspNetCore.Mvc;
using System;
using StreamStatsAgent;
using System.Threading.Tasks;
using System.Collections.Generic;
using WiM.Resources;
using StreamStatsAgent.Resources;

namespace StreamStatsServices.Controllers
{
    [Route("[controller]")]
    public class WatershedController : WiM.Services.Controllers.ControllerBase
    {
        public IStreamStatsAgent agent { get; set; }
        public WatershedController(IStreamStatsAgent agent ) : base()
        {
            this.agent = agent;
        }
        #region METHODS
        [HttpGet()]
        //watershed?rcode={}&xlocation={}&ylocation={}&crs={}&includeparameters={}&includeflowtypes={}&includefeatures={}&simplify={}
        //watershed?rcode={}&workspaceID={}&crs={}&includeparameters={}&includeflowtypes={}&includefeatures={}&simplify={}
        public async Task<IActionResult> Get([FromQuery]string rcode, [FromQuery]int crs=4326, [FromQuery]double? xlocation=null, [FromQuery] double? ylocation=null, [FromQuery] string workspaceID = "",[FromQuery] bool simplify = true, [FromQuery] bool surfacecontributiononly = false)
        {
            Watershed result = null;
            stormwaterOption scFlag = stormwaterOption.e_default;
            try
            {
                if (!(xlocation.HasValue & ylocation.HasValue) & string.IsNullOrEmpty(workspaceID)) return new BadRequestObjectResult("X,Y locations or WorkspaceID is required.");
                if (String.IsNullOrEmpty(rcode)) return new BadRequestObjectResult("Region identifier is required");
                //delineation
                if (surfacecontributiononly) scFlag = stormwaterOption.e_surfacecontributiononly;

                result = agent.GetWatershed(xlocation.Value, ylocation.Value, crs, rcode, simplify, scFlag);
                sm(agent.Messages);
                return Ok(result);
            }
            catch (Exception ex)
            {
                return HandleException(ex);
            }
        }
        
        //watershed/edit?rcode={regioncode}&workspaceID={workspaceID}&crs={espg}&includeparameters={parameterList}&includeflowtypes={flowtypeList}&includefeatures={featureList}&simplify={simplificationOption}
        [HttpGet("/edit")]
        public async Task<IActionResult> edit(string rcode, string workspaceID, int crs)
        {
            //returns list of available Navigations
            try
            {
                var result = agent.GetWatershed(0, 0, 1, "", true);
                sm(agent.Messages);
                return Ok(result);
            }
            catch (Exception ex)
            {
                return HandleException(ex);
            }
        }
        #endregion
        #region HELPER METHODS
        private void sm(List<Message> messages)
        {
            if (messages.Count < 1) return;
            HttpContext.Items[WiM.Services.Middleware.X_MessagesExtensions.msgKey] = messages;
        }
        #endregion
    }
}

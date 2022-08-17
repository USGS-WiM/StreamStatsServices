//------------------------------------------------------------------------------
//----- ServiceAgent -------------------------------------------------------
//------------------------------------------------------------------------------

//-------1---------2---------3---------4---------5---------6---------7---------8
//       01234567890123456789012345678901234567890123456789012345678901234567890
//-------+---------+---------+---------+---------+---------+---------+---------+

// copyright:   2017 WiM - USGS

//    authors:  Jeremy K. Newson USGS Web Informatics and Mapping
//              
//  
//   purpose:   The service agent is responsible for initiating the service call, 
//              capturing the data that's returned and forwarding the data back to 
//              the requestor.
//
//discussion:   
//
// 

using System;
using System.Collections.Generic;
using WiM.Resources;
using Microsoft.AspNetCore.Hosting;
using System.IO;
using Microsoft.Extensions.Options;
using StreamStatsAgent.Resources;
using WiM.Utilities.ServiceAgent;
using Newtonsoft.Json;

namespace StreamStatsAgent
{
    public interface IStreamStatsAgent : IMessage
    {
        Watershed GetWatershed(double X, double Y, int espg, string regioncode, bool simplify, stormwaterOption stormwater=0);
        void WriteError(string file, string error);
    }

    public class StreamStatsAgent : ExternalProcessServiceAgentBase, IStreamStatsAgent
    {
        #region Properties
        private Dictionary<string, string> Resources { get; set; }
        public List<Message> Messages { get; set; }
        #endregion
        #region Constructor
        public StreamStatsAgent(IHostingEnvironment hostingEnvironment, IOptions<Settings> Settings) :
            base(Settings.Value.StreamStats.baseurl, Path.Combine(hostingEnvironment.ContentRootPath, "Assets", "Scripts"))
        {
            this.Messages = new List<Message>();
            Resources = Settings.Value.StreamStats.resources;
        }
        #endregion
        #region Methods
        public Watershed GetWatershed(double X, double Y, int espg, string regioncode, bool simplify, stormwaterOption stormwater = stormwaterOption.e_default) {
            Watershed result = null;
            List<string> args = new List<string>();
            try
            {
                args.Add("-rcode " + regioncode);
                args.Add(String.Format("-pourpoint [{0},{1}]", X, Y));
                args.Add("-pourpointwkid " + espg);
                args.Add("-stormwaterOption "+(int)stormwater);
                var body = string.Join(" ", args);

                result = Execute<Watershed>(getProcessRequest(getProcessName(processType.e_stormwaterDelineation), body));      

                return result;
            }
            catch (Exception ex)
            {
                WriteError("D:\\logs\\StreamStatsAgentError.log", "Error getting watershed " + ex.Message);
                sm("Error getting watershed " + ex.Message, MessageType.error);
                throw;
            }            
        }
        #endregion
        #region HELPER METHODS
        public void WriteError(string file, string error)
        {
            File.WriteAllText(file, error);
        }

        private void sm(string message, MessageType type = MessageType.info)
        {
            this.Messages.Add(new Message() { msg=message, type = type });
        }
        private String getProcessName(processType sType)
        {
            string uri = string.Empty;
            switch (sType)
            {
                case processType.e_delineation:
                    uri = Resources["Delineation"];
                    break;
                case processType.e_stormwaterDelineation:
                    uri = Resources["StormWaterDelineation"];
                    break;
                case processType.e_editwatershed:
                    uri = Resources["EditWatershed"];
                    break;
                case processType.e_parameters:
                    uri = Resources["Characteristics"];
                    break;
                case processType.e_shape:
                    uri = Resources["Shape"];
                    break;
                case processType.e_features:
                    uri = Resources["Features"];
                    break;
            }

            return uri;
        }//end getURL
        #endregion
        #region Enumerations
        public enum processType
        {
            e_delineation,
            e_stormwaterDelineation,
            e_parameters,
            e_flowstats,
            e_features,
            e_editwatershed,
            e_shape
        }
        
        #endregion
    }
    public enum stormwaterOption
    {
        e_default = 1,
        e_stormwater = 1,
        e_surfacecontributiononly = 2
    }

}
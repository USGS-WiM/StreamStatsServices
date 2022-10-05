using System;
using System.Collections.Generic;
using System.Linq;
using WiM.Utilities.ServiceAgent;
using NSSService.Resources;
using System.Configuration;
using WiM.Resources.Spatial;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using RestSharp;

namespace SStats.Utilities.ServiceAgent
{   

    public class PercentOverlayServiceAgent : ServiceAgentBase
    {
        public PercentOverlayServiceAgent() : base(ConfigurationManager.AppSettings["gisHostServer"])
        {
        }
        public List<PercentOverlay> getPercentOverlay(FeatureCollectionBase watershed)
        {
            List<PercentOverlay> resultList = new List<PercentOverlay>();
            try
            {
                if (watershed.GetType() == typeof(EsriFeatureRecordSet))
                    watershed = (FeatureCollection)(watershed as EsriFeatureRecordSet);


                var result = Execute(getRestRequest(ConfigurationManager.AppSettings["percentoverlay"], getBody(watershed))) as JArray;

                foreach (var item in result.ToObject<List<PercentOverlay>>())
                {
                    foreach (var code in item.code.Split(','))
                    {
                        resultList.Add(new PercentOverlay() {
                             name = item.name,
                            code = code,
                            areasqmeter = item.areasqmeter, maskareasqmeter = item.maskareasqmeter,
                            percent = item.percent
                            
                        });
                    }//next code
                }//next item


                return resultList;
            }
            catch (Exception ex)
            {
                throw;
            }

        }

        private string getBody(FeatureCollectionBase feature)
        {
            List<string> body = new List<string>();
            try
            {
                body.Add("geometry=" + JsonConvert.SerializeObject(feature));
                body.Add("f=pjson");

                return string.Join("&", body);
            }
            catch (Exception)
            {
                throw;
            }
        }

    }
}
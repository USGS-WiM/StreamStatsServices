//------------------------------------------------------------------------------
//----- ServiceAgent -------------------------------------------------------
//------------------------------------------------------------------------------

//-------1---------2---------3---------4---------5---------6---------7---------8
//       01234567890123456789012345678901234567890123456789012345678901234567890
//-------+---------+---------+---------+---------+---------+---------+---------+

// copyright:   2012 WiM - USGS

//    authors:  Jeremy K. Newson USGS Wisconsin Internet Mapping
//              
//  
//   purpose:   The service agent is responsible for initiating the service call, 
//              capturing the data that's returned and forwarding the data back to 
//              the requestor.
//
//discussion:   delegated hunting and gathering responsibilities.   
//
//    

using System;
using System.Configuration;
using System.Collections.Generic;
using System.Collections;
using System.Linq;
using System.Net;
using System.Xml.Serialization;
using System.Xml;
using System.IO;
using System.Threading;

using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

using WiM.Utilities.ServiceAgent;
using WiM.Resources;
using WiM.Resources.Spatial;
using SStats.Resources;
using NSSService.Resources;
using CoordinatedReachServices.Resources;

using SSDB;
using RestSharp;

namespace SStats.Utilities.ServiceAgent
{
    public class NSSServiceAgent : ServiceAgentBase
    {
        #region Properties
        #endregion

        #region Constructors
        public NSSServiceAgent():base(ConfigurationManager.AppSettings["NSSHostServer"])
        {
        }
        public NSSServiceAgent(string baseurl)
            : base(baseurl)
        {
        }
        #endregion

        #region Methods 
        public List<StatisticGroupType> GetAvailableStatistics(string region) {
            try
            {
                RestSharp.RestRequest request = new RestSharp.RestRequest(String.Format(getURI(serviceType.e_statisticgroups), region));
                List<StatisticGroupType> result = Execute<List<StatisticGroupType>>(request).Data;

                return result;
            }
            catch (Exception ex)
            {
                throw new Exception("Failed to get statistic groups " + ex.Message);
            }

        }
        public List<Scenario> GetStatistics(String regionCode, string workspaceID, string statisticGroupCodes)
        {
            SSServiceAgent sssa = null;

            List<Scenario> scenarios = null;
            List<string> statgroupList;
            List<CoordinatedReach> creach = null;
            Dictionary<string, double?> parameterList = null;
            List<Scenario> scensarioResult = null;
            try
            {
                statgroupList = parse(statisticGroupCodes);
                sssa = new SSServiceAgent(workspaceID);

                //0 get watershed geojson
                List<FeatureWrapper> features = sssa.GetFeatures("globalwatershed,globalwatershedpoint", 4326, 2);              
               
                if (statgroupList.Any(item=>item.Equals("PFS", StringComparison.OrdinalIgnoreCase)|| item.Equals("2", StringComparison.OrdinalIgnoreCase)))
                {
                    creach = getCoordinatedReachs(regionCode, features.FirstOrDefault(i => i.name.Equals("globalwatershedpoint", StringComparison.OrdinalIgnoreCase)).feature);
                   if (creach.Count>0) statgroupList.RemoveAll(n => n.Equals("PFS", StringComparison.OrdinalIgnoreCase));
                }//end if

                if(statgroupList.Count>0)
                {
                    scenarios = getScenarios(regionCode, features
                        .FirstOrDefault(i => i.name.Equals("globalwatershed", StringComparison.OrdinalIgnoreCase)).feature, statgroupList);
                }//end if
               
                //3 get basincharacteristics
                var charactersitcsList = scenarios.SelectMany(s => s.RegressionRegions.SelectMany(r => r.Parameters.Select(p => p.Code))).ToList();
                if (creach.Count > 0) charactersitcsList.Add("DRNAREA");
                charactersitcsList=charactersitcsList.Distinct().ToList();

                //Check if attributes exist before requesting again
                var Attributes = features.FirstOrDefault(i => i.name.Equals("globalwatershed", StringComparison.OrdinalIgnoreCase)).feature
                    .features.SelectMany(f => 
                    ((JObject)f.attributes).ToObject<Dictionary<string, object>>()).GroupBy(p => p.Key)
                    .ToDictionary(g => g.Key, g => g.Last().Value);

                parameterList = charactersitcsList.Where(c =>
                    Attributes.ContainsKey(c.ToUpper()) && !Convert.IsDBNull(Attributes[c.ToUpper()]) && Convert.ToDouble(Attributes[c.ToUpper()]) > 0)
                    .ToDictionary(key => key, val => (double?)Convert.ToDouble(Attributes[val]));

                var requestList = charactersitcsList.Where(c => !parameterList.ContainsKey(c)).ToArray();
                if (requestList.Count() > 0)
                {
                    var pList = sssa.GetParameters(regionCode, String.Join(";", requestList));
                    pList.ForEach(p => parameterList[p.code] = p.value);
                }//endif               
                //4 get execute scenarios
                if(scenarios != null)
                    scensarioResult = getScenariosResults(regionCode, scenarios, parameterList, statgroupList);
                if (creach.Count > 0)
                {
                    var cScenario = getCoordinatedReachResult(regionCode, creach, parameterList);
                    if (scensarioResult != null) scensarioResult.Add(cScenario);
                    else scensarioResult = new List<Scenario>() { cScenario };
                }

                return scensarioResult;
            }
            catch (Exception ex)
            {
                throw;
            }
        }
       #endregion
        
        #region Helper Methods
        private List<CoordinatedReach> getCoordinatedReachs(string rcode, FeatureCollectionBase point)
        {
            try
            {
                if (!rcode.Equals("in", StringComparison.OrdinalIgnoreCase)) return null;
                
                    var crA = new CoordinatedReachAgent();
                    return crA.GetCoordinatedReach(rcode, point);              
            }
            catch (Exception)
            {
                return new List<CoordinatedReach>();
            }
        }
        private Scenario getCoordinatedReachResult(string rcode, List<CoordinatedReach> coordinatedReach, Dictionary<string, double?> paramList)
        {
            
            try
            {
                if (!rcode.Equals("in", StringComparison.OrdinalIgnoreCase)) return null;
               
                var crA = new CoordinatedReachAgent();
                return crA.GetScenario(rcode, coordinatedReach,paramList);               
            }
            catch (Exception)
            {

                return null;
            }
        }
        private List<Scenario> getScenarios(string rcode, FeatureCollectionBase wshed, List<string>statgroups)
        {
            List<PercentOverlay> regions = null;
            PercentOverlayServiceAgent poSA = null;
            try
            {

                poSA = new PercentOverlayServiceAgent();
                //1 get percentOverlay for workspace
                regions = poSA.getPercentOverlay(wshed);
                Dictionary<string, double> regressionregions = regions.GroupBy(p => p.code, StringComparer.OrdinalIgnoreCase)
                                                                .ToDictionary(g => g.Key, g => g.First().percent, StringComparer.OrdinalIgnoreCase);
                string regressionRegionString = String.Join(",", regressionregions.Keys.ToArray());
                //2 get scenarios
                string scenarioURI = String.Format(getURI(serviceType.e_scenarios), rcode, regressionRegionString, String.Join(",", statgroups), "");

                var scenarios = Execute<List<Scenario>>(new RestRequest(scenarioURI, Method.GET)).Data;

                scenarios.ForEach(s => s.RegressionRegions.ForEach(rr =>
                    rr.PercentWeight = (double?)regressionregions[rr.Code]??null));

                return scenarios;

            }
            catch (Exception)
            {

                throw;
            }
        }
        private List<Scenario> getScenariosResults(string rcode, List<Scenario> scenarios, Dictionary<string, double?> paramList, List<string> statgroups)
        {
            try
            {
                scenarios.ForEach(s => s.RegressionRegions.ForEach(rr =>
                {
                    rr.Parameters.ForEach(p =>
                    {
                        if (!paramList.ContainsKey(p.Code) || !paramList[p.Code].HasValue)
                            throw new NullReferenceException(p.Code + " value is null");
                        p.Value = paramList[p.Code].Value;
                    });
                }));
                string regressionRegionString = String.Join(",", scenarios.SelectMany(r => r.RegressionRegions.Select(rr => rr.Code)));
                string scenarioURI = String.Format(getURI(serviceType.e_scenarios), rcode, regressionRegionString, String.Join(",", statgroups), "/estimate");
                RestRequest request = new RestRequest(scenarioURI, Method.POST);
                request.RequestFormat = DataFormat.Json;
                request.AddBody(scenarios);
                return Execute<List<Scenario>>(request).Data;
            }
            catch (Exception ex)
            {

                throw;
            }

        }
        private String getURI(serviceType sType)
        {
            string uri = string.Empty;
            switch (sType)
            {
                case serviceType.e_statisticgroups:
                    uri = ConfigurationManager.AppSettings["statisticGroup"];
                    break;
                case serviceType.e_scenarios:
                    uri = ConfigurationManager.AppSettings["scenarios"];
                    break;
                case serviceType.e_percentOverlay:
                    uri = ConfigurationManager.AppSettings["percentOverlay"];
                    break;
            }

            return uri;
        }//end getURL
        private Boolean isDynamicError(dynamic obj, out string msg)
        {
            msg = string.Empty;
            try 
	        {
                var error = obj.error;
                if (error == null) throw new Exception();
                msg = error.message;
                return true;
	        }
	        catch (Exception ex)
	        {

                return false;
	        }

        }
        private List<string> parse(string items)
        {
            char[] delimiterChars = { ';', ',' };
            return items.ToLower().Split(delimiterChars, StringSplitOptions.RemoveEmptyEntries).ToList();
        }
        
        #endregion

        #region Enumerations
        public enum serviceType
        {
            e_statisticgroups,
            e_percentOverlay,
            e_scenarios

        }
        #endregion
    }//end sssServiceAgent       
}//end namespace

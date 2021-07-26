//------------------------------------------------------------------------------
//----- CoordinatedReachAgent----------------------------------------------------
//------------------------------------------------------------------------------

//-------1---------2---------3---------4---------5---------6---------7---------8
//       01234567890123456789012345678901234567890123456789012345678901234567890
//-------+---------+---------+---------+---------+---------+---------+---------+

// copyright:   2018 WiM - USGS

//    authors:  Jeremy K. Newson USGS Wisconsin Internet Mapping
//              
//  
//   purpose:   The service agent is responsible for initiating the service call, 
//              capturing the data that's returned and forwarding the data back to 
//              the requestor.
//
//discussion:   delegated hunting and gathering responsibilities.   
//              Created for IN service requests
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
using WiM.Resources.Spatial;
using NSSService.Resources;
using CoordinatedReachServices.Resources;

using SSDB;
using RestSharp;

namespace SStats.Utilities.ServiceAgent
{
    public class CoordinatedReachAgent : ServiceAgentBase
    {
        #region Properties
        #endregion

        #region Constructors
        public CoordinatedReachAgent() :this(ConfigurationManager.AppSettings["gisHostServer"])
        {}
        public CoordinatedReachAgent(string baseurl)
            : base(baseurl)
        {
        }
        #endregion

        #region Methods 
        public List<CoordinatedReach> GetCoordinatedReach(string regionCode, FeatureCollectionBase point)
        {
            //39.49343, -86.38945
            CoordinatedReach cReach = null;
            String fieldprecursor = "eqWithStrID.";
            List<string> keyAttributes = new List<string>() { "BASIN_NAME", "DVA_EQ_ID" };
            string outFields = "eqWithStrID.BASIN_NAME,eqWithStrID.DVA_EQ_ID,eqWithStrID.a10,eqWithStrID.b10,eqWithStrID.a25,eqWithStrID.b25,eqWithStrID.a50,eqWithStrID.b50,eqWithStrID.a100,eqWithStrID.b100,eqWithStrID.a500,eqWithStrID.b500";
            try
            {
                //check if Coordinated reach                
                EsriPoint pnt = point.features[0].geometry as EsriPoint;
                //testpoints
                //x =-86.389508769323712
                //y = 39.493453373938848
                var extent = getCircleExtent(pnt, 70);
                //result => -86.38899710090638,39.48629491402307,-86.38989541618346,39.50055969390581
                string coordReachURI = String.Format(getURI(serviceType.e_coordinatedReach), regionCode.ToLower(), extent.West, extent.South, extent.East, extent.North, 4326, outFields);
                 var response = Execute(new RestRequest(coordReachURI, Method.GET)) as JToken;
                var attributes = response.SelectTokens("$.features[*].attributes");

                if (attributes == null) return null;
                var ListReach = new List<CoordinatedReach>();
                foreach (var item in attributes)
                {

                    cReach = new CoordinatedReach();
                    cReach.Name = item.Value<String>(fieldprecursor + keyAttributes[0]);
                    cReach.ID = item.Value<String>(fieldprecursor + keyAttributes[1]);

                    var pkgroupings = item.Where(i => !keyAttributes.Select(att => fieldprecursor + att)
                    .Contains(((JProperty)(i)).Name)).Select(i => i as JProperty).GroupBy(i => i.Name.Substring(fieldprecursor.Length + 1));
                    foreach (var pkcode in pkgroupings)
                    {
                        var code = fieldprecursor + "{0}" + pkcode.Key;
                        var valA = pkcode.FirstOrDefault(i => i.Name.Equals(String.Format(code, "a"), StringComparison.OrdinalIgnoreCase)).Value.Value<double?>();
                        var valB = pkcode.FirstOrDefault(i => i.Name.Equals(String.Format(code, "b"), StringComparison.OrdinalIgnoreCase)).Value.Value<double?>();

                        //ensure both a&b have values
                        if (!valA.HasValue && !valB.HasValue) continue;

                        cReach.FlowCoefficient.Add(pkcode.Key,
                            new CoordReachCoeff()
                            {
                                CoefficientA = valA.Value,
                                CoefficientB = valB.Value
                            });
                    }//next
                    ListReach.Add(cReach);
                }               
                return ListReach;
            }
            catch (Exception ex)
            {
                return new List<CoordinatedReach>();
            }
        }
        public Scenario GetScenario(string rcode, List<CoordinatedReach> coordinatedReach, Dictionary<string, double?> paramList)
        {
            Scenario result = null;
            try
            {
                result = new Scenario();
                
                result.StatisticGroupName = "Peak-Flow Statistics";
                result.StatisticGroupID = 2;
                result.Links = new List<dynamic>() { new { Href = "http://www.in.gov/dnr/water/4898.htm", method = "GET", rel = "citations" } };
                result.RegressionRegions = coordinatedReach.Select(cr=>
                    new RegionEquation()
                    {
                         Code = cr.ID,
                         Name ="Coordinated Reach: "+cr.Name,
                         Parameters = getParameters(cr.FlowCoefficient,paramList),
                         Results=getResults(cr.FlowCoefficient,paramList)
                    }
                ).ToList();
                return result;
            }
            catch (Exception)
            {
                return null;
            }
        }
        #endregion

        #region Helper Methods
        private String getURI(serviceType sType)
        {
            string uri = string.Empty;
            switch (sType)
            {
                case serviceType.e_coordinatedReach:
                    uri = ConfigurationManager.AppSettings["coordinatedReachQueryServices"];
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
        private List<NSSService.Resources.Parameter> getParameters(Dictionary<string,CoordReachCoeff> FlowCoefficient, Dictionary<string, double?> paramList)
        {
            List<NSSService.Resources.Parameter> result = new List<NSSService.Resources.Parameter>();
            try
            {
                //drnarea
                result.Add(new NSSService.Resources.Parameter()
                {
                    Code= "DRNAREA",
                    Description = "Area that drains to a point on a stream",
                    Name = "Drainage Area",
                    Value = paramList["DRNAREA"].Value,
                    UnitType = new {Abbr="mi^2", Unit="square miles"}                   
                });

                foreach (var key in FlowCoefficient)
                {
                    result.Add(new NSSService.Resources.Parameter()
                    {
                        Code = "PK" + key.Key + "_CoeffA",
                        Value= Math.Round(key.Value.CoefficientA,3),
                        Name= "PK" + key.Key + " CoefficientA",
                        UnitType= new { Abbr= "dim", Unit= "dimensionless" }
                    });

                    result.Add(new NSSService.Resources.Parameter()
                    {
                        Code = "PK"+key.Key + "_CoeffB",
                        Value = Math.Round(key.Value.CoefficientB,3),
                        Name = "PK" + key.Key + " CoefficientB",
                        UnitType = new { Abbr = "dim", Unit = "dimensionless" }
                    });
                }//next key

                return result;
            }
            catch (Exception)
            {
                throw;
            }
        }
        private List<RegressionResult> getResults(Dictionary<string, CoordReachCoeff> FlowCoefficient, Dictionary<string, double?> paramList)
        {
            List<RegressionResult> result = new List<RegressionResult>();
            try
            {
                foreach (var item in FlowCoefficient)
                {
                    result.Add(new RegressionResult()
                    {
                        code = "PK"+item.Key,
                        Description = string.Format("Maximum instantaneous flow that occurs on average once in {0} years",item.Key),
                        Name = string.Format("{0} year Peak Flood",item.Key),
                        Equation = "CoefficientA*DRNAREA^CoefficientB",
                        UnitType = new { Abbr = "mi^2", Unit = "square miles" },
                        Value= item.Value.CoefficientA*Math.Pow(paramList["DRNAREA"].Value,item.Value.CoefficientB)
                    });
                }//next item
                return result;
            }
            catch (Exception)
            {
                throw;
            }
        }

        private extent getCircleExtent(EsriPoint pnt, double radiusMeter)
        {
            //https://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
            //Quick and dirty estimate

            //Earths radius, sphere
            var R = 6378137;
            var dLat = radiusMeter / R;
            var dLon = radiusMeter / (R * Math.Cos(Math.PI * pnt.y / 180));


            return new extent()
            {
                North = pnt.y + dLat * 180 / Math.PI,
                South = pnt.y - dLat * 180 / Math.PI,
                West = pnt.x - dLon * 180 / Math.PI,
                East = pnt.x + dLon * 180 / Math.PI

            };
        }
        #endregion

        #region Enumerations
        public enum serviceType
        {
            e_coordinatedReach
        }
        #endregion
    }//end sssServiceAgent       
}//end namespace

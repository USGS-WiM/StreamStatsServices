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

using SSDB;

namespace SStats.Utilities.ServiceAgent
{
    public class ServiceAgent : ServiceAgentBase
    {
        #region Properties
        private IDictionary<ResultType, FeatureCollectionBase> _delineationResultList = new Dictionary<ResultType, FeatureCollectionBase>();
        public IDictionary<ResultType, FeatureCollectionBase> DelineationResultList 
        {
            get { return _delineationResultList ;}
        }

        //private List<Parameter> BasinCharacteristicList;
        public string WorkspaceString { get; set; }
        public bool HasGeometry { get; private set; }
        #endregion

        #region Constructors
        public ServiceAgent():base(ConfigurationManager.AppSettings["SSHostServer"])
        {
            HasGeometry = false;
        }
        #endregion
       
        #region Methods
        public void GetDelineation(double x, double y, int wkid)
        {
            JObject result = null;
            String state = string.Empty;
            string msg;

            try
            {
                state = this.GetStudyCode(x, y, wkid);
                
                result = Execute( getRestRequest(getURI(serviceType.e_delineation), getBody(state, x,y,wkid))) as JObject;
                
                if (isDynamicError(result, out msg)) throw new Exception("Delineation Error: " +msg);
                
                HasGeometry = parseSSGWDelineationResult(result);

            }
            catch (Exception ex)
            {
                throw new Exception(ex.Message);
            }
        }//end PostFeatures
        public string GetStudyCode(double x, double y, int wkid){
           return getStudyCodeAbbr(Execute(new RestSharp.RestRequest(String.Format(getURI(serviceType.e_state), x, y, wkid, "st_abbr"))));
        }
        public List<Parameter> GetParameters(string state ,string bCharList)
        {
            try
            {
                //get list
                 List<Parameter> parameters = GetStateAvailableParameters(state);

                // SS returns a link to the basinChar. We want to get the item and pass it back.
                 string url = getCharacteristicXMLURL(Execute(getRestRequest(getURI(serviceType.e_characteristics), getBody(state, parameters))));

                //open and deserialize result
                return deserializeBasinCharacteristics(url, parameters);
            }
            catch (Exception ex)
            {
                throw;
            }
        }
        public List<Parameter> GetStateAvailableParameters(string state)
        {
            postgresqldbOps db = null;
            SSXMLAgent xml = null;
            List<Parameter> dbParameterList;
            List<Parameter> regionParameterList;
            try
            {
                db = new postgresqldbOps(ConfigurationManager.AppSettings["SSDBConnectionString"]);
                xml = new SSXMLAgent(state);

                //returns all code units and description
                dbParameterList = db.GetParameterList(); 
                //returns name, code for selected region
                regionParameterList = xml.GetRegionParameters();

                foreach (Parameter param in regionParameterList)
                {
                    Parameter selectedParam = dbParameterList.FirstOrDefault(p=>string.Equals(p.code, param.code, StringComparison.OrdinalIgnoreCase));
                    if (selectedParam == null) continue;
                    param.unit = selectedParam.unit;
                    param.description = selectedParam.description;
                }//next param

                return regionParameterList;
            }
            catch (Exception ex)
            {
                throw;
            }
            finally
            {
                if(db != null) db.Dispose();
            }
        }//end Get
        #endregion
        #region Delineation Helper Methods
        private string getBody(string state, double X, double Y, int wkid)
        {
            List<string> body = new List<string>();
            try
            {
                body.Add("STABBR=" + state);
                body.Add("f=" + "pjson");
                body.Add("env:outSR=" + wkid);
                body.Add("env:processSR=" + wkid);
                var esriFeatureColl = new EsriFeatureRecordSet(new EsriFeature(null, X, Y), wkid);
                body.Add("PourPoint=" + JsonConvert.SerializeObject(esriFeatureColl));


                return string.Join("&", body);
            }
            catch (Exception)
            {
                throw;
            }
        }//end getParameterList
        private string getStudyCodeAbbr(dynamic obj)
        {
            //.features[0].attributes.st_abbr.Value
            string msg = string.Empty;
            try
            {
                if (isDynamicError(obj, out msg)) throw new Exception(msg);

                return obj.features[0].attributes.st_abbr.Value;

            }
            catch (Exception ex)
            {

                throw new Exception("default error: requesting state abbr");
            }
        }
        private Boolean parseSSGWDelineationResult(JObject SSdelineationResult)
        {
            try
            {
                JToken results = SSdelineationResult["results"][0];
                this.WorkspaceString = results.Value<string>("value");
                return this.parseSSGBDelineationResult(SSdelineationResult);
            }
            catch (Exception)
            {
                return false;
            }//end try
        }//end parseDelineatinResult
        private Boolean parseSSGBDelineationResult(JObject SSdelineationResult)
        {
            List<FeatureBase> features = null;
            int wkid = -9;
            try
            {
                FeatureBase feature = null;
                features = SSdelineationResult["results"].Where(f => isFeature(f, out feature, out wkid)).Select(f => feature).ToList<FeatureBase>();

                if (wkid < 1) wkid = 102100;
                //set to featureCollection

                this.DelineationResultList.Add(ResultType.e_basin, new EsriFeatureRecordSet(features, wkid, "esriGeometryPolygon"));
                this.DelineationResultList.Add(ResultType.e_pourpoint, new EsriFeatureRecordSet(features, wkid, "esriGeometryPoint"));
                return true;
            }
            catch (Exception)
            {
                return false;
            }//end try
        }//end parseDelineatinResult
        private Boolean isFeature(JToken jobj, out FeatureBase Feature, out int wkid)
        {
            JArray obj = null;
            string gtype;

            try
            {
                obj = (JArray)jobj.SelectToken("value.features");
                gtype = (string)jobj.SelectToken("value.geometryType");
                wkid = (int)jobj.SelectToken("value.spatialReference.wkid");
                Feature = new EsriFeature(obj, gtype);
                return true;

            }
            catch (Exception ex)
            {

                Feature = null;
                wkid = 0;
                return false;
            }
        }
        #endregion

        #region Parameter Helper Methods
        private string getBody(string state, List<Parameter> bCharList)
        {
            List<string> body = new List<string>();
            try
            {
                body.Add("STABBR=" + state);
                body.Add("f=" + "pjson");
                body.Add("BCparams=" + string.Join(";",bCharList.Select(p => p.code).ToList()));
                body.Add("WorkspaceName=" + this.WorkspaceString);

                return string.Join("&", body);
            }
            catch (Exception)
            {
                throw;
            }
        }//end getParameterList 
        private string getStateParameters(dynamic obj)
        {
            //.features[0].attributes.st_abbr.Value
            string msg = string.Empty;
            try
            {
                if (isDynamicError(obj, out msg)) throw new Exception(msg);

                return obj.results[0].value.Value;

            }
            catch (Exception ex)
            {

                throw new Exception("default error: requesting state parameters");
            }
        }

        private string getCharacteristicXMLURL(dynamic obj)
        {
            //.results[0].value.url.Value
            string msg = string.Empty;
            try
            {
                if (isDynamicError(obj, out msg)) throw new Exception(msg);

                return obj.results[0].value.url.Value;

            }
            catch (Exception ex)
            {
                if (string.IsNullOrEmpty(ex.Message)) msg = "default error: requesting state abbr";
                throw new Exception(msg);
            }
        }
        private List<Parameter> deserializeBasinCharacteristics(string uri, List<Parameter> paramList)
        {
            Parameter selectedParam;
            //move this to xmlOp
            XmlReader xmlReader = XmlReader.Create(uri);
            while (xmlReader.Read())
            {
                if ((xmlReader.NodeType == XmlNodeType.Element) && (xmlReader.Name == "PARAMETER"))
                {
                    if (!xmlReader.HasAttributes) continue;
                    if (string.IsNullOrEmpty(xmlReader.GetAttribute("name")) || string.IsNullOrEmpty(xmlReader.GetAttribute("value"))) continue;

                    selectedParam = paramList.FirstOrDefault(p => string.Equals(p.code, xmlReader.GetAttribute("name"), StringComparison.OrdinalIgnoreCase));
                    selectedParam.value = Convert.ToDouble(xmlReader.GetAttribute("value"));
                   
                }//end if
            }//next
            return paramList;
        }
        
        #endregion

        #region Helper Methods
        private String getURI(serviceType sType)
        {
            string uri = string.Empty;
            switch (sType)
            {
                case serviceType.e_delineation:
                    //"GlobalDelineation/GPServer/GlobalDelineation/execute";
                    //getGW4/GPServer/getGW4/execute
                    uri = ConfigurationManager.AppSettings["SSDelineationService"];
                    break;
                case serviceType.e_characteristics:
                    //"BasinChars/GPServer/BasinChars/execute";
                    uri = ConfigurationManager.AppSettings["SSBasinCharService"];
                    break;
                case serviceType.e_characteristicsList:
                    //"getParamFields/GPServer/getParamFields/execute?Study_Area_Abbr={0}&f=pjson";
                    uri = ConfigurationManager.AppSettings["Parameters"];
                    break;
                case serviceType.e_state:
                    //"ss_states_dev/MapServer/3/query?geometry={{x:{0},y:{1}}}&geometryType=esriGeometryPoint&inSR={2}&spatialRel=esriSpatialRelIntersects&outFields={3}&returnGeometry=false&f=pjson";
                    uri = ConfigurationManager.AppSettings["SSStateService"];
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
        #endregion 
      
        #region Enumerations
        public enum serviceType
        {
            e_delineation,
            e_characteristics,
            e_characteristicsList,
            e_state
        }
        public enum ResultType { 
            e_basin,
            e_pourpoint
        }
        #endregion
    }//end sssServiceAgent       
}//end namespace

using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Configuration;
using System.IO;

using Newtonsoft;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using WiM.Utilities.ServiceAgent;
using WiM.Resources;
using WiM.Resources.Spatial;

using SStats.Resources;
using SSDB;

namespace SStats.Utilities.ServiceAgent
{

    public class SSServiceAgent : ExternalProcessServiceAgentBase, IMessage
    {
        
        #region Properties
        private IDictionary<string, FeatureWrapper> _featureResultList = new Dictionary<string, FeatureWrapper>(StringComparer.InvariantCultureIgnoreCase);

        public string WorkspaceString { get; set; }
        private List<string> _message = new List<string>();
        public List<string> Messages
        {
            get { return _message; }
        }
        public bool HasGeometry { get; private set; }
        #endregion

        #region Constructors
        public SSServiceAgent()
            : base(ConfigurationManager.AppSettings["EXEPath"], Path.Combine(new String[] { AppDomain.CurrentDomain.BaseDirectory, "Assets", "Scripts" }))
        {
            HasGeometry = false;
        }
        public SSServiceAgent(string workspaceID)
            : base(ConfigurationManager.AppSettings["EXEPath"], Path.Combine(new String[] { AppDomain.CurrentDomain.BaseDirectory, "Assets", "Scripts" }))
        {
            WorkspaceString = workspaceID;
            HasGeometry = false;
        }
        #endregion

        #region Methods

        public void GetDelineation(double x, double y, int espg, int simplificationOption, String basinCode)
        {
            JObject result = null;
            string msg;
            ServiceAgent sa = new ServiceAgent();
            try
            {
                if (!validStudyCode(basinCode)) basinCode = sa.GetStudyCode(x, y, espg);

                result = Execute(getProcessRequest(getProcessName(processType.e_delineation), getBody(basinCode, x, y, espg, simplificationOption))) as JObject;

                if (isDynamicError(result, out msg)) throw new Exception("Delineation Error: " + msg);

                HasGeometry = parseSSGWDelineationResult(result, simplificationOption);
            }
            catch (Exception ex)
            {
                throw new Exception(ex.Message);
            }
        }
        public List<Parameter> GetParameters(string state, string pList)
        {
            JObject result = null;
            List<string> requestPCodes;
            
            try
            {
                requestPCodes = this.parse(pList);

                ///get list
                List<Parameter> parameters = GetRegionAvailableParameters(state);
                List<Parameter> selectedList = parameters.Where(p => requestPCodes.Contains(p.code)).ToList();

                if (selectedList != null && selectedList.Count > 0) parameters = selectedList;
                result = Execute(getProcessRequest(getProcessName(processType.e_parameters), getBody(state, parameters))) as JObject;

                //deserialize result
                return parseParameters(result, parameters);
            }
            catch (Exception ex)
            {
                throw;
            }
        }
        public List<Parameter> GetRegionAvailableParameters(string state, string group = "")
        {
            postgresqldbOps db = null;
            SSXMLAgent xml = null;
            List<Parameter> dbParameterList;
            List<Parameter> regionParameterList;
            List<string> groupCodes;
            try
            {
                db = new postgresqldbOps(ConfigurationManager.AppSettings["SSDBConnectionString"]);               
                //returns all code units and description
                dbParameterList = db.GetParameterList();
                groupCodes = db.GetGroupCodes(state, group);
                this.sm(db.Messages);


                //returns name, code for selected region
                xml = new SSXMLAgent(state);
                regionParameterList = xml.GetRegionParameters();
                this.sm(xml.Messages);

                if (groupCodes.Count > 0) { 
                    regionParameterList = regionParameterList.Where(a => groupCodes.Contains(a.code)).ToList();
                    sm("sync w/ group. Final Count:" + regionParameterList.Count);
                }              
                
                foreach (Parameter param in regionParameterList)
                {
                    Parameter selectedParam = dbParameterList.FirstOrDefault(p => string.Equals(p.code, param.code, StringComparison.OrdinalIgnoreCase));
                    if (selectedParam == null) { this.sm(param.code + " failed to return a description and unit from the database"); continue; }
                    param.unit = selectedParam.unit;
                    param.description = selectedParam.description;
                }//next param

                return regionParameterList;
            }
            catch (Exception ex)
            {
                throw ex;
            }
            finally
            {
                if (db != null) db.Dispose();
            }
        }//end Get
        public List<String> GetRegionAvailableGroups(string rcode)
        {
            postgresqldbOps db = null;
            List<string> groupCodes;
            try
            {
                db = new postgresqldbOps(ConfigurationManager.AppSettings["SSDBConnectionString"]);
                groupCodes = db.GetGroupCodes(rcode);
                this.sm(db.Messages);
                return groupCodes;
            }
            catch (Exception ex)
            {
                throw ex;
            }
            finally
            {
                if (db != null) db.Dispose();
            }
        }//end Get
        public string GetWorkspace(string workspace, Int32 type)
        {
            dynamic resultObj = Execute(getProcessRequest(getProcessName(processType.e_shape), String.Format("-workspaceID {0} -directory {1} -toType {2}", 
                                                                                                    workspace, ConfigurationManager.AppSettings["SSRepository"], type)));
            return resultObj.Workspace;
        }
        public List<string> GetStateFlowStatistics(string regionCode) {
            SSXMLAgent xmlagent = null;
            List<string> regionFlowStatsList;
            try
            {
                xmlagent = new SSXMLAgent(regionCode);
                regionFlowStatsList = xmlagent.GetRegionFlowStats();
                this.sm(xmlagent.Messages);

                return regionFlowStatsList;
            }
            catch (Exception ex)
            {
                throw ex;
            }
            finally
            {
                if (xmlagent != null) xmlagent.Dispose();
            }
        
        }
        public dynamic GetFlowStatistics(string state, string flowtypeList)
        {
            var result = Execute(getProcessRequest(getProcessName(processType.e_flowstats), getstatisticsBody(state, flowtypeList))) as JObject;

            return result;
        }

        public List<FeatureWrapper> GetFeatures(string features)
        {
            List<string> requestFcodes = new List<string>();
            List<FeatureWrapper> results;
            try
            {
                //check if features already exist in collection
                foreach (var item in parse(features))
                    if (!this._featureResultList.ContainsKey(item)) requestFcodes.Add(item);
                loadFeatures(string.Join(";", requestFcodes));

                if (string.IsNullOrEmpty(features)) results = this._featureResultList.Select(x => x.Value).ToList();
                else results = this._featureResultList.Where(x => parse(features).Contains(x.Key.ToUpper())).Select(x => x.Value).ToList();

                return results;

            }
            catch (Exception)
            {
                
                throw;
            }
           

        }
        #endregion

        #region Delineation Helper Methods
        private Boolean validStudyCode(string code) {
            List<string> exludedBasinIDs = null;
            char[] delimiterChars = { ',' };
            try
            {
                exludedBasinIDs = Array.ConvertAll(ConfigurationManager.AppSettings["exludedcodes"].Split(','), p => p.Trim().ToUpper()).ToList();
                if (exludedBasinIDs.Contains(code.ToUpper())) throw new Exception("exclution states");                
                
                return true;
            }
            catch (Exception e) {
                return false;
            }
        }
        private string getBody(string state, double X, double Y, int wkid, int simplificationOption)
        {
            List<string> body = new List<string>();
            try
            {
                body.Add("-stabbr " + state);
                body.Add("-processSR " + wkid);
                body.Add(String.Format("-pourpoint [{0},{1}]",X,Y));
                body.Add("-pourpointwkid " + wkid);
                body.Add("-directory " + ConfigurationManager.AppSettings["SSRepository"]);
                body.Add("-simplification " + simplificationOption);
                return string.Join(" ", body);
            }
            catch (Exception)
            {
                throw;
            }
        }//end getParameterList   
        private Boolean parseSSGWDelineationResult(JObject SSdelineationResult, Int32 simplificationOption)
        {
            List<FeatureBase> feature = null;
            int wkid = -9;
            string geomType = string.Empty;
            List<Field> fields = null;
            char[] delimiterChars = { '_'};
            try
            {
                JToken results = SSdelineationResult;
                this.WorkspaceString = results.Value<string>("Workspace");
                if (isFeature(results["Watershed"], out feature, out wkid, out geomType, out fields)) addToFeatureList((simplificationOption == 1) ? "delineatedbasin" : "delineatedbasin(simplified)", feature, wkid, geomType, fields);
                if (isFeature(results["PourPoint"], out feature, out wkid, out geomType, out fields)) addToFeatureList("pourpoint", feature, wkid, geomType, fields);
                this.sm(results.Value<string>("Message").
                    Split(delimiterChars, StringSplitOptions.RemoveEmptyEntries).Where(msg => msg.Contains("AHMSG:"))
                                                                                .Select(msg => msg.Substring((msg.IndexOf("Start Time:")) > 0 ? msg.IndexOf("Start Time:") : 0)).ToList());
                
                return true;
            }
            catch (Exception)
            {
                return false;
            }//end try
        }//end parseDelineatinResult 
       
        #endregion

        #region Parameter Helper Methods
        private string getBody(string state, List<Parameter> bCharList)
        {
            List<string> body = new List<string>();
            try
            {
                body.Add("-stabbr " + state);
                body.Add("-parameters " + string.Join(";", bCharList.Select(p => p.code).ToList()));
                body.Add("-workspaceID " + this.WorkspaceString);
                body.Add("-directory " + ConfigurationManager.AppSettings["SSRepository"]);


                return string.Join(" ", body);
            }
            catch (Exception)
            {
                throw;
            }
        }

        private List<Parameter> parseParameters(JToken jobj, List<Parameter> paramList)
        {
            JArray objArray = (JArray)jobj.SelectToken("Parameters");
            char[] delimiterChars = { '_' };

            this.sm(jobj.Value<string>("Message")
                .Split(delimiterChars, StringSplitOptions.RemoveEmptyEntries).Where(msg => msg.Contains("AHMSG:"))
                                                                             .Select(msg => msg.Substring((msg.IndexOf("Start Time:")) > 0 ? msg.IndexOf("Start Time:") : 0)).ToList());

            foreach (var p in objArray)
            {
                if ((p["code"] != null || p["value"] != null) && !String.IsNullOrEmpty(p.SelectToken("value").ToString()))
                    paramList.FirstOrDefault(sp => string.Equals(sp.code, p.SelectToken("code").ToString(), StringComparison.OrdinalIgnoreCase)).value = (Double)p.SelectToken("value");
            }//next p

            return paramList;
        }
        #endregion

        #region Statistics Helper Methods
        private string getstatisticsBody(string state,string flowtype )
        {
            List<string> body = new List<string>();
            try
            {
                body.Add("-stabbr " + state);
                if(!string.IsNullOrEmpty(flowtype))
                    // double quotes around flow type to account for spaces"
                    body.Add("-flowtype " + '"'+flowtype+'"');
                body.Add("-workspaceID " + this.WorkspaceString);
                body.Add("-directory " + ConfigurationManager.AppSettings["SSRepository"]);

                return string.Join(" ", body);
            }
            catch (Exception)
            {
                throw;
            }
        }//end getParameterList   
        #endregion

        #region Feature Helper Methods
        private string loadFeatures(string feature)
        {
            JObject result = null;
            List<string> requestFCodes;
            string msg;
            try
            {
                requestFCodes = getRequestedFeatures(feature);
                if(string.IsNullOrEmpty(this.WorkspaceString)) throw new Exception("workspace string must be set");
                
                result = Execute(getProcessRequest(getProcessName(processType.e_features), getBody(requestFCodes))) as JObject;
                if (isDynamicError(result, out msg)) throw new Exception("Feature Error: " + msg);
                return parseFeatures(result);

            }
            catch (Exception ex)
            {
                throw;
            }

        }
        private string getBody(List<string> fList)
        {
            List<string> body = new List<string>();
            try
            {   
                if(fList.Count > 0)
                    body.Add("-includefeatures "+ string.Join(";", fList.Select(f => f).ToList()));
                body.Add("-workspaceID " + this.WorkspaceString);
                body.Add("-directory " + ConfigurationManager.AppSettings["SSRepository"]);


                return string.Join(" ", body);
            }
            catch (Exception)
            {
                throw;
            }
        }
        private string parseFeatures(JObject jobj)
        {
            List<FeatureBase> features = null;
            int wkid = -9;
            string gtype = string.Empty;
            List<Field> fields = null;
            char[] delimiterChars = { '_' };
            List<string> featurelist = new List<string>();
            try
            {
                this.WorkspaceString = jobj.Value<string>("Workspace");
                this.sm(jobj.Value<string>("Message").
                    Split(delimiterChars, StringSplitOptions.RemoveEmptyEntries).Where(msg => msg.Contains("AHMSG:"))
                                                                                .Select(msg => msg.Substring((msg.IndexOf("Start Time:")) > 0 ? msg.IndexOf("Start Time:") : 0)).ToList());

                foreach (JToken item in (JArray)jobj.SelectToken("Features"))
                {
                    features = null;
                    var name = item.Value<string>("name");
                    switch (name)
                    {
                        case "globalwatershedpoint":
                            name = "pourpoint";
                            break;
                        case "globalwatershedraw":
                            continue;
                        case "globalwatershed":
                            name = "delineatedbasin";
                            break;
                        case "simplifiedgw":
                            name = "delineatedbasin(simplified)";
                            break;
                        default:
                            break;
                    }//end switch

                    featurelist.Add(name);


                    if (isFeature(item["feature"], out features, out wkid, out gtype, out fields)) {
                        addToFeatureList(name, features, wkid, gtype, fields);
                        HasGeometry = true;
                    }
                    else if (!this._featureResultList.ContainsKey(name))
                        _featureResultList.Add(name, new FeatureWrapper() { name = name });
                                        
                }//next item
            
                return string.Join(";", featurelist);
            }
            catch (Exception ex)
            {
                throw;
            }//end try
        }
        private List<string> getRequestedFeatures(string features){
            List<string> requestFCodes = new List<string>();

            try
            {
                foreach (string item in parse(features))
                {
                    switch (item.ToLower())
                    {
                        case "pourpoint":
                            requestFCodes.Add("globalwatershedpoint");
                            break;
                        case "delineatedbasin":
                            requestFCodes.Add("globalwatershed");
                            break;
                        case "delineatedbasin(simplified)":
                            requestFCodes.Add("simplifiedgw");
                            break;
                        default:
                            requestFCodes.Add(item);
                            break;
                    }//end switch
                }//next item

                return requestFCodes;
            }
            catch (Exception)
            {
                
                throw;
            }
        
        }
        #endregion

        #region Other Helper Methods
        private Boolean isFeature(JToken jobj, out List<FeatureBase> Feature, out int wkid, out string gtype, out List<Field> fields)
        {
            JArray obj = null;
            Feature = new List<FeatureBase>();

            try
            {                                
                fields = jobj["fields"] != null ? JsonConvert.DeserializeObject<List<Field>>(jobj.SelectToken("fields").ToString()) : null; 
                obj = (JArray)jobj.SelectToken("features");
                gtype = (string)jobj.SelectToken("geometryType");
                wkid = (int)jobj.SelectToken("spatialReference.wkid");
                foreach (JToken item in obj)
                    Feature.Add(new EsriFeature(item, gtype));

                return true;

            }
            catch (Exception ex)
            {

                Feature = null;
                wkid = 0;
                gtype = string.Empty;
                fields = null;
                return false;
            }
        }
        private void addToFeatureList(string name, List<FeatureBase> feature, int wkid, string geomType, List<Field> fields)
        {
            FeatureCollectionBase fColl = null;
            FeatureWrapper fStruct = null;
            try
            {
                if (this._featureResultList.ContainsKey(name)) return;

                fColl = new EsriFeatureRecordSet(feature, wkid, geomType, fields);
               
                fStruct = new FeatureWrapper() { name = name, feature = fColl };                

            }
            catch (Exception ex)
            {
                sm(name + " Add Feature error " + ex.Message);
            }
            finally {
                if (fColl !=null)
                    this._featureResultList.Add(name,fStruct);
            }
        }        
        private String getProcessName(processType sType)
        {
            string uri = string.Empty;
            switch (sType)
            {
                case processType.e_delineation:
                    uri = ConfigurationManager.AppSettings["Delineation"];
                    break;
                case processType.e_parameters:
                    uri = ConfigurationManager.AppSettings["Characteristics"];
                    break;
                case processType.e_shape:
                    uri = ConfigurationManager.AppSettings["Shape"];
                    break;
                case processType.e_flowstats:
                    uri = ConfigurationManager.AppSettings["Flowstats"];
                    break;
                case processType.e_features:
                    uri = ConfigurationManager.AppSettings["Features"];
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
            char[] delimiterChars = { ';', ',', ' ' };
            return items.ToUpper().Split(delimiterChars, StringSplitOptions.RemoveEmptyEntries).ToList();
        }
        private void sm(string msg) {
            this._message.Add(msg);
        }
        private void sm(List<string> msg)
        {
            this._message.AddRange(msg);
        }
        #endregion

        #region Enumerations
        public enum processType
        {
            e_delineation,
            e_parameters,
            e_shape,
            e_flowstats,
            e_features
        }

        #endregion
    }

}
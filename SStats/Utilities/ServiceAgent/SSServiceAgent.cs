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
using WiM.Utilities.Storage;
using WiM.Exceptions;

using SStats.Resources;
using SSDB;

namespace SStats.Utilities.ServiceAgent
{

    public class SSServiceAgent : ExternalProcessServiceAgentBase
    {
        
        #region Properties
        private IDictionary<string, FeatureWrapper> _featureResultList = new Dictionary<string, FeatureWrapper>(StringComparer.InvariantCultureIgnoreCase);

        public string WorkspaceString { get; private set; }
        private string RepositoryDirectory { get; set; }
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
            RepositoryDirectory = getRepositoryPath();
        }
        public SSServiceAgent(string workspaceID)
            : base(ConfigurationManager.AppSettings["EXEPath"], Path.Combine(new String[] { AppDomain.CurrentDomain.BaseDirectory, "Assets", "Scripts" }))
        {
            WorkspaceString = workspaceID;
            HasGeometry = false;
            RepositoryDirectory = getRepositoryPath();
            if (!isWorkspaceValid(RepositoryDirectory)) throw new BadRequestException(workspaceID + " Is not valid"); 
            
        }
        #endregion

        #region Methods
        public Boolean Delineate(double x, double y, int espg, String basinCode)
        {
            JObject result = null;
            string msg;
            ServiceAgent sa = new ServiceAgent();
            try
            {
                if (!validStudyCode(basinCode)) basinCode = sa.GetStudyCode(x, y, espg);

                result = Execute(getProcessRequest(getProcessName(processType.e_delineation), getBody(basinCode, x, y, espg))) as JObject;

                if (isDynamicError(result, out msg)) throw new Exception("Delineation Error: " + msg);

                parseResult(result);
                return true;
            }
            catch (Exception ex)
            {
                sm("Error delineating " + ex.Message);
                throw new Exception(ex.Message);
            }
        }
        public Boolean EditWatershed(WatershedEditDecisionList watershedEDL, int espg)
        {
            List<GeometryBase> appendFeatures = null;
            List<GeometryBase> removeFeatures = null;
            string msg;
            JObject result = null;
            try
            {
                //verify watershed exists
                if (!isWorkspaceValid(RepositoryDirectory)) throw new DirectoryNotFoundException("Workspace not found.");
                //convert to esriFeatures
                appendFeatures = parseFeatures(watershedEDL.Append, espg);
                removeFeatures = parseFeatures(watershedEDL.Remove, espg);
 
                result = Execute(getProcessRequest(getProcessName(processType.e_editwatershed), getBody(appendFeatures, removeFeatures,espg))) as JObject;

                if (isDynamicError(result, out msg)) throw new Exception("Delineation Error: " + msg);
                parseResult(result);
                return true;
            }
            catch (Exception ex)
            {
                sm("Error editing watershed " + ex.Message);
                return false;
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
                List<Parameter> selectedList = parameters.Where(p => requestPCodes.Contains(p.code.ToLower())).ToList();

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
            //List<Parameter> dbParameterList;
            List<Parameter> regionParameterList;
            List<string> groupCodes;
            try
            {
                //returns name, code for selected region
                xml = new SSXMLAgent(state);
                regionParameterList = xml.GetRegionParameters();
                this.sm(xml.Messages);

                db = new postgresqldbOps(ConfigurationManager.AppSettings["SSDBConnectionString"]);
                groupCodes = db.GetGroupCodes(state, group);

                if (groupCodes.Count > 0) { 
                    regionParameterList = regionParameterList.Where(a => groupCodes.Contains(a.code)).ToList();
                    sm("sync w/ group. Final Count:" + regionParameterList.Count);
                }

                db.LoadParameterList(regionParameterList);
                this.sm(db.Messages);


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
        public Stream GetFileItem(Int32 type)
        {
            string result = string.Empty;
            //1= shape
            //2=gdb
            if (type == 1)
            {
                dynamic resultObj = Execute(getProcessRequest(getProcessName(processType.e_shape),
                                        String.Format("-workspaceID {0} -directory {1} -toType {2}",
                                        this.WorkspaceString, RepositoryDirectory, type)));
                result = resultObj.Workspace;
            }
            else
                result = Path.Combine(WorkspaceString, WorkspaceString + ".gdb");


            Storage aStorage = new Storage(this.RepositoryDirectory);
            return aStorage.GetZipFile(result);
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
            List<string> requestfCodes;

            requestfCodes = this.parse(flowtypeList);

            var result = Execute(getProcessRequest(getProcessName(processType.e_flowstats), getstatisticsBody(state, requestfCodes))) as JObject;

            return result;
        }
        public List<FeatureWrapper> GetFeatures(string features, Int32 crsCode, Int32 simplificationOption = 1)
        {
            List<string> requestFcodes = new List<string>();
            List<FeatureWrapper> results;
            try
            {

                loadFeatures(features, crsCode, simplificationOption);

                if (string.IsNullOrEmpty(features)) results = this._featureResultList.Select(x => x.Value).ToList();
                else results = this._featureResultList.Select(x => x.Value).ToList();

                return results;

            }
            catch (Exception)
            {
                
                throw;
            }
           

        }
        public IDictionary<string,string> GetAttributes(string attrList)
        {
            JObject result = null;
            List<string> attrCodes;

            try
            {
                attrCodes = this.parse(attrList);
                if (attrCodes == null && attrCodes.Count <= 0) return new Dictionary<string,string>();

                result = Execute(getProcessRequest(getProcessName(processType.e_attributes), getBody(String.Join(";", attrCodes)))) as JObject;
                
                //deserialize result
                return parseAttributes(result,attrCodes);
            }
            catch (Exception ex)
            {
                throw;
            }
        }
        #endregion

        #region Watershed Helper Methods
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
        private string getBody(string state, double X, double Y, int wkid)
        {
            List<string> body = new List<string>();
            try
            {
                body.Add("-directory " + RepositoryDirectory);
                body.Add("-stabbr " + state);
                body.Add(String.Format("-pourpoint [{0},{1}]",X,Y));
                body.Add("-pourpointwkid " + wkid);
                return string.Join(" ", body);
            }
            catch (Exception)
            {
                throw;
            }
        }//end getParameterList   
        private void parseResult(JObject SSdelineationResult)
        {
            char[] delimiterChars = { '_'};
            try
            {
                JToken results = SSdelineationResult;
                this.WorkspaceString = results.Value<string>("Workspace");
                this.sm(results.Value<string>("Message").
                    Split(delimiterChars, StringSplitOptions.RemoveEmptyEntries).Where(msg => msg.Contains("AHMSG:"))
                                                                                .Select(msg => msg.Substring((msg.IndexOf("Start Time:")) > 0 ? msg.IndexOf("Start Time:") : 0)).ToList());
                
            }
            catch (Exception ex)
            {
                sm("Error parsing delineation result " + ex.Message);
                throw new Exception("Error parsing delineation result " + ex.Message);
            }//end try
        }//end parseDelineatinResult 

        private string getBody(List<GeometryBase> appendList, List<GeometryBase> removeList, int wkid)
        {
            List<string> body = new List<string>();
            try
            {
                body.Add("-workspaceID " + this.WorkspaceString);
                body.Add("-directory " + RepositoryDirectory);
                body.Add("-appendlist " +  JsonConvert.SerializeObject(appendList));
                body.Add("-removelist " + JsonConvert.SerializeObject(removeList));
                body.Add("-wkid " + wkid);
                return string.Join(" ", body);
            }
            catch (Exception)
            {
                throw;
            }
        }//end getParameterList  
        private List<GeometryBase> parseFeatures(List<dynamic> jobj, Int32 espg)
        {
            List<GeometryBase> featurelist = new List<GeometryBase>();
            EsriFeature rset = null;
            try
            {
                 
                foreach (JToken item in jobj)
                {
                    String geomtype = Convert.ToString(item.SelectToken("geometry.type"));
                    rset = new EsriFeature(item, geomtype);
                    featurelist.Add(rset.geometry);
                }//next item

                return featurelist;
            }
            catch (Exception ex)
            {
                throw;
            }//end try
        }
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
                body.Add("-directory " + RepositoryDirectory);


                return string.Join(" ", body);
            }
            catch (Exception)
            {
                throw;
            }
        }

        private List<Parameter> parseParameters(JToken jobj, List<Parameter> paramList)
        {
            Parameter selectedParam = null;
            JArray objArray = (JArray)jobj.SelectToken("Parameters");
            char[] delimiterChars = { '_' };

            this.sm(jobj.Value<string>("Message")
                .Split(delimiterChars, StringSplitOptions.RemoveEmptyEntries).Where(msg => msg.Contains("AHMSG:"))
                                                                             .Select(msg => msg.Substring((msg.IndexOf("Start Time:")) > 0 ? msg.IndexOf("Start Time:") : 0)).ToList());

            foreach (var p in objArray)
            {
                if ((p["code"] != null || p["value"] != null) && !String.IsNullOrEmpty(p.SelectToken("value").ToString()))
                {
                    selectedParam = paramList.FirstOrDefault(sp => string.Equals(sp.code, p.SelectToken("code").ToString(), StringComparison.OrdinalIgnoreCase));
                    if(selectedParam !=null)    
                        selectedParam.value = (Double)p.SelectToken("value");
                }//end if                    
            }//next p

            return paramList;
        }
        #endregion

        #region Statistics Helper Methods
        private string getstatisticsBody(string state,List<string> flowtypeList )
        {
            List<string> body = new List<string>();
            string flowtype = string.Empty;
            try
            {
                flowtype = string.Join(";", flowtypeList.Select(p => p).ToList());

                body.Add("-stabbr " + state);
                if(!string.IsNullOrEmpty(flowtype))
                    // double quotes around flow type to account for spaces"
                    body.Add("-flowtype " + '"'+flowtype+'"');
                body.Add("-workspaceID " + this.WorkspaceString);
                body.Add("-directory " + RepositoryDirectory);

                return string.Join(" ", body);
            }
            catch (Exception)
            {
                throw;
            }
        }//end getParameterList   
        #endregion

        #region Feature Helper Methods
        private string loadFeatures(string feature, Int32 crsCode, Int32 simplificationOption)
        {
            JObject result = null;
            List<string> requestFCodes;
            string msg;
            try
            {
                requestFCodes = parse(feature);
                if(string.IsNullOrEmpty(this.WorkspaceString)) throw new Exception("workspace string must not be null");
                
                result = Execute(getProcessRequest(getProcessName(processType.e_features), getBody(requestFCodes, crsCode, simplificationOption))) as JObject;
                if (isDynamicError(result, out msg)) throw new Exception("Feature Error: " + msg);
                return parseFeatures(result);

            }
            catch (Exception ex)
            {
                throw;
            }

        }
        private string getBody(List<string> fList,int crsCode, int simplificationOption)
        {
            List<string> body = new List<string>();
            try
            {   
                if(fList.Count > 0)
                    body.Add("-includefeatures "+ string.Join(";", fList.Select(f => f).ToList()));
                body.Add("-workspaceID " + this.WorkspaceString);
                body.Add("-directory " + RepositoryDirectory);
                body.Add("-outputcrs " + crsCode);
                body.Add("-simplification " + simplificationOption);


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

        #endregion

        #region Attribute Helper Methods
        private string getBody(string aList)
        {
            List<string> body = new List<string>();
            try
            {
                body.Add("-workspaceID " + this.WorkspaceString);
                body.Add("-directory " + RepositoryDirectory);
                body.Add("-attributes " + aList);


                return string.Join(" ", body);
            }
            catch (Exception)
            {
                throw;
            }
        }
        private IDictionary<string, string> parseAttributes(JObject jobj, List<string>attrlist)
        {
            Dictionary<string,string> Attributes = new Dictionary<string,string>(StringComparer.InvariantCultureIgnoreCase);           
            char[] delimiterChars = { '_' };
            try
            {
                JArray objArray = (JArray)jobj.SelectToken("Attributes");

                this.sm(jobj.Value<string>("Message")
                    .Split(delimiterChars, StringSplitOptions.RemoveEmptyEntries).Where(msg => msg.Contains("AHMSG:"))
                                                                                 .Select(msg => msg.Substring((msg.IndexOf("Start Time:")) > 0 ? msg.IndexOf("Start Time:") : 0)).ToList());

                foreach (var a in attrlist)
                {
                    foreach (var r in objArray)
                    {
                        if ((r["name"] != null || r["value"] != null) && !String.IsNullOrEmpty(r.SelectToken("value").ToString()) && String.Equals(r.SelectToken("name").ToString(),a,StringComparison.OrdinalIgnoreCase))
                        {
                            if (!Attributes.ContainsKey(r.SelectToken("name").ToString()))
                                Attributes.Add(r.SelectToken("name").ToString(), r.SelectToken("value").ToString());
                        }//end if   
                    }//next r                                    
                }//next a

                return Attributes;
            }
            catch (Exception ex)
            {
                throw;
            }//end try
        }

        #endregion

        #region Other Helper Methods
        protected string getRepositoryPath()
        {
            string selectedPath = string.Empty;
            string uncPaths = ConfigurationManager.AppSettings["UNCDrives"];
            string repository = ConfigurationManager.AppSettings["SSRepository"];
            try
            {
                //is there a workspaceID
                bool isWorkspace = string.IsNullOrEmpty(this.WorkspaceString);

                foreach (string dir in uncPaths.Split(','))
                {
                    selectedPath = System.IO.Path.Combine(dir, repository);
                    if (!System.IO.Directory.Exists(selectedPath)) 
                        continue;
                    else if (string.IsNullOrEmpty(this.WorkspaceString) || System.IO.Directory.Exists(System.IO.Path.Combine(selectedPath, WorkspaceString)))
                    {
                        //sm("selected path: " + selectedPath);
                        return selectedPath;
                    }
                }//next dir
                throw new Exception("Directory not found");
            }
            catch (Exception ex)
            {
                throw new Exception("Error finding directory " + ex.Message);
            }
        }
        private Boolean isWorkspaceValid(string repository)
        {
            try
            {
                if (!Directory.Exists(Path.Combine(repository, this.WorkspaceString))) return false;
                return true;
            }
            catch (Exception)
            {
                return false;
            }
        }
        private Boolean isFeature(JToken jobj, out List<FeatureBase> Feature, out int wkid, out string gtype, out List<Field> fields)
        {
            JArray obj = null;
            Feature = new List<FeatureBase>();

            try
            {                                
                fields = jobj["fields"] != null ? JsonConvert.DeserializeObject<List<Field>>(jobj.SelectToken("fields").ToString()) : null;
                obj = (JArray)jobj.SelectToken("features") ?? (JArray)jobj.SelectToken("geometry");
                gtype = (string)jobj.SelectToken("geometryType")??(string)jobj.SelectToken("type");
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
                case processType.e_editwatershed:
                    uri = ConfigurationManager.AppSettings["EditWatershed"];
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
                case processType.e_attributes:
                    uri = ConfigurationManager.AppSettings["Attributes"];
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
                if (error == null) return false;
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
            char[] delimiterChars = { ';', ','};
            return items.ToLower().Split(delimiterChars, StringSplitOptions.RemoveEmptyEntries).ToList();
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
            e_features,
            e_editwatershed,
            e_attributes

        }

        #endregion
    }
}
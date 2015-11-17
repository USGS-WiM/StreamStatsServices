using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Xml.Serialization;

using WiM.Resources.Spatial;
using WiM.Resources;
using Newtonsoft.Json;

namespace SStats.Resources
{

    [XmlInclude(typeof(EsriFeatureRecordSet))]
    [XmlRoot("watershed")]
    public class Watershed
    {
        public Watershed() {
            this.FeatureList = new List<FeatureWrapper>();
        }
        [JsonProperty("workspaceID")]
        [XmlElement("workspaceID")]
        public string workspaceID { get; set; }

        [JsonProperty("featurecollection")]
        [XmlArray("featurecollection")]
        [XmlArrayItem("feature")]
        public List<FeatureWrapper> FeatureList { get; set; }
        
        [JsonProperty("parameters")]
        [XmlArray("parameters")]
        [XmlArrayItem("parameter")]
        public List<Parameter> Parameters { get; set; }

        [JsonProperty("messages")]
        [XmlArray("messages")]
        [XmlArrayItem("message")]
        public List<String> Messages { get; set; }
    }

    [XmlInclude(typeof(EsriFeatureRecordSet))]
    [XmlRoot("features")]
    public class Features
    {
        [JsonProperty("featurecollection")]
        [XmlArray("featurecollection")]
        [XmlArrayItem("feature")]
        public List<FeatureWrapper> FeatureList { get; set; }

        [JsonProperty("messages")]
        [XmlArray("messages")]
        [XmlArrayItem("message")]
        public List<String> Messages { get; set; }
    }

    [XmlRoot("parameters")]
    public class Parameters
    {
        [JsonProperty("parameters")]
        [XmlArray("parameters")]
        [XmlArrayItem("parameter")]
        public List<Parameter> ParameterList { get; set; }

        [JsonProperty("messages")]
        [XmlArray("messages")]
        [XmlArrayItem("message")]
        public List<String> Messages { get; set; }
    }

    [XmlRoot("parametergroups")]
    public class ParameterGroups
    {
        [JsonProperty("groups")]
        [XmlArray("groups")]
        [XmlArrayItem("group")]
        public List<String> GroupList { get; set; }

        [JsonProperty("messages")]
        [XmlArray("messages")]
        [XmlArrayItem("message")]
        public List<String> Messages { get; set; }
    }

    [XmlRoot("flowstatistics")]
    public class FlowStatistics
    {
        [JsonProperty("flowstatistics")]
        [XmlArray("flowstatistics")]
        [XmlArrayItem("flowstatistic")]
        public List<string> FlowStatsList { get; set; }

        [JsonProperty("messages")]
        [XmlArray("messages")]
        [XmlArrayItem("message")]
        public List<String> Messages { get; set; }
    }

    [XmlRoot("capabilities")]
    public class Capabilities
    {
        [JsonProperty("region")]
        [XmlElement("region")]
        public string regionCode { get; set; }

        [JsonProperty("mapservice")]
        [XmlElement("mapservice")]
        public string mapservice { get; set; }

        [JsonProperty("mapservice_src")]
        [XmlElement("mapservice_src")]
        public string mapservice_src { get; set; }

        [JsonProperty("availabletools")]
        [XmlArray("availabletools")]
        [XmlArrayItem("tool")]
        public List<string> toolList { get; set; }

        [JsonProperty("messages")]
        [XmlArray("messages")]
        [XmlArrayItem("message")]
        public List<String> Messages { get; set; }
    }
    
}//end namespace
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Xml.Serialization;

using NSSService.Resources;
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
        public List<WiM.Resources.Parameter> Parameters { get; set; }

        [JsonProperty("messages")]
        [XmlArray("messages")]
        [XmlArrayItem("message")]
        public List<String> Messages { get; set; }
    }

    //[XmlInclude(typeof(EsriFeature))]
    [XmlRoot("WatershedEDL")]
    public class WatershedEditDecisionList
    {
        [JsonProperty("append")]
        [XmlElement("append")]
        public List<dynamic> Append { get; set; }
        [JsonProperty("remove")]
        [XmlElement("remove")]
        public List<dynamic> Remove { get; set; }
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
    [XmlInclude(typeof(EsriFeatureRecordSet))]
    [XmlRoot("features")]
    public class NHDTrace
    {
        [JsonProperty("featurecollection")]
        [XmlArray("featurecollection")]
        [XmlArrayItem("feature")]
        public List<FeatureWrapper> FeatureList { get; set; }

        public string Report { get; set; }

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
        public List<WiM.Resources.Parameter> ParameterList { get; set; }

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
        public List<StatisticGroupType> FlowStatsList { get; set; }

        [JsonProperty("messages")]
        [XmlArray("messages")]
        [XmlArrayItem("message")]
        public List<String> Messages { get; set; }
    }
   
    
}//end namespace
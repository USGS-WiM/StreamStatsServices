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
            this.FeatureList = new Dictionary<string, FeatureCollectionBase>();
        }
        [JsonProperty("workspaceID")]
        [XmlElement("workspaceID")]
        public string workspaceID { get; set; }

        public Dictionary<string, FeatureCollectionBase> FeatureList { get; set; }

        //[JsonProperty("delineatedbasin")]
        //[XmlElement("delineatedbasin")]
        //public FeatureCollectionBase DelineatedBasin { get; set; }
        
        //[JsonProperty("pourpoint")]
        //[XmlElement("pourpoint")]
        //public FeatureCollectionBase PourPoint { get; set; }
        
        [JsonProperty("parameters")]
        [XmlArray("parameters")]
        [XmlArrayItem("parameter")]
        public List<Parameter> Parameters { get; set; }

        [JsonProperty("messages")]
        [XmlArray("messages")]
        [XmlArrayItem("message")]
        public List<String> Messages { get; set; }
    }//end streamStats

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
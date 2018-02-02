using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Xml.Serialization;
using WiM.Resources;
using Newtonsoft.Json;
using GeoJSON.Net.Geometry;

namespace StreamStatsAgent.Resources
{
    [XmlRoot("WatershedEDL")]
    public class WatershedEditDecisionList
    {
        public List<MultiLineString> Append { get; set; }
        public List<MultiLineString> Remove { get; set; }
    }
}//end namespace
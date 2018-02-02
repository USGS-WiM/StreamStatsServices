using System;
using System.Collections.Generic;
using System.Text;
using GeoJSON.Net.Feature;

namespace StreamStatsAgent.Resources
{
    public class Watershed
    {
        public string WorkspaceID { get; set; }
        public List<FeatureItem> FeatureList { get; set; }
        public List<Parameter> Parameters { get; set; }
    }
    public class FeatureItem
    {
        public string Name { get; set; }
        public Feature Feature { get; set; }
    }
}

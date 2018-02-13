using System;
using System.Collections.Generic;
using System.Text;
using GeoJSON.Net.Feature;

namespace StreamStatsAgent.Resources
{
    public class Watershed
    {
        public string WorkspaceID { get; set; }
        public FeatureCollection Layers { get; set; }
        public List<Parameter> Parameters { get; set; }
    }
}

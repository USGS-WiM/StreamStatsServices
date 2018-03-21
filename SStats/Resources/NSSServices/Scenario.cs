using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Xml.Serialization;
//using WiM.Resources;
using Newtonsoft.Json;

namespace NSSService.Resources
{
    public class Scenario
    {
        public int StatisticGroupID { get; set; }
        public string StatisticGroupName { get; set; }
        public List<RegionEquation> RegressionRegions { get; set; }
        public List<dynamic> Links { get; set; }
    }//end Scenario

    public class Parameter
    {
        public Int32 ID { get; set; }
        public string Name { get; set; }
        public string Code { get; set; }
        public string Description { get; set; }
        public Double Value { get; set; }
        public dynamic UnitType { get; set; }
        public dynamic Limits { get; set; }
    }

    public class RegionEquation
    {
        public RegionEquation() { }

        public Int32 ID { get; set; }
        public string Name { get; set; }
        public string Code { get; set; }
        public double? PercentWeight { get; set; }
        public bool ShouldSerializePercentWeight()
        { return PercentWeight.HasValue; }
        public List<Parameter> Parameters { get; set; }
        public List<RegressionResult> Results { get; set; }
        public List<dynamic> Extensions { get; set; }
        public bool ShouldSerializeExtension()
        { return Extensions != null || Extensions.Count > 1; }

        public string Disclaimer { get; set; }
        public bool ShouldSerializeDisclaimer()
        { return !string.IsNullOrEmpty(Disclaimer); }
    }
}
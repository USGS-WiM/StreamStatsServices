using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Xml.Serialization;
using WiM.Resources;
using Newtonsoft.Json;
using System.Runtime.Serialization.Formatters.Binary;
using System.IO;

namespace NSSService.Resources
{
    public class RegressionResult
    {
        public Double? EquivalentYears { get; set; }
        public string Name { get; set; }
        public string code { get; set; }
        public string Description { get; set; }
        public Double? Value { get; set; }
        public List<Error> Errors { get; set; }
        public dynamic UnitType { get; set; }
        public String Equation { get; set; }
        public IntervalBounds IntervalBounds { get; set; }
    }//end class

    public class Error
    {
        public string Name { get; set; }
        public string Code { get; set; }
        public Double? Value { get; set; }
    }//end class

    public class IntervalBounds
    {
        public double Lower { get; set; }
        public double Upper { get; set; }
    }
    
}//end namespace
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace CoordinatedReachServices.Resources
{
    public class CoordReachCoeff
    {
        public Double CoefficientA { get; set; }
        public Double CoefficientB { get; set; }
    }
    public class CoordinatedReach
    {
        public String Name { get; set; }
        public String ID { get; set; }
        public Dictionary<string, CoordReachCoeff> FlowCoefficient { get; private set; }

        public CoordinatedReach()
        {
            FlowCoefficient = new Dictionary<string, CoordReachCoeff>();
        }
    }
}

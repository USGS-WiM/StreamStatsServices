using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using WiM.Resources;

namespace StreamStatsAgent.Resources
{
    public class Parameter:IParameter
    {
        public Int32 ID { get; set; }
        public string Name { get;set; }
        public string Description { get; set; }
        public string Code { get; set; }
        public IUnit Unit { get; set; }
        public double? Value { get; set; }

        public static Parameter FromDataReader(System.Data.IDataReader r)
        {
            return new Parameter()
            {
                Code = r["Code"] is DBNull ? "" : (r["Code"]).ToString(),
                Name = r["Name"] is DBNull ? "" : (r["Name"]).ToString(),
                Description = r["Description"] is DBNull ? "" : (r["Description"]).ToString(),
                Unit = { Abbr = r["UnitAbr"] is DBNull ? "" : (r["UnitAbr"]).ToString(), Unit = r["Unit"] is DBNull ? "" : (r["Unit"]).ToString() }
            };

        }
    }
}
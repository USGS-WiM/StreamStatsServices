using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace SStats.Resources
{
    public class Param:WiM.Resources.Parameter
    {
        public Int32 ID { get; set; }

        public static Param FromDataReader(System.Data.IDataReader r)
        {
            return new Param()
            {
                code = r["Code"] is DBNull ? "" : (r["Code"]).ToString(),
                name = r["Name"] is DBNull ? "" : (r["Name"]).ToString(),
                description = r["Description"] is DBNull ? "" : (r["Description"]).ToString(),
                unit = r["Unit"] is DBNull ? "" : (r["Unit"]).ToString()
            };

        }
    }
}
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using WiM.Utilities.ServiceAgent;
using NSSService.Resources;
using System.Configuration;
using WiM.Resources.Spatial;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.IO;

namespace SStats.Utilities.ServiceAgent
{   

    public class StateSelectServiceAgent : ServiceAgentBase
    {
        public StateSelectServiceAgent() : base(ConfigurationManager.AppSettings["gisHostServer"])
        {
        }
        public string getUnderlyingBasinCode(Point pnt, Int32 crs)
        {
            string msg = string.Empty;
            try
            {
                //test if espg correct, if not request projection
                if ( crs != 4326)
                {
                    //project?inSR=4326&outSR=26915&geometries={geometries:[{x:-93.9508,y:42.0191}],geometryType:esriGeometryPoint}f=pjson
                    var result = Execute(new RestSharp.RestRequest(String.Format(ConfigurationManager.AppSettings["projections"], crs, 4326, pnt.coordinates[0], pnt.coordinates[1]))) as JObject;
                    if (isDynamicError(result, out msg)) throw new Exception(msg);
                    var geom = result.SelectToken("geometries").FirstOrDefault();
                    pnt = new Point(Convert.ToDouble(geom.SelectToken("x")), Convert.ToDouble(geom.SelectToken("y")));
                }
                
                //get polygons
                var stateFC = JsonConvert.DeserializeObject(File.ReadAllText(Path.Combine(new String[] { AppDomain.CurrentDomain.BaseDirectory, "Assets", ConfigurationManager.AppSettings["statejson"] }))) as JObject;
                foreach (var item in stateFC["features"].Children())
                {
                    if (!String.Equals(item.SelectToken("geometry.type").ToString(), "Polygon")) continue;

                    var rings = item.SelectToken("geometry.coordinates").ToObject<List<List<List<double>>>>();
                    if (!ContainsPoint(rings,pnt)) continue;
                    
                    return item.SelectToken("properties.abbr").ToString();

                }//next item



                throw new NotImplementedException();
            }
            catch (Exception ex)
            {
                return string.Empty;
            }

        }
        private bool ContainsPoint(List<List<List<double>>> poly, Point pt)
        {
            try
            {
                var containsPoint = false;
                // check if it is in the outer ring first
                if (ContainsPoint(poly[0],pt))
                {
                    var i = 1;
                    var inHole = false;
                    while (i < poly.Count() && !inHole)
                    {
                        if (ContainsPoint(poly[i],pt)) inHole = true;
                        i++;
                    }//next
                    if (!inHole) containsPoint = true;
                }//endif

                return containsPoint;
            }
            catch (Exception ex)
            {
                throw;
            }
        }
        private bool ContainsPoint (List<List<double>> ring, Point pt)
        {
            var isInside = false;
            var j = ring.Count() - 1;
            for (var i = 0; i < ring.Count(); j = i++)
            {
                var xi = ring[i][1];
                var yi = ring[i][0];
                var xj = ring[j][1];
                var yj = ring[j][0];

                var intersect = ((yi > pt.coordinates[0]) != (yj > pt.coordinates[0])) &&
                    (pt.coordinates[1] < (xj - xi) * (pt.coordinates[0] - yi) / (yj - yi) + xi);
                if (intersect) isInside = !isInside;
            }//next
            return isInside;
        }
        private Boolean isDynamicError(dynamic obj, out string msg)
        {
            msg = string.Empty;
            try
            {
                var error = obj.error;
                if (error == null) throw new Exception();
                msg = error.message;
                return true;
            }
            catch (Exception ex)
            {

                return false;
            }

        }
    }
}
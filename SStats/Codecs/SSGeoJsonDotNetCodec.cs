//------------------------------------------------------------------------------
//----- JsonDotNetCodec -----------------------------------------------------------
//------------------------------------------------------------------------------

//-------1---------2---------3---------4---------5---------6---------7---------8
//       01234567890123456789012345678901234567890123456789012345678901234567890
//-------+---------+---------+---------+---------+---------+---------+---------+

// copyright:   2013 WiM - USGS

//    authors:  Jeremy Newson USGS Wisconsin Internet Mapping
//  
//   purpose:   Created a JSON Codec that works with EF. JsonDataContractCodec 
//              does not work because IsReference is set
//
//discussion:   A Codec is an enCOder/DECoder for a resources in 
//              this case the resources are POCO classes derived from the EF. 
//              https://github.com/openrasta/openrasta/wiki/Codecs
//
//     

#region Comments
// 02.03.12 - JB - Created to properly de/serialize JSON
#endregion

using System;
using System.IO;
using System.Text;
using System.Reflection;
using System.Collections.Generic;
using System.Linq;

using OpenRasta.TypeSystem;
using OpenRasta.Web;
using OpenRasta.Codecs;

using SStats.Resources;
using WiM.Resources.Spatial;
using Newtonsoft.Json;
using WiM.Codecs.json;

namespace SStats.Codecs.json
{
     [MediaType("application/json;q=0.5", "json")]
     [MediaType("application/geojson;q=0.5", "geojson")]
    public class SSGeoJsonDotNetCodec: JsonDotNetCodec
    {

        public override void WriteTo(object entity, IHttpEntity response, string[] parameters)
        {
            List<FeatureWrapper> fw = null;
            try
            {            
                if (entity == null)
                    return;

                if (entity.GetType() == typeof(Watershed)) 
                    fw = ((Watershed)entity).FeatureList;
                else if (entity.GetType() == typeof(Features))
                    fw =  ((Features)entity).FeatureList;
                else if (entity.GetType() == typeof(NHDTrace))
                    fw = ((NHDTrace)entity).FeatureList;

                if (fw != null)
                {
                    foreach (FeatureWrapper item in fw)
                    {
                        if (item.feature.GetType() == typeof(EsriFeatureRecordSet))
                            item.feature = (FeatureCollection)(item.feature as EsriFeatureRecordSet);
                    }//next item
                }//endif 

                //reset content type to json
                response.ContentType = MediaType.Json;

                base.WriteTo(entity, response, parameters);
                
            }
            catch (Exception ex)
            {

                base.WriteTo(entity, response, parameters);
            }
                        
        }
    }
}


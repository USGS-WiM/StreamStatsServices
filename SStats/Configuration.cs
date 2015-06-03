//------------------------------------------------------------------------------
//----- Configuration -----------------------------------------------------------
//------------------------------------------------------------------------------

//-------1---------2---------3---------4---------5---------6---------7---------8
//       01234567890123456789012345678901234567890123456789012345678901234567890
//-------+---------+---------+---------+---------+---------+---------+---------+

// copyright:   2014 WiM - USGS

//    authors:  Jeremy Newson          
//  
//   purpose:   Configuration implements the IConfiurationSource interface. OpenRasta
//              will call the Configure method and use it to configure the application 
//              through a fluent interface using the Resource space as root objects. 
//
//discussion:   The ResourceSpace is where you can define the resources in the application and what
//              handles them and how thy are represented. 
//              https://github.com/openrasta/openrasta/wiki/Configuration
//
//     
#region Comments
// 02.21.14 - JKN - Created
#endregion
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

using OpenRasta.Configuration;
using OpenRasta.IO;
using OpenRasta.Pipeline.Contributors;
using OpenRasta.Web.UriDecorators;
using SStats.Codecs.json;

using WiM.Codecs.json;
using WiM.Codecs.xml;
using WiM.PipeLineContributors;

//using WiM.URIDecorators;

using SStats.Resources;
using SStats.Handlers;

namespace SStats
{
    public class Configuration:IConfigurationSource
    {
        public void Configure()
        {
            using (OpenRastaConfiguration.Manual)
            {
                // Allow codec choice by extension 
                ResourceSpace.Uses.UriDecorator<ContentTypeExtensionUriDecorator>();
                ResourceSpace.Uses.PipelineContributor<ErrorCheckingContributor>();
                ResourceSpace.Uses.PipelineContributor<CrossDomainPipelineContributor>();

                //watershed
                addWatershedResource();
                addParameterResource();
                addDownloadResource();
                addFlowStatisticResource();
                addFeatureResource();
            http://support.esri.com/ja/knowledgebase/techarticles/detail/39029

                //the capabilites section if for vs 3 and needs to be removed -jkn
                ResourceSpace.Has.ResourcesOfType<List<Capabilities>>()
                .AtUri("/capabilities?rcode={regioncode}&type={type}")
                .HandledBy<CapabilitiesHandler>()
                .TranscodedBy<UTF8XmlSerializerCodec>(null).ForMediaType("application/xml;q=1").ForExtension("xml")
                .And.TranscodedBy<JsonDotNetCodec>(null).ForMediaType("application/json;q=0.9").ForExtension("json");

            }//end using
        }//end Configure

        #region Helper methods
        private void addWatershedResource(){
        ResourceSpace.Has.ResourcesOfType<Watershed>()
                .AtUri("/watershed?rcode={regioncode}&xlocation={X}&ylocation={Y}&crs={espg}&simplify={simplificationOption}&includeparameters={parameterList}&includeflowtypes={flowtypeList}&includefeatures={featureList}")
                .And.AtUri("/watershed?rcode={regioncode}&workspaceID={workspaceID}&includeparameters={parameterList}&includeflowtypes={flowtypeList}&includefeatures={featureList}").Named("GetWatershedFromWorkspaceID")
                .HandledBy<WatershedHandler>()
                .TranscodedBy<UTF8XmlSerializerCodec>(null).ForMediaType("application/xml;q=1").ForExtension("xml")
                .And.TranscodedBy<JsonDotNetCodec>(null).ForMediaType("application/json;q=0.9").ForExtension("json")
                .And.TranscodedBy<SSGeoJsonDotNetCodec>(null).ForMediaType("application/geojson;q=0.9").ForExtension("geojson");
        
        }
        private void addParameterResource() {
            ResourceSpace.Has.ResourcesOfType<Parameters>()
                    .AtUri("/parameters?rcode={regioncode}&group={group}")
                    .And.AtUri("/parameters?rcode={regioncode}&workspaceID={workspaceID}&includeparameters={parameterList}").Named("GetParametersFromWorkspaceID")
                    .HandledBy<ParameterHandler>()
                    .TranscodedBy<UTF8XmlSerializerCodec>(null).ForMediaType("application/xml;q=1").ForExtension("xml")
                    .And.TranscodedBy<JsonDotNetCodec>(null).ForMediaType("application/json;q=0.9").ForExtension("json");
        }
        private void addDownloadResource() {
            ResourceSpace.Has.ResourcesOfType<IFile>()
                    .AtUri("/download?workspaceID={workspaceID}&format={f}").Named("DownloadZipFile")
                    .HandledBy<DownloadHandler>();
        }
        private void addFlowStatisticResource() {
            ResourceSpace.Has.ResourcesOfType<List<FlowStatistics>>()
                    .AtUri("/flowstatistics?rcode={regioncode}")
                    .HandledBy<StatisticsHandler>()
                    .TranscodedBy<UTF8XmlSerializerCodec>(null).ForMediaType("application/xml;q=1").ForExtension("xml")
                    .And.TranscodedBy<JsonDotNetCodec>(null).ForMediaType("application/json;q=0.9").ForExtension("json");

            ResourceSpace.Has.ResourcesOfType<dynamic>()
             .AtUri("flowstatistics?rcode={regioncode}&workspaceID={workspaceID}&flowtypes={flowtypeList}").Named("GetFlowStatsFromWorkspaceID")
            .HandledBy<StatisticsHandler>()
            .TranscodedBy<JsonDotNetCodec>(null).ForMediaType("application/json;q=0.9");
        }
        private void addFeatureResource() {
            ResourceSpace.Has.ResourcesOfType<Features>()
             .AtUri("/features?workspaceID={workspaceID}&includefeatures={featureList}")
             .HandledBy<FeatureHandler>()
             .TranscodedBy<UTF8XmlSerializerCodec>(null).ForMediaType("application/xml;q=1").ForExtension("xml")
             .And.TranscodedBy<JsonDotNetCodec>(null).ForMediaType("application/json;q=0.9").ForExtension("json")
             .And.TranscodedBy<SSGeoJsonDotNetCodec>(null).ForMediaType("application/geojson;q=0.9").ForExtension("geojson");        
        }
        #endregion
    }//end Configuration
}//end namespace
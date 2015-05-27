//------------------------------------------------------------------------------
//----- ########## -------------------------------------------------------------
//------------------------------------------------------------------------------

//-------1---------2---------3---------4---------5---------6---------7---------8
//       01234567890123456789012345678901234567890123456789012345678901234567890
//-------+---------+---------+---------+---------+---------+---------+---------+

// copyright:   2015 WiM - USGS

//    authors:  Jeremy K. Newson USGS Wisconsin Internet Mapping
//             
// 
//   purpose:  
//          
//discussion:
//

#region "Comments"
//04.23.2015 jkn - Created
#endregion

#region "Imports"
using System;
using System.Configuration;
using System.Data;
using System.Xml;
using System.Xml.XPath;
using System.IO;
using WiM.Resources;
using System.Collections.Generic;
using System.Collections;
using System.Linq;
using System.Xml.Linq;
using SStats.Resources;



#endregion
namespace SStats.Utilities.ServiceAgent
{
    public class SSXMLAgent: IMessage
    {

    #region " asynchronous delegates "
    // these asynchronous delegates are pointers to procedures. we use the delegate's BeginInvoke
    // method to call the procedure asynchronously or we use the delegate's Invoke method to call
    // the routine synchronously. the delegate's BeginInvoke method takes the same arguments as
    // the procedure that the delegate points to, plus two additional arguments. Unlike the Invoke method,
    // BeginInvoke returns an IAsyncResult. The returned IAsyncResult's IsCompleted property is then
    // queried and if this property returns true then the delegate's EndInvoke method is called. this
    // method is used to retrieve both the return value and the value of any argument passed byRef.

    // there is one delegate declared for each procedure.
    #endregion
    #region "Events"
    #endregion
    #region "Fields"
        private XPathNavigator XNav;
    #endregion
    #region "Properties"   
        public string XMLFile { get; private set; }
        private List<string> _message = new List<string>();
        public List<string> Messages
        {
            get { return _message; }
        }
    #endregion
    #region "Collections & Dictionaries"
    #endregion
    #region "Constructor and IDisposable Support"
    #region Constructors   
        public SSXMLAgent(string regionCode)
        {
            string xmldirectory = ConfigurationManager.AppSettings["SSXMLRepository"];
            string file = Path.Combine(xmldirectory, "StreamStats" + regionCode + ".xml");
            if (!File.Exists(file)) throw new Exception("file doesn't exist. " + file);
            this.XMLFile = file;
            //loadXMLNavigator();
        }
    #endregion 
    #region IDisposable Support
        // Track whether Dispose has been called.
        private bool disposed = false;

        // Implement IDisposable.
        // Do not make this method virtual.
        // A derived class should not be able to override this method.
        public void Dispose()
        {
            Dispose(true);
            // This object will be cleaned up by the Dispose method.
            // Therefore, you should call GC.SupressFinalize to
            // take this object off the finalization queue
            // and prevent finalization code for this object
            // from executing a second time.
            GC.SuppressFinalize(this);
        } //End Dispose

        // Dispose(bool disposing) executes in two distinct scenarios.
        // If disposing equals true, the method has been called directly
        // or indirectly by a user's code. Managed and unmanaged resources
        // can be disposed.
        // If disposing equals false, the method has been called by the
        // runtime from inside the finalizer and you should not reference
        // other objects. Only unmanaged resources can be disposed.
        protected virtual void Dispose(bool disposing)
        {
            // Check to see if Dispose has already been called.
            if (!this.disposed)
            {
                if (disposing)
                {

                    // TODO:Dispose managed resources here.
                    //ie component.Dispose();

                }//EndIF

                // TODO:Call the appropriate methods to clean up
                // unmanaged resources here.
                //ComRelease(Extent);

                // Note disposing has been done.
                disposed = true;


            }//EndIf
        }//End Dispose
        #endregion
    #endregion
    #region "Methods"
        public List<Parameter> GetRegionParameters() {
            XElement iterator = null;
            IQueryable<XElement> query;
            IEnumerable<XElement> paramElements;

            try
            {
                iterator = XElement.Load(this.XMLFile);
                query = iterator.Descendants("ApFunction").Where(a => a.Attribute("Name").Value == "WshParams").AsQueryable();
                paramElements = query.Elements("ParamsDisplayOrder");

                if (paramElements.Descendants().Count() > 0)
                {
                    sm("From displayOrder");
                    return loadParameters(paramElements.Descendants());
                }
                else {
                    sm("From ApFields");
                    return loadParameters(query.Elements("ApFields").Where(a => a.Attribute("TagName").Value == "ApFields").Elements()); 
                }

            }
            catch (Exception err) {
                this.sm(err.Message);
                throw err;
            }
        }
        public List<string> GetRegionFlowStats()
        {
            XElement iterator = null;
            IQueryable<XElement> query;

            try
            {
                iterator = XElement.Load(this.XMLFile);
                query = iterator.Descendants("ApFunction").Where(a => a.Attribute("Name").Value == "WshParams").AsQueryable();
                return query.Elements("ApLayers").Where(a => a.Attribute("TagName").Value == "RegionLayers").Elements().Select(l=>l.Attribute("TagName").Value).ToList();
            }
            catch (Exception err)
            {
                this.sm(err.Message);
                throw err;
            }
        }

        public static Capabilities GetRegionCapabilities(string regioncode,  String cType)
        {
            XElement iterator = null;
            XElement selectedItem;
            string xmlFile = ConfigurationManager.AppSettings["SSCapabilityRepository"];
            Capabilities capabilities = new Capabilities(); ;

            try
            {
                xmlFile = Path.Combine(xmlFile, string.Equals(cType, "dev", StringComparison.OrdinalIgnoreCase) ? "ApStates_dev.xml" : "ApStates_prod.xml");

                iterator = XElement.Load(xmlFile);
                selectedItem = iterator.Descendants("ApState").Where(a => String.Equals(a.Attribute("Name").Value, regioncode, StringComparison.OrdinalIgnoreCase)).FirstOrDefault();
                capabilities.regionCode = selectedItem.Attribute("Name")!= null? selectedItem.Attribute("Name").Value: null;
                capabilities.mapservice_src = selectedItem.Attribute("MapServiceWKID")!= null? selectedItem.Attribute("MapServiceWKID").Value:null;
                capabilities.mapservice = selectedItem.Attribute("MapServiceName")!= null? selectedItem.Attribute("MapServiceName").Value: null;
                capabilities.toolList = selectedItem.Elements("ApTools").Elements().Where(a => a.Attribute("Visible").Value == "1").Select(l => l.Attribute("Name").Value).ToList();

                return capabilities;
            }
            catch (Exception err)
            {
                throw err;
            }
        }
    #endregion
    #region "Helper Methods"
 
        private void loadXMLNavigator() {
            XPathDocument xdoc = new XPathDocument(this.XMLFile);
            this.XNav = xdoc.CreateNavigator();
        }
        private string getFieldTypeLocation(fieldType ft){
            switch (ft)
	        {
		        case fieldType.e_parameters:
                    return "//ApFunction[(Name=WshParams)]";

                default:
                    throw new Exception("ft not specified");
	        }//end switch
        }
        private List<Parameter> loadParameters(IEnumerable<XElement> elements)
        {
            sm("count: " + elements.Count());
            return elements.Select(x => new Parameter()
                    {
                        name = x.Attribute("Name").Value,
                        code = x.Attribute("TagName").Value
                    }).ToList();

        }
        private void sm(string msg){
            this._message.Add(msg);
        }
    #endregion
    #region "Structures"
        //A structure is a value type. When a structure is created, the variable to which the struct is assigned holds
        //the struct's actual data. When the struct is assigned to a new variable, it is copied. The new variable and
        //the original variable therefore contain two separate copies of the same data. Changes made to one copy do not
        //affect the other copy.

        //In general, classes are used to model more complex behavior, or data that is intended to be modified after a
        //class object is created. Structs are best suited for small data structures that contain primarily data that is
        //not intended to be modified after the struct is created.
    #endregion
    #region "Asynchronous Methods"

    #endregion
    #region "Enumerated Constants"
        public enum fieldType{
            e_parameters
        }
    #endregion

    }//end class XMLAgentBase
}//end namespace

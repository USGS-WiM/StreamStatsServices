//------------------------------------------------------------------------------
//----- postgresqldbOps -------------------------------------------------------------
//------------------------------------------------------------------------------

//-------1---------2---------3---------4---------5---------6---------7---------8
//       01234567890123456789012345678901234567890123456789012345678901234567890
//-------+---------+---------+---------+---------+---------+---------+---------+

// copyright:   2015 WiM - USGS

//    authors:  Jeremy K. Newson USGS Wisconsin Internet Mapping
//             
// 
//   purpose: Manage databases, provides retrieval/creation/update/deletion
//          
//discussion:
//

#region "Comments"
//02.09.2015 jkn - Created
#endregion

#region "Imports"
using System;
using System.Collections;
using System.Collections.Generic;
using System.Data;
using Npgsql;
using System.Linq;
using WiM.Resources;

#endregion

namespace SSDB
{
    public class postgresqldbOps:IDisposable, IMessage
    {
        #region "Fields"
        //Server=136.177.100.147;Port=5432;User Id=***REMOVED***;Password=***REMOVED***;Database=globalsde;
        private string connectionString = string.Empty;
        private NpgsqlConnection connection;
        #endregion
        #region Properties
        private List<string> _message = new List<string>();
        public List<string> Messages
        {
            get { return _message; }
        }
        #endregion
        #region "Constructor and IDisposable Support"
        #region Constructors
        public postgresqldbOps(string pSQLconnstring)
        {
            this.connectionString = pSQLconnstring;
            this.connection = new NpgsqlConnection(String.Format(connectionString, "***REMOVED***"));
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
                    if (this.connection.State != ConnectionState.Closed) this.connection.Close();
                    this.connection.Dispose();

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
        public List<Parameter> GetParameterList()
        {
            try
            {
                List<Parameter> para = new List<Parameter>();

                this.OpenConnection();
                NpgsqlCommand command = new NpgsqlCommand("select * from basin_char_defs", this.connection);

                using (NpgsqlDataReader reader = command.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        para.Add (new Parameter()
                        {
                            code = reader["Label"].ToString(),
                            description = reader["Definition"].ToString(),
                            unit = reader["English"].ToString()
                        });
                    }
                }

                return para;


            }
            catch (Exception ex)
            {
                this.sm(ex.Message);
                throw ex;
            }
            finally
            {
                this.CloseConnection();
            }
        }
        public List<string> GetGroupCodes(string state, string group)
        {
            string SQL;
            try
            {
                List<string> para = new List<string>();
                if (string.IsNullOrEmpty(group) || string.IsNullOrEmpty(state)) return para;

                this.OpenConnection();
                SQL = String.Format("SELECT * FROM report_fields_vw WHERE LOWER(st_abbr) = LOWER('{0}') AND LOWER(p_group)=LOWER('{1}');",state,group);
                NpgsqlCommand command = new NpgsqlCommand(SQL, this.connection);

                using (NpgsqlDataReader reader = command.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        string code = reader["p_fields"].ToString();
                        para.AddRange(code.Split(';').ToList());
                    }
                }
                this.sm("group count: " + para.Count);
                return para;
            }
            catch (Exception ex)
            {
                this.sm(ex.Message);
                throw ex;
            }
            finally
            {
                this.CloseConnection();
            }
        }
        public List<string> GetGroupCodes(string state)
        {
            string SQL;
            try
            {
                List<string> para = new List<string>();
                if (string.IsNullOrEmpty(state)) return para;

                this.OpenConnection();
                SQL = String.Format("SELECT * FROM report_fields_vw WHERE LOWER(st_abbr) = LOWER('{0}');", state);
                NpgsqlCommand command = new NpgsqlCommand(SQL, this.connection);

                using (NpgsqlDataReader reader = command.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        string code = reader["p_group"].ToString();
                        para.Add(code);
                    }
                }
                this.sm("group count: " + para.Count);
                return para;
            }
            catch (Exception ex)
            {
                this.sm(ex.Message);
                throw ex;
            }
            finally
            {
                this.CloseConnection();
            }
        }
        #endregion
        #region "Helper Methods"
        private void OpenConnection()
        {
            try
            {
                if (connection.State == ConnectionState.Open) this.connection.Close();
                this.connection.Open();
            }
            catch (Exception ex)
            {
                this.CloseConnection();
                throw ex;
            }
        }
        private void CloseConnection()
        {
            try
            {
                if (this.connection.State == ConnectionState.Open) this.connection.Close();
            }
            catch (Exception ex)
            {
                if (this.connection.State == ConnectionState.Open) connection.Close();
                throw ex;
            }
        }
        private void sm(string msg) {
            this._message.Add(msg);
        }
        #endregion
        #region "Enumerated Constants"
        #endregion

       
    }
}
















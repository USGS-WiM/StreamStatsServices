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
using System.Linq;
using System.Data.Common;
using System.Data.OleDb;
using MySql.Data;
using MySql.Data.MySqlClient;

#endregion

namespace SSDB
{
    public class dbOps : IDisposable
    {
        #region "Fields"
        private string connectionString = string.Empty;
        private DbConnection connection;
        public ConnectionType connectionType { get; private set; }
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
        public dbOps(string pSQLconnstring, ConnectionType pConnectionType, bool doResetTables = false)
        {
            this.connection = null;
            this.connectionString = pSQLconnstring;
            this.connectionType = pConnectionType;
            init();
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
        public List<T> GetDBItems<T>(SQLType type, params object[] args)
        {
            List<T> dbList = null;
            string sql = string.Empty;
            try
            {
                sql = string.Format(getSQL(type), args);

                this.OpenConnection();
                DbCommand command = getCommand(sql);
                Func<IDataReader, T> fromdr = (Func<IDataReader, T>)Delegate.CreateDelegate(typeof(Func<IDataReader, T>), null, typeof(T).GetMethod("FromDataReader"));

                using (DbDataReader reader = command.ExecuteReader())
                {
                    dbList = reader.Select<T>(fromdr).ToList();
                    sm("DB return count: " + dbList.Count);
                }//end using

                return dbList;
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
        public T FromDataReader<T>(IDataReader r)
        {
            return (T)Activator.CreateInstance(typeof(T), new object[] { });
        }
        private DbCommand getCommand(string sql)
        {
            switch (this.connectionType)
            {
                case ConnectionType.e_access:
                    return new OleDbCommand(sql, (OleDbConnection)this.connection);
                case ConnectionType.e_postgresql:
                    return null;
                case ConnectionType.e_mysql:
                    return new MySqlCommand(sql, (MySqlConnection)this.connection); ;
                default:
                    return null;
            }
        }
        private string getSQL(SQLType type)
        {
            string results = string.Empty;
            switch (type)
            {
                case SQLType.e_parameterlist:
                    results = @"SELECT vt.Name, vt.Description, vt.Code, ut.Unit FROM `nss`.`VariableType` vt 
                                left JOIN `nss`.`Variable` v ON (v.VariableTypeID = vt.ID)
                                left JOIN `nss`.`UnitType` ut ON (v.UnitTypeID = ut.ID)
                                WHERE `Code` IN ({0})
                                GROUP BY vt.Code; ";
                    break;
                default:
                    break;
            }
            return results;
        }
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
        private void init()
        {
            switch (connectionType)
            {
                case ConnectionType.e_access:
                    this.connection = new OleDbConnection(connectionString);
                    break;
                case ConnectionType.e_postgresql:
                    break;
                case ConnectionType.e_mysql:
                    this.connection = new MySqlConnection(connectionString);
                    break;
                default:
                    break;
            }

        }

        private void sm(string msg)
        {
            this._message.Add(msg);
        }
        #endregion
        #region "Enumerated Constants"
        public enum SQLType
        {
            e_parameterlist,
            
        }
        public enum ConnectionType
        {
            e_access,
            e_postgresql,
            e_mysql
        }
        #endregion

    }
}
















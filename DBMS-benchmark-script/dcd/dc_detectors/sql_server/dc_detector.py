import time
from pandas import DataFrame
from typing import Any
import urllib
from dcd.tools.log import *

from sqlalchemy import create_engine, text

from dcd.interfaces.dc import IDC
from dcd.interfaces.dc_detector import IDCDetector
from dcd.core.dc_detector_timelimit import DCDetectorFindViolationsTimeLimit
from dcd.sql.sql_builder import ISQLBuilder

class DCDetector(DCDetectorFindViolationsTimeLimit, IDCDetector):
  
  def __init__(self, sql_builder: ISQLBuilder) -> None:
      self.sql_builder = sql_builder
      
      server = 'localhost,5300'
      database = 'master'
      username = 'sa'
      password = 'Admin_P@ss'
      connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
      connection_uri = 'mssql+pyodbc:///?odbc_connect=' + urllib.parse.quote_plus(connection_string)
      self.engine = create_engine(connection_uri, fast_executemany=True)
      
      self.container_name = "sqlserver-container"
      
  def setup(self, df: DataFrame) -> float:
      log("(SQL Server)\t\tsetup and inserting data")
      
      table_name = 't'

      with self.engine.begin() as conn:
        df.iloc[0:0].to_sql(table_name, con=conn, if_exists='replace', index=False)
        
        chunk_size = 10000
        init_time = time.time()
        for i in range(0, len(df), chunk_size):
          chunk = df.iloc[i:i + chunk_size]
          chunk.to_sql(table_name, con=conn, if_exists='append', index=False)
          # conn.execute(text('COMMIT;'))
        end_time = time.time()
        
        insert_time = end_time - init_time
      return insert_time
    
  def destroy(self) -> None:
    with self.engine.begin() as conn:
      conn.execute(text('DROP TABLE IF EXISTS t;'))
  
  def get_exec_plan(self, dc: IDC) -> Any:
    
    query = self.sql_builder.build(dc)
    
    with self.engine.connect() as conn:
      conn.execute(text('SET SHOWPLAN_ALL ON'))
      result = conn.execute(text(query)).fetchall()
      conn.execute(text('SET SHOWPLAN_ALL OFF'))
      showplan_explain = '\n'.join(map(str, result))

    texts = [
      'Query:\t{}'.format(query),
      'Explain:\n{}'.format(showplan_explain)
    ]
      
    return '\n\n'.join(map(str, texts))
  
  def get_explain(self, dc: IDC) -> Any:
    query = self.sql_builder.build(dc)
    
    with self.engine.connect() as conn:
      conn.execute(text('SET SHOWPLAN_ALL ON'))
      result = conn.execute(text(query)).fetchall()
      conn.execute(text('SET SHOWPLAN_ALL OFF'))
      showplan_explain = '\n'.join(map(str, result))

    texts = [
      'Query:\t{}'.format(query),
      'Explain:\n{}'.format(showplan_explain)
    ]
      
    return '\n\n'.join(map(str, texts))
  
  def get_version(self) -> str:
    with self.engine.connect() as conn:
      result = conn.execute(text("SELECT @@VERSION;")).fetchone()
      return result[0]
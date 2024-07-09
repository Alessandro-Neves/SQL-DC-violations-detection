import time
from pandas import DataFrame
from typing import Any
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.exc import OperationalError
from dcd.tools.log import *
from dcd.interfaces.dc import IDC
from dcd.sql.sql_builder import ISQLBuilder
from dcd.interfaces.dc_detector import IDCDetector
from dcd.core.dc_detector_timelimit import DCDetectorFindViolationsTimeLimit

class DCDetector(DCDetectorFindViolationsTimeLimit, IDCDetector):
  
  def __init__(self, sql_builder: ISQLBuilder) -> None:
    self.sql_builder = sql_builder
    self.engine = create_engine("ibm_db_sa://db2inst1:password@localhost:5500/testdb")
    self.container_name = "db2-container"
    
  def _create_explain_tables(self):
      conn = self.engine.connect()
      try:
          conn.execute(text("CALL SYSPROC.SYSINSTALLOBJECTS('EXPLAIN', 'C', '', 'DB2INST1')"))
      except Exception as e:
          if "SQL0601N" in str(e):
              log("(Db2)\t\tExplain tables already exist, skipping creation.")
          else:
              log("(Db2)\t\tError creating explain tables: {}".format(e))
      finally:
          conn.close()
    
  def setup(self, df: DataFrame) -> float:
    table_name = 't'
    
    # Explanation: Sometimes DB2 takes a few seconds to correctly instantiate and start the database, 
    # in addition, sometimes it goes into backup restore mode, which also causes it to take a few more 
    # seconds to start, this routine just waits for these procedures finish.
    time_trying_conn = 0
    while True:
      try:
        with self.engine.begin() as conn:  
          log("(Db2)\t\tconnected to dbms")
          conn.execute(text("DROP TABLE IF EXISTS {}".format(table_name)))
        break

      except (OperationalError, Exception) as e:
        log("(Db2)\t\terror on connect to the database, trying again on 30 seconds ...")
        
        if time_trying_conn > 600:
          log("(Db2)\t\tcannot connect to the database")
          log("(Db2)\t\tOperationalError: {}".format(e))
          raise Exception(str(e))
        
        time.sleep(30)
        time_trying_conn += 30
      
    log("(Db2)\t\tsetup and inserting data")
    
    chunk_size = 10000
    replace = True
    with self.engine.begin() as conn:
      init_time = time.time()
      for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i + chunk_size]
        chunk.to_sql(table_name, con=conn, if_exists='replace' if replace else 'append', index=False)
        replace = False
      end_time = time.time()
    
    insert_time = end_time - init_time
    return insert_time
    
  def destroy(self) -> None:
    with self.engine.begin() as conn:
      conn.execute(text('DROP TABLE IF EXISTS t;'))
  
  def get_exec_plan(self, dc: IDC) -> Any:
    self._create_explain_tables()
    
    sql_query = self.sql_builder.build(dc)
    
    conn = self.engine.connect()
    try:
      conn.execute(text("EXPLAIN PLAN FOR {}".format(sql_query)))
      
      explain_statement_result = conn.execute(text("SELECT * FROM EXPLAIN_STATEMENT WHERE EXPLAIN_TIME = (SELECT MAX(EXPLAIN_TIME) FROM EXPLAIN_STATEMENT)")).fetchall()
      explain_operator_result = conn.execute(text("SELECT * FROM EXPLAIN_OPERATOR WHERE EXPLAIN_TIME = (SELECT MAX(EXPLAIN_TIME) FROM EXPLAIN_OPERATOR)")).fetchall()
      
      explain_statement_str = "\n".join(map(str, explain_statement_result))
      explain_operator_str = "\n".join(map(str, explain_operator_result))
    finally:
      conn.close()
    
    texts = [
      'Query:\t{}'.format(sql_query),
      'EXPLAIN STATEMENT:\n{}'.format(explain_statement_str),
      'EXPLAIN OPERATOR:\n{}'.format(explain_operator_str),
    ]
    
    return '\n\n'.join(texts)

  def get_explain(self, dc: IDC) -> Any:
    sql_query = self.sql_builder.build(dc)
    
    with self.engine.connect() as conn:
      exec_opts = {'execution_options': {'explain': True}}
      results = conn.execution_options(**exec_opts).execute(text(sql_query))
      plano_execucao_presumido = results.fetchall()
      return str(plano_execucao_presumido)
    
  def get_version(self) -> str:
    with self.engine.connect() as conn:
      result = conn.execute(text("SELECT service_level FROM TABLE (sysproc.env_get_inst_info()) AS t")).fetchone()
      return result[0]

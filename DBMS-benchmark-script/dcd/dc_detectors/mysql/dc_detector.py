import time
from pandas import DataFrame
from typing import Any
from sqlalchemy import create_engine, text
from dcd.tools.log import *

from dcd.interfaces.dc import IDC
from dcd.interfaces.dc_detector import IDCDetector
from dcd.core.dc_detector_timelimit import DCDetectorFindViolationsTimeLimit
from dcd.sql.sql_builder import ISQLBuilder

class DCDetector(DCDetectorFindViolationsTimeLimit , IDCDetector):
  def __init__(self, sql_builder: ISQLBuilder) -> None:
    self.sql_builder = sql_builder
    self.engine = create_engine("mysql+pymysql://root:root@localhost:5200/root")
    self.container_name = "mysql-container"
  
  def setup(self, df: DataFrame) -> float:
    log("(MySQL)\t\tsetup and inserting data")
    table_name = 't'
    
    with self.engine.begin() as conn:
      init_time = time.time()
      df.to_sql(table_name, con=conn, if_exists='replace', index=False)
      end_time = time.time()
        
      insert_time = end_time - init_time
    return insert_time

  def destroy(self) -> None:
    with self.engine.begin() as conn:
      conn.execute(text('DROP TABLE IF EXISTS t;'))


  def get_exec_plan(self, dc: IDC) -> Any:
    
    explain_str = self.get_explain(dc)
    
    sql_query = self.sql_builder.build(dc)
    
    with self.engine.connect() as conn:
      explain_analize_result = conn.execute(text("EXPLAIN ANALYZE {}".format(sql_query))).fetchall()
      explain_analize_str = "\n".join([r[0] for r in explain_analize_result])
    
    return '{}\n\nExec Plan:\n{}'.format(explain_str, explain_analize_str)
  
  def get_explain(self, dc: IDC) -> Any:
    sql_query = self.sql_builder.build(dc)
    
    with self.engine.connect() as conn:
      explain_result = conn.execute(text("EXPLAIN {}".format(sql_query))).fetchall()
      explain_str = "\n".join(map(str, explain_result))
    
    texts = [
      'Query:\t{}'.format(sql_query),
      'Explain:\n{}'.format(explain_str),
    ]
    
    return '\n\n'.join(map(str, texts))
  
  def get_version(self) -> str:
    with self.engine.connect() as conn:
      result = conn.execute(text("SELECT VERSION();")).fetchone()
      return result[0]
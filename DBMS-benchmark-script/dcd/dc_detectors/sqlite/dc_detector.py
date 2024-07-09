import time
from pandas import DataFrame
from typing import Any
from sqlalchemy import create_engine, text

from dcd.tools.log import *
from dcd.types.detection_result import DetectionResult
from dcd.interfaces.dc import IDC
from dcd.interfaces.dc_detector import IDCDetector
from dcd.sql.sql_builder import ISQLBuilder

class DCDetector(IDCDetector):
  def __init__(self, sql_builder: ISQLBuilder) -> None:
    self.sql_builder = sql_builder
    self.db_url = "sqlite:///./sqlite.db"
    self.engine = create_engine(self.db_url)
    
  def setup(self, df: DataFrame) -> float:
    log("(SQLite)\t\tsetup and inserting data")
    table_name = 't'
    
    with self.engine.begin() as conn:
      init_time = time.time()
      df.to_sql(table_name, con=conn, if_exists='replace', index=False)
      end_time = time.time()
      
      insert_time = end_time - init_time
      
    return insert_time
  
  def find_violations(self, dc: IDC) -> DetectionResult:
    with self.engine.connect() as conn:
      query = self.sql_builder.build(dc)
      
      init_time = time.time()
      result = conn.execute(text(query)).fetchall()
      end_time = time.time()

      search_time = end_time - init_time
      
      # log("[SQLite Search time]\t\t", search_time)
    
    return {
      "result": result,
      "search_time": search_time
    }
    
  def destroy(self) -> None:
    with self.engine.begin() as conn:
      conn.execute(text('DROP TABLE if exists t;'))
  
  def get_exec_plan(self, dc: IDC) -> Any:
    sql_query = self.sql_builder.build(dc)
    
    explain_str = self.get_explain(dc)
    
    with self.engine.begin() as conn:
      explain_query_plan_result = conn.execute(text("EXPLAIN QUERY PLAN {}".format(sql_query))).fetchall()
      explain_query_plan_str = "\n".join(map(str, explain_query_plan_result))
      
    return '{}\n\nExec Plan:\n{}'.format(explain_str, explain_query_plan_str)
    
  def get_explain(self, dc: IDC) -> Any:
    sql_query = self.sql_builder.build(dc)
    
    with self.engine.begin() as conn:
      explain_result = conn.execute(text("EXPLAIN {}".format(sql_query))).fetchall()
      explain_str = "\n".join(map(str, explain_result))
      
      texts = [
        'Query:\t{}'.format(sql_query),
        'Explain:\n{}'.format(explain_str)
      ]
      
      return '\n\n'.join(map(str, texts))
    
  def get_version(self) -> str:
    with self.engine.connect() as conn:
      result = conn.execute(text("SELECT sqlite_version();")).fetchone()
      return result[0]
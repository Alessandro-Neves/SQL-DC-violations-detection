import duckdb
import time
from pandas import DataFrame
from typing import Any
from dcd.tools.log import log

from dcd.types.detection_result import DetectionResult
from dcd.interfaces.dc import IDC
from dcd.interfaces.dc_detector import IDCDetector
from dcd.sql.sql_builder import ISQLBuilder

class DCDetector(IDCDetector):
  
  conn: Any = None
  
  def __init__(self, sql_builder: ISQLBuilder) -> None:
    self.sql_builder = sql_builder
    
    
  def setup(self, df: DataFrame) -> float:
    log("(DuckDB)\t\tsetup and inserting data")
    
    self.conn = duckdb.connect(database='duck.db')
    self.conn.execute("DROP TABLE IF EXISTS t")
    
    init_time = time.time()
    self.conn.execute("CREATE TABLE IF NOT EXISTS t AS SELECT * FROM df")
    end_time = time.time()
    
    insert_time = end_time - init_time
    
    return insert_time
  
  def find_violations(self, dc: IDC) -> DetectionResult: 
    if not self.sql_builder:
      raise Exception("DCDetector::find_violations:\nNone sql_builder")
    
    sql_query = self.sql_builder.build(dc)
    
    init_time = time.time()
    result = self.conn.execute(sql_query).fetchall()
    end_time = time.time()
    
    search_time = end_time - init_time
    
    return {
      "result": result,
      "search_time": search_time
    }
    
  def destroy(self) -> None:
    self.conn.execute("DROP TABLE IF EXISTS t")
    self.conn.close()
    
  def get_exec_plan(self, dc: IDC) -> Any:
    
    explain_str = self.get_explain(dc)
    
    sql_query = self.sql_builder.build(dc)
    
    explain_analize_result = self.conn.execute("EXPLAIN ANALYZE {}".format(sql_query)).fetchall()
    explain_analize_str = "\n".join([str(r[1]) for r in explain_analize_result])
    
    return '{}\n\nExec Plan:\n{}'.format(explain_str, explain_analize_str)
  
  def get_explain(self, dc: IDC) -> Any:
    sql_query = self.sql_builder.build(dc)
    
    explain_result = self.conn.execute("EXPLAIN {}".format(sql_query)).fetchall()
    explain_str = "\n".join([str(r[1]) for r in explain_result])
    
    texts = [
      'Query:\t{}'.format(sql_query),
      'Explain:\n{}'.format(explain_str),
    ]
    
    return '\n\n'.join(map(str, texts))
  
  def get_version(self) -> str:
    return "DuckDB Version: 0.8.1"
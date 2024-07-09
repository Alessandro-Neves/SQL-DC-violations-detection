import time
import numpy as np
import math
from pandas import DataFrame
from typing import Any
from sqlalchemy import create_engine, text
from dcd.tools.log import *
from dcd.interfaces.dc import IDC
from dcd.interfaces.dc_detector import IDCDetector
from dcd.core.dc_detector_timelimit import DCDetectorFindViolationsTimeLimit
from dcd.sql.sql_builder import ISQLBuilder

def convert_numpy_to_python(value):
  if '.' in str(value):
    return float(value)
  elif str(value) == 'nan':
    return 'NULL'
  return int(value)

class DCDetector(DCDetectorFindViolationsTimeLimit, IDCDetector):
  
  def __init__(self, sql_builder: ISQLBuilder) -> None:
    self.sql_builder = sql_builder
    self.db_url = "postgresql+psycopg2://postgres:postgres@localhost:5400/postgres"
    self.engine = create_engine(self.db_url)
    
    self.container_name = "umbra-container"
    
  def setup(self, df: DataFrame) -> float:
    log("(Umbra)\t\tsetup and inserting data") 
    
    table_name = 't'
    
    create_table_query = self._generate_create_table_sql(df, table_name)
    drop_table_query = "DROP TABLE IF EXISTS {}".format(table_name)
    
    conn = self.engine.connect()
    
    conn.execute(text(drop_table_query))
    conn.commit()
    
    conn.execute(text(create_table_query))
    conn.commit()
    
    chunk_size = 100
    num_records = len(df)
    
    df_columns = df.columns
    df_dtypes = df.dtypes
    
    init_time = time.time()
    for i in range(0, num_records, chunk_size):
      chunk = df.iloc[i:i + chunk_size].to_records(index=False)
      
      is_str_col = lambda col_idx: df_dtypes[df_columns[col_idx]] == 'object'
      convert = lambda x, use_as_string: "'{}'".format(str(x)) if use_as_string else str(convert_numpy_to_python(x))
      format_values = lambda t: "({})".format(', '.join([convert(value, is_str_col(col_idx)) for col_idx, value in enumerate(t)]))
      
      values_query = ",".join(format_values(t) for t in chunk)
      
      insert_data_query = "INSERT INTO {} VALUES {}".format(table_name, values_query)
        
      conn.execute(text(insert_data_query))
      
    conn.commit()
    end_time = time.time()
    
    conn.close()
    
    insert_time = end_time - init_time
    return insert_time
    
  def destroy(self) -> None:
    conn = self.engine.connect()
    conn.execute(text('DROP TABLE IF EXISTS t;'))
    conn.commit()
    conn.close()
  
  def get_exec_plan(self, dc: IDC) -> Any:
    
    explain_str = self.get_explain(dc)
    
    sql_query = self.sql_builder.build(dc)
    conn = self.engine.connect()
    
    explain_analize_result = conn.execute(text("EXPLAIN ANALYZE {}".format(sql_query))).fetchall()
    explain_analize_str = "\n".join([str(r[0]) for r in explain_analize_result])
    
    return '{}\n\nExec Plan:\n{}'.format(explain_str, explain_analize_str)
  
  def get_explain(self, dc: IDC) -> Any:
    sql_query = self.sql_builder.build(dc)
    conn = self.engine.connect()
    
    explain_result = conn.execute(text("EXPLAIN {}".format(sql_query))).fetchall()
    explain_str = "\n".join([str(r[0]) for r in explain_result])
    
    texts = [
      'Query:\t{}'.format(sql_query),
      'Explain:\n{}'.format(explain_str)
    ]
    
    return '\n\n'.join(map(str, texts))
  
  def _generate_create_table_sql(self, df, table_name):
    type_map = {
        'object': 'TEXT',
        'int': 'INT',
        'int8': 'INT',
        'int16': 'INT',
        'int32': 'INT',
        'int64': 'BIGINT',
        'float': 'FLOAT',
        'float32': 'FLOAT',
        'float64': 'DOUBLE PRECISION'
    }
    
    columns = []
    for column_name, column_type in zip(df.columns, df.dtypes):
        sql_type = type_map.get(str(column_type), "TEXT")
        columns.append("{} {}".format(column_name, sql_type))
    
    create_table_sql = f'''
        CREATE TABLE {table_name} (
            {', '.join(columns)}
        )
    '''
    
    return create_table_sql
  
  def get_version(self) -> str:
    with self.engine.connect() as conn:
      result = conn.execute(text("SELECT version();")).fetchone()
      return result[0]
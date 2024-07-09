import time
import threading
import subprocess
from sqlalchemy import text, Engine
from dcd.interfaces.dc import IDC
from dcd.sql.sql_builder import ISQLBuilder
from dcd.types.detection_result import DetectionResult
from dcd.tools.log import *

class DCDetectorFindViolationsTimeLimit():
  
  engine: Engine = None
  sql_builder: ISQLBuilder = None
  container_name: str = None
  
  def find_violations(self, dc: IDC) -> DetectionResult:
    
    if self.engine is None or self.sql_builder is None or self.container_name is None:
      raise Exception('DCDetectorFindViolationsTimeLimit::find_violations()::Exception::PropertiesNotInitialized')
    
    def thread_exec_query(engine: Engine, query: str, response_holder: list):
      try:
        conn = engine.connect()
  
        init_time = time.time()
        result = conn.execute(text(query)).fetchall()
        end_time = time.time()
        conn.close()
        
        search_time = end_time - init_time
        
        response_holder.append(result)
        response_holder.append(search_time)
      except Exception as e:
        response_holder.append(e)
        
    time_has_run_out = False
        
    query = self.sql_builder.build(dc)
    
    response_holder = []
    
    thread = threading.Thread(target=thread_exec_query, args=(self.engine, query, response_holder))
    thread.start()
    
    thread.join(4*60*60)

    if thread.is_alive():
      log('[TimeLimitToExecQuery] stopping database...')
      time_has_run_out = True
      try:
        subprocess.run("docker rm -f {}".format(self.container_name), shell=True, check=True)
      except subprocess.CalledProcessError as e:
        log(f"DCDetector::find_violations::subprocess.CalledProcessError: {e}")
        exit(0)
      
    thread.join()
    
    if isinstance(response_holder[0], Exception):
      if time_has_run_out:
        raise Exception('DCDetectorFindViolationsTimeLimit::find_violations()::Exception::TimeLimitToExecQuery')
      raise response_holder[0]
    
    return {
      'result': response_holder[0],
      'search_time': response_holder[1]
    }
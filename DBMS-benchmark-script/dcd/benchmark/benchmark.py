import time
import pandas as pd
import subprocess
from pandas import DataFrame
from typing import List
from dcd.interfaces.dc import IDC
from dcd.interfaces.dc_detector import IDCDetector
from dcd.tools.dataset_operations import DatasetOps
from dcd.tools.log import *

class Benchmark():    
  @staticmethod
  def run_benchmark(dc_detectors: List[IDCDetector], names: List[str], times: int, dc: IDC, noises_percentages: List[float], root_folder: str, query_type: str, docker=False) -> DataFrame:
    search_results_df = DataFrame(columns=["Engine"] + noises_percentages)
    insert_time_results_df = DataFrame(columns=["Engine", "Time"])
    
    if docker:
      Benchmark.restart_docker_databases()
    
    root_result_path = '{}/results/{}'.format(root_folder, query_type)
    open(root_result_path + '/log.txt', 'w')

    for i, dc_detector in enumerate(dc_detectors):
      engine = names[i]
      try:
        search_time_results = []
        gen_explain = True
        total_insert_time = 0.0

        for noisy_percentage in noises_percentages:
          log("\n(Running on {})\t{}%".format(names[i], noisy_percentage))
          
          df_address = "{}/data/{}.csv".format(root_folder, noisy_percentage)
          df_with_idx = DatasetOps.read_and_index_from_csv(df_address)
          
          insert_time = dc_detector.setup(df_with_idx)
          log("(Insert time)\t\t{:.6f}".format(insert_time))
          
          total_insert_time += insert_time
          
          if gen_explain:
            gen_explain = False
            explain_query_res = dc_detector.get_exec_plan(dc)
            write_on = '{}/Explain{}.txt'.format(root_result_path, names[i])
            with open(write_on, 'w') as f:
              f.write(explain_query_res)

          total_search_time = 0.0
          for itime in range(times):
            if itime == 0:
              # To disregard the first run
              res = dc_detector.find_violations(dc)
              log("(Warm-up run)\t\t{:.6f}".format(res['search_time']))

            detection_result = dc_detector.find_violations(dc)
            search_time = detection_result['search_time']
            results = detection_result['result']

            total_search_time += search_time
            result_snapshot = results if query_type in 'BF' else ''
                
            log("(Progress)\t\t{:.6f}\t\t{}\t\t{}".format(search_time, len(results), result_snapshot))
          
          dc_detector.destroy()
          search_average_time = round(float(total_search_time / times), 6)
          search_time_results.append(search_average_time)
          log("(Average search time)\t{}".format(search_average_time))
          
        average_insert_time = total_insert_time / len(noises_percentages)
        
        insert_time_results_df.loc[len(insert_time_results_df)] = (engine, round(average_insert_time, 6))
        search_results_df.loc[len(search_results_df)] = tuple([engine] + search_time_results)

        insert_time_results_df.to_csv('{}/results/{}/insert_times.csv'.format(root_folder, query_type), index=False)
        search_results_df.to_csv('{}/results/{}/search_times.csv'.format(root_folder, query_type), index=False)
        
      except Exception as e:
        log("(Exception): {}".format(str(e)))
        insert_time_results_df.loc[len(insert_time_results_df)] = (engine, None)
        search_results_df.loc[len(search_results_df)] = ([engine] + ([None] * len(noises_percentages)))
    
    with open('logs/log.txt', '+r') as fr:
      with open(root_result_path + '/log.txt', 'w') as fw:
        fw.write(fr.read())

  @staticmethod
  def restart_docker_databases():
    try:
      log("Stopping databases ...")
      subprocess.run("docker rm -f --volumes postgres-container mysql-container sqlserver-container umbra-container db2-container", shell=True, check=True)
      log("Wait")
      time.sleep(30)
      log("Starting databases ...")
      subprocess.run("docker-compose -f databases/compose-postgres.yml -f databases/compose-mysql.yml -f databases/compose-sqlserver.yml -f databases/compose-umbra.yml -f databases/compose-db2.yml up --remove-orphans -d", shell=True, check=True)
      log("Wait")
      time.sleep(120)
      try:
        log("Setting Umbra ...")
        subprocess.run("docker exec umbra-container psql -h /tmp -U postgres -c \"ALTER USER postgres WITH PASSWORD 'postgres'\"", shell=True, check=True)
      except Exception as e:
        log("Exception: {}".format(e))
        
      log('Wait')
      time.sleep(120)
      
    except subprocess.CalledProcessError as e:
      log("subprocess.CalledProcessError: {}".format(e))
from dcd.core.dc_reader import DCReader
from pipeline_config import datasets, benchmarks_to_run, is_on_docker
from dcd.benchmark.benchmark import Benchmark
from dcd.tools.log import log, open_log_files
      
for benchmark in benchmarks_to_run:
  names = [r[0] for r in benchmark['detectors']]
  detectors = [r[1] for r in benchmark['detectors']]
  query_type = benchmark['query_type']

  for dataset in datasets:
    open_log_files()
    root_folder = dataset['root_path']
    dc_file = root_folder + '/dc.dc'
    noises_percentages = dataset['noises_percentages']
    dc_detectors = [d for d in detectors]
    times = dataset['times']
    title = dataset['title']
    dc = DCReader(dc_file).pop_dc()

    log("[Benchmark {}]\n".format(title))
    log("[Running benchmark {}]".format(query_type))

    Benchmark.run_benchmark(
      dc_detectors, names, times, dc, noises_percentages, root_folder, query_type, is_on_docker
    )
    
    log("[End benchmark {}]\n\n".format(query_type))

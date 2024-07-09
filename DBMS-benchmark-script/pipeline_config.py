from options import Benchmark_A, Benchmark_B, Benchmark_C, Benchmark_D, Benchmark_E, Benchmark_F
from options import Lineitem_DC1_150k_Config, DOB_Job_DC1_2M_Config, Loan_Default_DC1_255k_Config
from options import Tax_DC1_1M_Config, Salaries_DC1_100k_Config, Salaries_DC2_100k_Config
from options import Measures_V2_DC1_Config, Yellow_Taxi_Trip_100k_config, Brasil_Exp_Comp_10mi_DC1_Config
from options import Flights_90k_DC1_Config, Scalability_Brasil_Exp_Comp_10mi_1perc_Config, Scalability_Salaries_100k_1perc_Config
from options import Test

datasets = [
  # Lineitem_DC1_150k_Config,
  # DOB_Job_DC1_2M_Config,
  # Loan_Default_DC1_255k_Config,
  # Tax_DC1_1M_Config,
  # Salaries_DC1_100k_Config,
  # Salaries_DC2_100k_Config,
  # Measures_V2_DC1_Config,
  # Yellow_Taxi_Trip_100k_config,
  # Brasil_Exp_Comp_10mi_DC1_Config,
  # Flights_90k_DC1_Config,
  # Scalability_Brasil_Exp_Comp_10mi_1perc_Config,
  # Scalability_Brasil_Exp_Comp_10mi_1perc_Config,
  Test
]

benchmarks_to_run = [
  Benchmark_A,
  Benchmark_B,
  Benchmark_C,
  Benchmark_D,
  Benchmark_E,
  Benchmark_F
]

is_on_docker=False
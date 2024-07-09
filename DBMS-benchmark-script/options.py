from dcd.sql.tuple_pairs_limit_builder import TuplePairsLimitSQLBuilder, TuplePairsLimitSQLServerSQLBuilder
from dcd.sql.tuple_pairs_builder import TuplePairsSQLBuilder, TuplePairsSQLBuilderWithGroupBy
from dcd.sql.qtd_violations_builder import QtdVioSQLBuilder
from dcd.sql.tuples_on_some_violation import TuplesOnSomeViolationSQLBuilder, TuplesOnSomeViolationSQLBuilderWithExists
from dcd.dc_detectors.duck.dc_detector import DCDetector as DuckDCDetector
from dcd.dc_detectors.postgres.dc_detector import DCDetector as PostgresDCDetector
from dcd.dc_detectors.sqlite.dc_detector import DCDetector as SQLiteDCDetector
from dcd.dc_detectors.mysql.dc_detector import DCDetector as MysqlDCDetector
from dcd.dc_detectors.sql_server.dc_detector import DCDetector as SQLServerDCDetector
from dcd.dc_detectors.db2.dc_detector import DCDetector as Db2DCDetector
from dcd.dc_detectors.umbra.dc_detector import DCDetector as UmbraDCDetector

def create_dc_detectors(rdbms_list, sql_builder):
  return [[name, detector(sql_builder)] for name, detector in rdbms_list]

DuckDB =        ("DuckDB", DuckDCDetector)
SQLServer =     ("SQL Server", SQLServerDCDetector)
Umbra =         ("Umbra", UmbraDCDetector)
PostgreSQL =    ("PostgreSQL", PostgresDCDetector)
MySQL =         ("MySQL", MysqlDCDetector)
Db2 =           ("Db2", Db2DCDetector)
SQLite =        ("SQLite", SQLiteDCDetector)

DBMSs = [
  DuckDB,
  # SQLServer,
  # Umbra,
  # PostgreSQL,
  # MySQL,
  # Db2,
  SQLite
]

Benchmark_A = {
  'query_type': 'A',
  'detectors': create_dc_detectors(DBMSs, TuplePairsSQLBuilder())
}

Benchmark_B = {
  'query_type': 'B',
  'detectors': create_dc_detectors(DBMSs, QtdVioSQLBuilder())
}

Benchmark_C = {
  'query_type': 'C',
  'detectors': create_dc_detectors(DBMSs, TuplePairsSQLBuilderWithGroupBy())
}

Benchmark_D = {
  'query_type': 'D',
  'detectors': create_dc_detectors(DBMSs, TuplesOnSomeViolationSQLBuilder())
}

Benchmark_E = {
  'query_type': 'E',
  'detectors': create_dc_detectors(DBMSs, TuplesOnSomeViolationSQLBuilderWithExists())
}

Benchmark_F = {
  'query_type': 'F',
  'detectors': [
    ['DuckDB', DuckDCDetector(TuplePairsLimitSQLBuilder())],
    # ['SQL Server', SQLServerDCDetector(TuplePairsLimitSQLServerSQLBuilder())],
    # ['Umbra', UmbraDCDetector(TuplePairsLimitSQLBuilder())],
    # ['PostgreSQL', PostgresDCDetector(TuplePairsLimitSQLBuilder())],
    # ['MySQL', MysqlDCDetector(TuplePairsLimitSQLBuilder())],
    # ['Db2', Db2DCDetector(TuplePairsLimitSQLBuilder())],
    ['SQLite', SQLiteDCDetector(TuplePairsLimitSQLBuilder())],
  ]
}

DOB_Job_DC1_2M_Config = {
  'title': 'DOB Job 2.7mi- DC1',
  'times': 3,
  'noises_percentages': [0, 0.1, 1, 5, 10, 30],
  'root_path': 'benchmark/testdatas/DOB_job/dc1'
}

Lineitem_DC1_150k_Config = {
  'title': 'Lineitem 150k - DC1',
  'times': 3,
  'noises_percentages': [0, 0.1, 1, 5, 10, 30],
  'root_path': 'benchmark/testdatas/lineitem/dc1'
}

Loan_Default_DC1_255k_Config = {
  'title': 'Loan Def 255k - DC1',
  'times': 3,
  'noises_percentages': [0, 0.1, 1, 5, 10, 30],
  'root_path': 'benchmark/testdatas/loan_default/dc1'
}

Salaries_DC1_100k_Config = {
  'title': 'Salaries 100k - DC1',
  'times': 3,
  'noises_percentages': [0, 0.1, 1, 5, 10, 30],
  'root_path': 'benchmark/testdatas/salaries/dc1'
}

Salaries_DC2_100k_Config = {
  'title': 'Salaries 100k - DC2',
  'times': 3,
  'noises_percentages': [0, 0.1, 1, 5, 10, 30],
  'root_path': 'benchmark/testdatas/salaries/dc2'
}

Tax_DC1_1M_Config = {
  'title': 'Tax 1mi - DC1',
  'times': 3,
  'noises_percentages': [0, 0.1, 1, 5, 10, 30],
  'root_path': 'benchmark/testdatas/tax/dc1'
}

Measures_V2_DC1_Config = {
  'title': 'Measures V2 1.3mi - DC1',
  'times': 3,
  'noises_percentages': [0, 0.1, 1, 5, 10, 30],
  'root_path': 'benchmark/testdatas/measures_v2/dc1'
}

Flights_90k_DC1_Config = {
  'title': 'Flights 90k - DC1',
  'times': 3,
  'noises_percentages': [0, 0.1, 1, 5, 10, 30],
  'root_path': 'benchmark/testdatas/flights/dc1'
}

Brasil_Exp_Comp_10mi_DC1_Config = {
  'title': 'Brasil Exp Completo 10mi - DC1',
  'times': 3,
  'noises_percentages': [0, 0.1, 1, 5],
  'root_path': 'benchmark/testdatas/brasil_exp_comp_10mi/dc1'
}

Yellow_Taxi_Trip_100k_config = {
  'title': 'Yellow Taxi Pickup Dropoff 100K - DC1',
  'times': 3,
  'noises_percentages': [0, 0.1, 1, 5, 10, 30],
  'root_path': 'benchmark/testdatas/2018_yellow_taxi_trip_pickup_dropoff_100K/dc1'
}

Scalability_Brasil_Exp_Comp_10mi_1perc_Config = {
  'title': 'Brasil Exp Completo 10mi Scalability - DC1',
  'times': 3,
  'noises_percentages': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
  'root_path': 'benchmark/testdatas/brasil_exp_comp_scalability/1%'
}

Scalability_Salaries_100k_1perc_Config = {
  'title': 'Salaries 100k Scalability - DC1',
  'times': 3,
  'noises_percentages': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
  'root_path': 'benchmark/testdatas/salaries/dc1/1%'
}

Test = {
  'title': 'Test - DC1',
  'times': 3,
  'noises_percentages': [0, 1, 5, 10],
  'root_path': 'benchmark/testdatas/test/dc1'
}
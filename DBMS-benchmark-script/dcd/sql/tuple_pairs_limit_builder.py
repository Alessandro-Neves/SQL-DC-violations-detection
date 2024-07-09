from dcd.sql.sql_builder import ISQLBuilder
from dcd.interfaces.dc import IDC, string_predicates

class TuplePairsLimitSQLBuilder(ISQLBuilder):
  
  def build(self, dc: IDC) -> str:
    """
    SELECT t1.id , t2.id
    FROM T t1
    JOIN T t2 ON { predicates } LIMIT 1;
    """

    predicates = string_predicates(dc)
    return "SELECT t1.tid as id1, t2.tid as id2 FROM t t1 JOIN t t2 ON " + predicates + " AND t1.tid <> t2.tid LIMIT 1;"
  
class TuplePairsLimitSQLServerSQLBuilder(ISQLBuilder):
  
  def build(self, dc: IDC) -> str:
    """
    SELECT TOP 1 t1.id , t2.id
    FROM T t1
    JOIN T t2 ON { predicates };
    """

    predicates = string_predicates(dc)
    sql_query = "SELECT TOP 1 t1.tid as id1, t2.tid as id2 FROM t t1 JOIN t t2 ON " + predicates + " AND t1.tid <> t2.tid;"
    return sql_query
from dcd.sql.sql_builder import ISQLBuilder
from dcd.interfaces.dc import IDC, string_predicates

class QtdVioSQLBuilder(ISQLBuilder):
  def build(self, dc: IDC) -> str:
    """
    SELECT COUNT(*)
    FROM T t1 
    JOIN T t2 ON { predicates };
    """
    
    predicates = string_predicates(dc)
    return "SELECT COUNT(*) FROM t t1 JOIN t t2 ON " + predicates + " AND t1.tid <> t2.tid;"
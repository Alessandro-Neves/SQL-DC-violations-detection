from dcd.sql.sql_builder import ISQLBuilder
from dcd.interfaces.dc import IDC, string_predicates, string_pred_collumns

class TuplePairsSQLBuilder(ISQLBuilder):
  
  def build(self, dc: IDC) -> str:
    """
    SELECT t1.id , t2.id
    FROM T t1
    JOIN T t2 ON { predicates };
    """

    predicates = string_predicates(dc)
    return "SELECT t1.tid as id1, t2.tid as id2 FROM t t1 JOIN t t2 ON " + predicates + " AND t1.tid <> t2.tid;"

  
    
    
class TuplePairsSQLBuilderWithGroupBy(ISQLBuilder):
  
  def build(self, dc: IDC) -> str:
    """
    SELECT t1.tid, t2.tid FROM T t1, T t2 
    GROUP BY { t1.columns, t2.columns } 
    HAVING { predicates }
    """
    """
    Example:
    SELECT t1.tid, t2.tid FROM T t1, T t2 
    GROUP BY t1.tid, t2.tid, t1.job, t2.job, t1.borough, t2.borough, t1.lot, t2.lot 
    HAVING t1.job = t2.job AND t1.borough <> t2.borough AND t1.lot > t2.lot AND t1.tid <> t2.tid
    """

    predicates = string_predicates(dc)
    columns = string_pred_collumns(dc)
    
    sql_query =   "SELECT t1.tid as id1, t2.tid as id2 FROM t t1, t t2 "
    sql_query +=  "GROUP BY t1.tid, t2.tid, " + columns + " HAVING " + predicates + " AND t1.tid <> t2.tid;"
    return sql_query
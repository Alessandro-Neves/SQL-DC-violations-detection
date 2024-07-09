from dcd.sql.sql_builder import ISQLBuilder
from dcd.interfaces.dc import IDC, string_predicates

class TuplesOnSomeViolationSQLBuilder(ISQLBuilder):
  def build(self, dc: IDC) -> str:
    """
    SELECT t1.id FROM T t1 
    JOIN T t2 
      ON { predicates }
    UNION
    SELECT t2.id FROM T t1 
    JOIN T t2 
      ON { predicates };
    """

    predicates = string_predicates(dc)
    sql = "SELECT t1.tid FROM t t1 JOIN t t2 ON " + predicates + " AND t1.tid <> t2.tid "
    sql += "UNION SELECT t2.tid FROM t t1 JOIN t t2 ON " + predicates + " AND t1.tid <> t2.tid;"
    return sql

class TuplesOnSomeViolationSQLBuilderWithExists(ISQLBuilder):
  def build(self, dc: IDC) -> str:    
    """
    SELECT t1.id FROM T t1 
    WHERE EXISTS (
      SELECT 1 FROM T t2
      WHERE { predicates }
    )
    UNION
    SELECT t2.id FROM T t2 
    WHERE EXISTS (
      SELECT 1 FROM T t1
      WHERE { predicates }
    );
    """
    
    predicates = string_predicates(dc)
    sql = "SELECT t1.tid FROM t t1 WHERE EXISTS ( SELECT 1 FROM t t2 WHERE "
    sql += predicates + " AND t1.tid <> t2.tid) "
    sql += "UNION SELECT t2.tid FROM t t2 WHERE EXISTS ( SELECT 1 FROM t t1 WHERE "
    sql += predicates + " AND t1.tid <> t2.tid) "
    return sql
  
  
class TestSQLBuilderWithExists(ISQLBuilder):
  def build(self, dc: IDC) -> str:    
    """
    SELECT t1.id FROM T t1 
    WHERE EXISTS (
      SELECT 1 FROM T t2
      WHERE { predicates }
    );
    """

    predicates = string_predicates(dc)
    sql = "SELECT t1.tid FROM t t1 WHERE EXISTS ( SELECT 1 FROM t t2 WHERE "
    sql += predicates + " AND t1.tid <> t2.tid);"
    return sql
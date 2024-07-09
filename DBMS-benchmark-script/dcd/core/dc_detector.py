from pandas import DataFrame
import copy
from typing import List
from functools import reduce

from dcd.interfaces.dc import IDC
from dcd.interfaces.dc_detector import IDCDetector
from dcd.types.predicate import Predicate, PREDICATE_OPERATOR
from dcd.types.common import PairIdList


class DCDetector(IDCDetector):
  
  def find_violations(self, df: DataFrame, dc: IDC) -> PairIdList:    
    violations = DataFrame()
    
    df2 = df
    tuples_qtd = df2.shape[0]
    df2['targets'] = [[] for _ in range(tuples_qtd)]
    
    scalar_predicates = list(filter(lambda p: not p.is_relational, dc.get_predicates()))
    relational_predicates = [p for p in dc.get_predicates() if p not in scalar_predicates]
    
    if bool(scalar_predicates):
      violations = self.filter_by_scalar_predicates(df, scalar_predicates)
    
    if bool(relational_predicates):
      same_targets_rps = list(filter(lambda p: not p.has_diff_target, relational_predicates))
      diff_targets_rps = [p for p in relational_predicates if p not in same_targets_rps]
      
      targets = violations if bool(scalar_predicates) else df2
      
      if bool(same_targets_rps):
        violations = self.filter_by_same_target_predicates(targets, df, same_targets_rps)
        targets = violations
        
      if bool(diff_targets_rps):
        violations = self.filter_by_diff_target_predicates(targets, df, diff_targets_rps)
        
    adjacency_list = [(int(t['tid']), t['targets']) for i , t in violations.iterrows()] # type: ignore
    
    adjacency_list_with_some = list(filter(lambda t: bool(t[1]), adjacency_list))  # type: ignore
    
    pairs = []
    for t in adjacency_list_with_some:
      t1 = t[0]
      for t2 in t[1]:
        pairs.append(tuple((t1, t2))) # type: ignore
    return pairs
          
  def filter_by_scalar_predicates(self, df: DataFrame, scalar_predicates: List[Predicate]) -> DataFrame:
    if not bool(scalar_predicates):
      raise Exception("DCDetector::filter_by_scalar_predicates:\nempty scalar_predicates list")
    
    operators_fn = {
      PREDICATE_OPERATOR.GT: lambda df, col, scalar: df[col] > scalar,
      PREDICATE_OPERATOR.LT: lambda df, col, scalar: df[col] < scalar,
      PREDICATE_OPERATOR.EQ: lambda df, col, scalar: df[col] == scalar,
      PREDICATE_OPERATOR.GTE: lambda df, col, scalar: df[col] >= scalar,
      PREDICATE_OPERATOR.LTE: lambda df, col, scalar: df[col] <= scalar,
      PREDICATE_OPERATOR.IQ: lambda df, col, scalar: df[col] != scalar,
    }
    
    for sp in scalar_predicates:
      if sp.left_side.is_scalar_value or not sp.right_side.is_scalar_value:
        raise Exception(f"DCDetector::filter_by_scalar_predicates:\nunexpected scalar predicate\nparam: {sp}")
    
    conditions = [ operators_fn[sp.operator]
                  (df, sp.left_side.col_name_or_value, sp.right_side.col_name_or_value) 
                  for sp in scalar_predicates]
    
    res = df[reduce(lambda x, y: x & y, conditions)]
    
    for i, line in res.iterrows():
      res.at[i, 'targets'].append(int(line['tid']))
      
    return res
  
  def filter_by_diff_target_predicates(self, targets: DataFrame, df: DataFrame, rel_predicates: List[Predicate]) -> DataFrame:
    
    operators_fn = {
      PREDICATE_OPERATOR.GT: lambda scalar, df, col: scalar > df[col],
      PREDICATE_OPERATOR.LT: lambda scalar, df, col: scalar < df[col],
      PREDICATE_OPERATOR.EQ: lambda scalar, df, col: scalar == df[col],
      PREDICATE_OPERATOR.GTE: lambda scalar, df, col: scalar >= df[col],
      PREDICATE_OPERATOR.LTE: lambda scalar, df, col: scalar <= df[col],
      PREDICATE_OPERATOR.IQ: lambda scalar, df, col: scalar != df[col],
    }
    
    for i, t in targets.iterrows():
      conditions = [ operators_fn[rp.operator]
                  (t[rp.left_side.col_name_or_value], df, rp.right_side.col_name_or_value) 
                  for rp in rel_predicates]
      
      conditions.append(df['tid'] != t['tid'])
      
      violations_ids = df[reduce(lambda x, y: x & y, conditions)]['tid'].to_list()
      
      if len(violations_ids) > 0:
        targets.at[i, 'targets'].extend(violations_ids)
      else:
        targets.at[i, 'targets'] = []
              
    return targets
  
  def filter_by_same_target_predicates(self, targets: DataFrame, df: DataFrame, rel_predicates: List[Predicate]) -> DataFrame:
    operators_fn = {
      PREDICATE_OPERATOR.GT: lambda col_a, df, col_b: df[col_a] > df[col_b],
      PREDICATE_OPERATOR.LT: lambda col_a, df, col_b: df[col_a] < df[col_b],
      PREDICATE_OPERATOR.EQ: lambda col_a, df, col_b: df[col_a] == df[col_b],
      PREDICATE_OPERATOR.GTE: lambda col_a, df, col_b: df[col_a] >= df[col_b],
      PREDICATE_OPERATOR.LTE: lambda col_a, df, col_b: df[col_a] <= df[col_b],
      PREDICATE_OPERATOR.IQ: lambda col_a, df, col_b: df[col_a] != df[col_b],
    }
    
    conditions = [ operators_fn[rp.operator]
                (rp.left_side.col_name_or_value, df, rp.right_side.col_name_or_value) 
                for rp in rel_predicates]
    
    conditions.append(df['tid'].isin(targets['tid']))
    
    res = df[reduce(lambda x, y: x & y, conditions)]
        
    for i, line in res.iterrows():
      res.at[i, 'targets'].append(int(line['tid']))
      
    return res
from abc import ABC, abstractmethod
from typing import List

from dcd.types.predicate import Predicate

class IDC(ABC):  
  @abstractmethod
  def get_predicates(self) -> List[Predicate]:
    raise NotImplementedError
  
def string_predicates(dc: IDC) -> str:
  """
  P1 AND ... AND Pm
  """
  scalar_predicates = list(filter(lambda p: not p.is_relational, dc.get_predicates()))
  relational_predicates = [p for p in dc.get_predicates() if p not in scalar_predicates]
  
  same_targets_rps = list(filter(lambda p: not p.has_diff_target, relational_predicates))
  diff_targets_rps = [p for p in relational_predicates if p not in same_targets_rps]
  
  if scalar_predicates or same_targets_rps:
    raise Exception("string_predicates::build:Don't support same targets or scalar predicates yet")
  
  if not bool(diff_targets_rps):
    raise Exception("string_predicates::build:Need at least one diff target predicate") 
  
  str_predicates = " AND ".join([f"t1.{rps.left_side.col_name_or_value} {rps.operator.value} t2.{rps.right_side.col_name_or_value}" for i, rps in enumerate(diff_targets_rps)])
  return str_predicates

def string_pred_collumns(dc: IDC) -> str:
  scalar_predicates = list(filter(lambda p: not p.is_relational, dc.get_predicates()))
  relational_predicates = [p for p in dc.get_predicates() if p not in scalar_predicates]
  
  same_targets_rps = list(filter(lambda p: not p.has_diff_target, relational_predicates))
  diff_targets_rps = [p for p in relational_predicates if p not in same_targets_rps]
  
  if scalar_predicates or same_targets_rps:
    raise Exception("string_pred_collumns::build:Don't support same targets or scalar predicates yet")
  
  if not bool(diff_targets_rps):
    raise Exception("string_pred_collumns::build:Need at least one diff target predicate")
  
  return ', '.join(['t1.{}, t2.{}'.format(rps.left_side.col_name_or_value, rps.right_side.col_name_or_value) for rps in diff_targets_rps])
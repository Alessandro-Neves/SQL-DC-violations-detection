import re
from typing import List

from dcd.types.predicate import Predicate, PredicateComponent, get_PREDICATE_OPERATOR_by_key
from dcd.interfaces.dc import IDC

class DC(IDC):
  predicates: List[Predicate]
  
  def __init__(self, str_predicates: List[str]) -> None:
    self.predicates = []

    for str_cs in str_predicates:
      splitted_comps = str_cs.split(' ')

      if operator := get_PREDICATE_OPERATOR_by_key(splitted_comps[1]):    
        p_left_side = PredicateComponent (
        is_scalar_value = self._is_scalar(splitted_comps[0]),
        col_name_or_value = self._get_col_name_or_scalar_value(splitted_comps[0])
        )
        
        p_right_side = PredicateComponent (
          is_scalar_value = self._is_scalar(splitted_comps[2]),
          col_name_or_value = self._get_col_name_or_scalar_value(splitted_comps[2])
        )
        
        is_relational = not p_left_side.is_scalar_value and not p_right_side.is_scalar_value
        has_diff_target = not (self._has_t1(splitted_comps[0]) and self._has_t1(splitted_comps[2])) if is_relational else False
        
        predicate = Predicate(p_left_side, operator, p_right_side, is_relational, has_diff_target)
        self.predicates.append(predicate)
      else:
        raise Exception(f"DC::__init__:\nunexpected None value on predicate operator\nparam: {splitted_comps[1]}")
    
  def get_predicates(self) -> List[Predicate]:
    return self.predicates
  
  def _is_scalar(self, str):
    pattern = r'^t[12]\..*'
    return not bool(re.match(pattern, str))
  
  def _has_t1(self, str):
    pattern = r'^t1\..*'
    return bool(re.match(pattern, str))
  
  def _to_number_else_str(self, input_string):
    if input_string.isdigit() or (input_string[0] == '-' and input_string[1:].isdigit()):
        return int(input_string)
    else:
        return input_string
      
  def _get_col_name(self, str):
    pattern = r'^(t[12]\..*)$'
    return match[0][3:] if (match := re.match(pattern, str)) else None
      
  def _get_col_name_or_scalar_value(self, str):
    if self._is_scalar(str):
      return self._to_number_else_str(str)

    if col_name := self._get_col_name(str):
      return col_name
    else:
      raise Exception(f"DC::_get_col_name_or_scalar_value:\nreturned unexpected None value\nparam: {str}")
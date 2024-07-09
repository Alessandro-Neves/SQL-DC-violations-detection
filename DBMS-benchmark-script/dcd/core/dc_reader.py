from dcd.types.predicate import Constraint
from dcd.interfaces.dc_reader import IDCReader
from dcd.core.dc import DC
from typing import List

class DCReader(IDCReader):
  _dc: List[DC]
  
  def __init__(self, constraints_file_path) -> None:
    
    with open(constraints_file_path, 'r') as file:
      lines = file.readlines()

    self._dc = []
    for line in lines:
      line = line.strip()
      constraints = line.split(',')
      dc = DC(constraints)
      self._dc.append(dc)
      
  def get_dcs(self) -> List[DC]:
    return self._dc
  
  def pop_dc(self) -> DC:
    return self._dc.pop(0)
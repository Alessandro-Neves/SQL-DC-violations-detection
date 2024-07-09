from abc import ABC, abstractmethod
from typing import List
from dcd.types.predicate import Constraint
from dcd.interfaces.dc import IDC

class IDCReader(ABC):
  @abstractmethod
  def __init__(self, constraints_file_path) -> None:
    raise NotImplementedError
  
  @abstractmethod
  def get_dcs(self) -> List[IDC]:
    raise NotImplementedError
  
  @abstractmethod
  def pop_dc(self) -> IDC:
    raise NotImplementedError
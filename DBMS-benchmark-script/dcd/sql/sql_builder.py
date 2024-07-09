from abc import ABC, abstractmethod
from dcd.interfaces.dc import IDC

class ISQLBuilder(ABC):
  
  @abstractmethod
  def build(self, dc: IDC, tag: str = None) -> str:
    raise NotImplementedError
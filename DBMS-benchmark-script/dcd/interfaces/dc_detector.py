from abc import ABC, abstractmethod
from pandas import DataFrame
from typing import Any
from dcd.interfaces.dc import IDC
from dcd.types.detection_result import DetectionResult

class IDCDetector(ABC):
  @abstractmethod
  def setup(self, df: DataFrame) -> float:
    raise NotImplementedError

  @abstractmethod
  def find_violations(self, df: DataFrame, dc: IDC) -> DetectionResult:
    raise NotImplementedError
  
  @abstractmethod
  def destroy(self) -> None:
    raise NotImplementedError
  
  @abstractmethod
  def get_exec_plan(self, dc: IDC) -> Any:
    raise NotImplementedError
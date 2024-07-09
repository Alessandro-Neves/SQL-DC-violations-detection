from pandas import read_csv, DataFrame
from typing import List

from dcd.interfaces.dc_reader import IDCReader
from dcd.interfaces.dc_detector import IDCDetector
from dcd.interfaces.dc import IDC

class DatasetOps():
  @staticmethod
  def read_and_index_from_csv(csv_address: str) -> DataFrame:
    df = read_csv(csv_address, low_memory=False)
    
    colunas_object = df.select_dtypes(include='object').columns.tolist()
    df[colunas_object] = df[colunas_object].astype(str)
    
    df_with_index = df.copy()
    if 'tid' in df_with_index.columns:
      df_with_index = df_with_index.drop('tid', axis=1)
      
    df_with_index.insert(0, 'tid', df_with_index.index)
    return df_with_index
  
  @staticmethod
  def is_clean_dataset(df: DataFrame, dc_reader: IDCReader, dc_detector: IDCDetector) -> bool:
    dfc = df.copy()
    dcs = dc_reader.get_dcs()
    return not any(bool(dc_detector.find_violations(dfc, dc)) for dc in dcs)
  
  @staticmethod
  def clean_dataset(df: DataFrame, dc_reader: IDCReader, dc_detector: IDCDetector) -> DataFrame:
    df.insert(0, 'tid', df.index)
    
    dcs = dc_reader.get_dcs()
    
    for dc in dcs:
      violations = dc_detector.find_violations(df, dc)
      
      ids = [id for tupla in violations for id in tupla]
      
      ids_to_rm = list(set(ids))
      
      for i, id_index in enumerate(ids_to_rm):
        df.drop(id_index, inplace=True)
          
    return df.drop('tid', axis=1)
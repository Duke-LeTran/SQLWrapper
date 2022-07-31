import pandas as pd
from sqlalchemy.dialects.oracle import NUMBER, VARCHAR2, DATE
#from typing import Union

def max_len_cols(df_input:pd.DataFrame, method='default', *args,  **kwargs):
    """
    Manages calling the two functions:
    * max_lens_cols_oracle - returns with Oracle datatypes
    * max_lens_cols_default - returns max counts of columns
    """
    if method == 'oracle':
        return max_len_cols_oracle(df_input, *args, **kwargs)
    else:
        return max_len_cols_default(df_input, *args, **kwargs)

def max_len_cols_default(df_input:pd.DataFrame) -> dict:
    """returns a dict of max count of each column in pd.DataFrame"""
    max_len = {}
    df_input = df_input.fillna('')
    for col in df_input.columns:
        try:
            max_len[col.upper()] = int(df_input[col].str.len().max())
        except AttributeError as error:
            max_len[col] = df_input[col].dtype
    return max_len

def max_len_cols_oracle(df_input:pd.DataFrame, factor=1) -> dict:
    """returns datatype with ORACLE NUMBER TYPE"""
    max_len = {}
    for col in df_input.columns:
        try:
            if df_input[col].dtype.name is 'bool':
                max_len[col] = NUMBER(1,0)
            else:
                max_len[col.upper()] = df_input[col].str.len().max()
        except AttributeError as error:
            if 'date' in col.lower():
                max_len[col.upper()] = 'date'
            print(error)
            print(col)
    #  setting datatypes
    result_dict = {}
    for col, dtype in max_len.items():
        try:
            if 'date' in col.lower():
                result_dict[col] = DATE
            elif type(dtype) == NUMBER:
                result_dict[col.upper()] = dtype
            else:
                result_dict[col] = VARCHAR2(int(int(dtype)* factor))
        except:
            print(col, dtype)
            result_dict[col] = VARCHAR2(100)
    return result_dict



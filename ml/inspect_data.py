import json
import os
import pandas as pd

def inspect_notebook():
    nb_path = 'ml/kernel-BMI-prediction of health status(1).ipynb'
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    print("=== NOTEBOOK CELLS ===")
    for i, cell in enumerate(nb['cells']):
        cell_type = cell['cell_type']
        source = "".join(cell.get('source', []))
        first_line = source.strip().split('\n')[0] if source.strip() else '<empty>'
        print(f"[{i}] {cell_type}: {first_line[:80]}")

def inspect_datasets():
    csv1_path = 'ml/500_Person_Gender_Height_Weight_Index.csv'
    csv2_path = 'ml/ObesityDataSet_raw_and_data_sinthetic.csv'

    print("\n=== DATASET 1: 500_Person_Gender_Height_Weight_Index.csv ===")
    df1 = pd.read_csv(csv1_path)
    print(f"Shape: {df1.shape}")
    print("Columns and types:")
    print(df1.dtypes)
    print("\nMissing values:")
    print(df1.isnull().sum())
    print("\nDuplicate rows:", df1.duplicated().sum())
    print("\nHead:")
    print(df1.head())
    print("\nIndex class distribution:")
    print(df1['Index'].value_counts().sort_index())
    print("\nStats:")
    print(df1.describe())

    print("\n=== DATASET 2: ObesityDataSet_raw_and_data_sinthetic.csv ===")
    df2 = pd.read_csv(csv2_path)
    print(f"Shape: {df2.shape}")
    print("Columns and types:")
    print(df2.dtypes)
    print("\nMissing values:")
    print(df2.isnull().sum())
    print("\nDuplicate rows:", df2.duplicated().sum())
    print("\nHead:")
    print(df2.head())
    print("\nTarget column distribution:")
    # Find categorical columns that might be target
    target_col = df2.columns[-1]
    print(f"Target col: {target_col}")
    print(df2[target_col].value_counts())
    print("\nUnique values in categorical columns:")
    for col in df2.select_dtypes(include=['object']).columns:
        print(f"  {col}: {df2[col].unique().tolist()}")

if __name__ == '__main__':
    inspect_notebook()
    inspect_datasets()

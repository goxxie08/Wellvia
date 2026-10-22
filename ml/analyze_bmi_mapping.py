import pandas as pd
import numpy as np

# Load datasets
df1 = pd.read_csv('ml/500_Person_Gender_Height_Weight_Index.csv')
df2 = pd.read_csv('ml/ObesityDataSet_raw_and_data_sinthetic.csv')

print("--- DATASET 1 BMI ANALYSIS ---")
# Calculate BMI from df1
# Height is in cm, Weight in kg
df1['calculated_bmi'] = df1['Weight'] / ((df1['Height'] / 100.0) ** 2)

for idx in sorted(df1['Index'].unique()):
    subset = df1[df1['Index'] == idx]
    print(f"Index {idx}: N={len(subset)}, BMI min={subset['calculated_bmi'].min():.2f}, max={subset['calculated_bmi'].max():.2f}, mean={subset['calculated_bmi'].mean():.2f}")

print("\n--- DATASET 2 BMI ANALYSIS ---")
# In df2, Height is in meters, Weight is in kg
df2['calculated_bmi'] = df2['Weight'] / (df2['Height'] ** 2)
for label in df2['NObeyesdad'].unique():
    subset = df2[df2['NObeyesdad'] == label]
    print(f"Label {label}: N={len(subset)}, BMI min={subset['calculated_bmi'].min():.2f}, max={subset['calculated_bmi'].max():.2f}, mean={subset['calculated_bmi'].mean():.2f}")

print("\n--- SYNTHETIC SAMPLES IN DATASET 2 ---")
# In dataset 2, synthetic samples have fractional Age, FCVC, NCP, CH2O, FAF, TUE
float_ages = (df2['Age'] != df2['Age'].round()).sum()
print(f"Non-integer Ages in df2: {float_ages} out of {len(df2)} ({float_ages/len(df2)*100:.1f}%)")

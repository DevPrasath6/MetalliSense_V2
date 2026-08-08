"""
Analyze the training dataset to understand Fe and C distributions
"""
import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv('app/data/dataset.csv')

print("="*70)
print("DATASET ANALYSIS - Fe and C Distributions")
print("="*70)

print(f"\nTotal samples: {len(df)}")
print(f"Normal samples (is_deviated=False): {len(df[df['is_deviated'] == False])}")
print(f"Deviated samples (is_deviated=True): {len(df[df['is_deviated'] == True])}")

# Analyze Fe
print(f"\n{'='*70}")
print("Fe (Iron) Analysis")
print(f"{'='*70}")

df_normal = df[df['is_deviated'] == False]
df_deviated = df[df['is_deviated'] == True]

print(f"\nNormal samples:")
print(f"  Fe mean: {df_normal['Fe'].mean():.2f}%")
print(f"  Fe std: {df_normal['Fe'].std():.2f}%")
print(f"  Fe min: {df_normal['Fe'].min():.2f}%")
print(f"  Fe max: {df_normal['Fe'].max():.2f}%")
print(f"  Fe range: [{df_normal['Fe'].quantile(0.05):.2f}, {df_normal['Fe'].quantile(0.95):.2f}] (90% of data)")

print(f"\nDeviated samples:")
print(f"  Fe mean: {df_deviated['Fe'].mean():.2f}%")
print(f"  Fe std: {df_deviated['Fe'].std():.2f}%")
print(f"  Fe min: {df_deviated['Fe'].min():.2f}%")
print(f"  Fe max: {df_deviated['Fe'].max():.2f}%")
print(f"  Fe range: [{df_deviated['Fe'].quantile(0.05):.2f}, {df_deviated['Fe'].quantile(0.95):.2f}] (90% of data)")

# Analyze C
print(f"\n{'='*70}")
print("C (Carbon) Analysis")
print(f"{'='*70}")

print(f"\nNormal samples:")
print(f"  C mean: {df_normal['C'].mean():.2f}%")
print(f"  C std: {df_normal['C'].std():.2f}%")
print(f"  C min: {df_normal['C'].min():.2f}%")
print(f"  C max: {df_normal['C'].max():.2f}%")
print(f"  C range: [{df_normal['C'].quantile(0.05):.2f}, {df_normal['C'].quantile(0.95):.2f}] (90% of data)")

print(f"\nDeviated samples:")
print(f"  C mean: {df_deviated['C'].mean():.2f}%")
print(f"  C std: {df_deviated['C'].std():.2f}%")
print(f"  C min: {df_deviated['C'].min():.2f}%")
print(f"  C max: {df_deviated['C'].max():.2f}%")
print(f"  C range: [{df_deviated['C'].quantile(0.05):.2f}, {df_deviated['C'].quantile(0.95):.2f}] (90% of data)")

# Check samples with extreme values
print(f"\n{'='*70}")
print("Samples with Extreme Values in NORMAL data")
print(f"{'='*70}")

print(f"\nNormal samples with Fe < 90%: {len(df_normal[df_normal['Fe'] < 90])}")
print(f"Normal samples with Fe < 85%: {len(df_normal[df_normal['Fe'] < 85])}")
print(f"Normal samples with C > 4.5%: {len(df_normal[df_normal['C'] > 4.5])}")
print(f"Normal samples with C > 5.5%: {len(df_normal[df_normal['C'] > 5.5])}")

if len(df_normal[df_normal['Fe'] < 90]) > 0:
    print(f"\nSample with low Fe in normal data:")
    sample = df_normal[df_normal['Fe'] < 90].iloc[0]
    print(f"  Fe={sample['Fe']:.2f}, C={sample['C']:.2f}, Si={sample['Si']:.2f}, Mn={sample['Mn']:.2f}")

if len(df_normal[df_normal['C'] > 4.5]) > 0:
    print(f"\nSample with high C in normal data:")
    sample = df_normal[df_normal['C'] > 4.5].iloc[0]
    print(f"  Fe={sample['Fe']:.2f}, C={sample['C']:.2f}, Si={sample['Si']:.2f}, Mn={sample['Mn']:.2f}")

print(f"\n{'='*70}")

"""
Synthetic Data Generator for MetalliSense
Generates physics-aware synthetic spectrometer data
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import random

from .grade_specs import GradeSpecificationGenerator


class SyntheticDataGenerator:
    """
    Generates synthetic spectrometer data with realistic characteristics:
    - Physics-aware compositions
    - Realistic deviations
    - Multiple grades
    - Temporal patterns
    """
    
    def __init__(self, grade_generator: GradeSpecificationGenerator):
        self.grade_generator = grade_generator
        self.elements = ["Fe", "C", "Si", "Mn", "P", "S"]
        np.random.seed(42)
        random.seed(42)
    
    def _generate_normal_composition(self, grade: str) -> Dict[str, float]:
        """
        Generate a composition within specification (normal sample)
        Uses beta distribution for more realistic sampling
        """
        spec = self.grade_generator.get_grade_spec(grade)
        composition = {}
        
        for element in self.elements:
            min_val, max_val = spec["composition_ranges"][element]
            range_width = max_val - min_val
            
            # Use beta distribution centered around midpoint
            # This creates more samples near the middle, fewer at extremes
            beta_sample = np.random.beta(2, 2)  # Centered beta distribution
            value = min_val + beta_sample * range_width
            
            composition[element] = round(value, 4)
        
        return composition
    
    def _generate_deviated_composition(self, grade: str) -> Dict[str, float]:
        """
        Generate a composition with deviations (out of spec)
        Deviations are physics-aware and realistic
        """
        spec = self.grade_generator.get_grade_spec(grade)
        composition = {}
        
        # Start with a normal composition
        base_composition = self._generate_normal_composition(grade)
        
        # Select 1-3 elements to deviate
        num_deviations = random.randint(1, 3)
        elements_to_deviate = random.sample(self.elements, num_deviations)
        
        for element in self.elements:
            if element in elements_to_deviate:
                min_val, max_val = spec["composition_ranges"][element]
                range_width = max_val - min_val
                
                # Decide if deviation is above or below range
                if random.random() < 0.5:
                    # Above range deviation
                    deviation = random.uniform(0.05, 0.3) * range_width
                    value = max_val + deviation
                else:
                    # Below range deviation
                    deviation = random.uniform(0.05, 0.3) * range_width
                    value = min_val - deviation
                
                # Ensure physical constraints (no negative values)
                value = max(0.01, value)
                composition[element] = round(value, 4)
            else:
                composition[element] = base_composition[element]
        
        # Normalize to ensure sum is reasonable
        # For iron-based alloys, Fe is the balance
        total = sum(composition.values())
        if total > 100:
            # Adjust Fe to balance
            excess = total - 100
            composition["Fe"] = max(50.0, composition["Fe"] - excess)
        
        return composition
    
    def _add_measurement_noise(self, composition: Dict[str, float]) -> Dict[str, float]:
        """
        Add realistic spectrometer measurement noise
        Different elements have different precision levels
        """
        noise_levels = {
            "Fe": 0.05,   # ±0.05%
            "C": 0.02,    # ±0.02%
            "Si": 0.03,   # ±0.03%
            "Mn": 0.02,   # ±0.02%
            "P": 0.005,   # ±0.005%
            "S": 0.005    # ±0.005%
        }
        
        noisy_composition = {}
        for element, value in composition.items():
            noise = np.random.normal(0, noise_levels[element])
            noisy_value = value + noise
            noisy_composition[element] = round(max(0.001, noisy_value), 4)
        
        return noisy_composition
    
    def generate_dataset(
        self, 
        num_samples: int, 
        normal_ratio: float = 0.65,
        add_noise: bool = True
    ) -> pd.DataFrame:
        """
        Generate synthetic dataset
        
        Args:
            num_samples: Total number of samples to generate
            normal_ratio: Ratio of normal (in-spec) samples
            add_noise: Whether to add measurement noise
            
        Returns:
            DataFrame with synthetic data
        """
        print(f"Generating {num_samples} synthetic samples...")
        
        grades = self.grade_generator.get_available_grades()
        num_normal = int(num_samples * normal_ratio)
        num_deviated = num_samples - num_normal
        
        data = []
        start_time = datetime(2024, 1, 1, 0, 0, 0)
        
        # Generate normal samples
        print(f"Generating {num_normal} normal samples...")
        for i in range(num_normal):
            grade = random.choice(grades)
            composition = self._generate_normal_composition(grade)
            
            if add_noise:
                composition = self._add_measurement_noise(composition)
            
            # Add timestamp (one reading every 5 minutes)
            timestamp = start_time + timedelta(minutes=5 * i)
            
            sample = {
                "timestamp": timestamp,
                "grade": grade,
                "is_deviated": False,
                **composition
            }
            data.append(sample)
        
        # Generate deviated samples
        print(f"Generating {num_deviated} deviated samples...")
        for i in range(num_deviated):
            grade = random.choice(grades)
            composition = self._generate_deviated_composition(grade)
            
            if add_noise:
                composition = self._add_measurement_noise(composition)
            
            timestamp = start_time + timedelta(minutes=5 * (num_normal + i))
            
            sample = {
                "timestamp": timestamp,
                "grade": grade,
                "is_deviated": True,
                **composition
            }
            data.append(sample)
        
        # Create DataFrame and shuffle
        df = pd.DataFrame(data)
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        print(f"\nDataset Statistics:")
        print(f"Total samples: {len(df)}")
        print(f"Normal samples: {len(df[df['is_deviated'] == False])}")
        print(f"Deviated samples: {len(df[df['is_deviated'] == True])}")
        print(f"\nGrade distribution:")
        print(df['grade'].value_counts())
        
        return df
    
    def analyze_dataset(self, df: pd.DataFrame):
        """Print dataset analysis"""
        print("\n" + "="*60)
        print("DATASET ANALYSIS")
        print("="*60)
        
        print(f"\nShape: {df.shape}")
        print(f"\nColumns: {df.columns.tolist()}")
        
        print("\n--- Composition Statistics ---")
        composition_cols = ["Fe", "C", "Si", "Mn", "P", "S"]
        print(df[composition_cols].describe())
        
        print("\n--- Deviation Analysis ---")
        print(f"Normal samples: {len(df[df['is_deviated'] == False])} "
              f"({len(df[df['is_deviated'] == False]) / len(df) * 100:.1f}%)")
        print(f"Deviated samples: {len(df[df['is_deviated'] == True])} "
              f"({len(df[df['is_deviated'] == True]) / len(df) * 100:.1f}%)")
        
        print("\n--- Grade Distribution ---")
        print(df['grade'].value_counts())
        
        print("\n--- Sample Data (first 5 rows) ---")
        print(df.head())
        
        print("\n" + "="*60)


if __name__ == "__main__":
    # Test the generator
    from grade_specs import GradeSpecificationGenerator
    
    grade_gen = GradeSpecificationGenerator()
    data_gen = SyntheticDataGenerator(grade_gen)
    
    # Generate test dataset
    df = data_gen.generate_dataset(num_samples=1000, normal_ratio=0.65)
    data_gen.analyze_dataset(df)
    
    # Save to CSV
    df.to_csv("test_dataset.csv", index=False)
    print("\nTest dataset saved to test_dataset.csv")

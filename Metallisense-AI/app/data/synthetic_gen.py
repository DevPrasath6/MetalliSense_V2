"""
Synthetic Data Generator for MetalliSense
Generates physics-aware synthetic spectrometer data with quality validation
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import random

from .grade_specs import GradeSpecificationGenerator


class DataQualityValidator:
    """Validates generated data quality"""
    
    @staticmethod
    def validate_composition(composition: Dict[str, float], grade_spec: Dict) -> Tuple[bool, str]:
        """
        Validate a single composition sample
        
        Returns:
            (is_valid, error_message)
        """
        # Check for negative values
        for element, value in composition.items():
            if value < 0:
                return False, f"Negative value for {element}: {value}"
        
        # Check total composition (relaxed range for 6-element tracking)
        # In real spectrometry, we often only track major elements
        # Total can be 85-105% as trace elements aren't measured
        total = sum(composition.values())
        if total < 85.0 or total > 105.0:
            return False, f"Total composition out of range: {total:.2f}%"
        
        # Check Fe dominance (Fe should be majority element in all grades)
        if composition.get("Fe", 0) < 50.0:
            return False, f"Fe content too low: {composition.get('Fe', 0):.2f}%"
        
        # Check for unrealistic element combinations
        # High carbon (>2%) typically means cast iron, should have lower Fe
        if composition.get("C", 0) > 2.0 and composition.get("Fe", 0) > 95.0:
            return False, "Unrealistic: High carbon with very high Fe"
        
        return True, ""
    
    @staticmethod
    def analyze_dataset_quality(df: pd.DataFrame) -> Dict:
        """
        Comprehensive quality analysis of dataset
        
        Returns:
            Dictionary with quality metrics
        """
        composition_cols = ["Fe", "C", "Si", "Mn", "P", "S"]
        
        quality_report = {
            "total_samples": len(df),
            "negative_values": 0,
            "total_out_of_range": 0,
            "extreme_outliers": 0,
            "grade_balance": {},
            "composition_ranges": {},
            "duplicates": 0
        }
        
        # Check for negative values
        for col in composition_cols:
            quality_report["negative_values"] += (df[col] < 0).sum()
        
        # Check total composition
        df['total_composition'] = df[composition_cols].sum(axis=1)
        quality_report["total_out_of_range"] = ((df['total_composition'] < 85) | 
                                                  (df['total_composition'] > 105)).sum()
        
        # Check for extreme outliers (values beyond 3 standard deviations)
        for col in composition_cols:
            mean = df[col].mean()
            std = df[col].std()
            outliers = ((df[col] < mean - 3*std) | (df[col] > mean + 3*std)).sum()
            quality_report["extreme_outliers"] += outliers
        
        # Check grade balance
        quality_report["grade_balance"] = df['grade'].value_counts().to_dict()
        
        # Check composition ranges
        for col in composition_cols:
            quality_report["composition_ranges"][col] = {
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "mean": float(df[col].mean()),
                "std": float(df[col].std())
            }
        
        # Check duplicates
        quality_report["duplicates"] = df.duplicated(subset=composition_cols).sum()
        
        # Calculate quality score (0-100)
        issues = (quality_report["negative_values"] + 
                 quality_report["total_out_of_range"] + 
                 quality_report["extreme_outliers"])
        quality_score = max(0, 100 - (issues / len(df) * 100))
        quality_report["quality_score"] = round(quality_score, 2)
        
        return quality_report


class SyntheticDataGenerator:
    """
    Generates synthetic spectrometer data with realistic characteristics:
    - Physics-aware compositions
    - Realistic deviations
    - Multiple grades
    - Temporal patterns
    - Quality validation
    """
    
    def __init__(self, grade_generator: GradeSpecificationGenerator):
        self.grade_generator = grade_generator
        self.elements = ["Fe", "C", "Si", "Mn", "P", "S"]
        self.validator = DataQualityValidator()
        np.random.seed(42)
        random.seed(42)
    
    def _generate_normal_composition(self, grade: str, max_retries: int = 10) -> Dict[str, float]:
        """
        Generate a composition within specification (normal sample)
        Uses beta distribution for more realistic sampling
        Includes quality validation
        """
        spec = self.grade_generator.get_grade_spec(grade)
        
        for attempt in range(max_retries):
            composition = {}
            
            for element in self.elements:
                min_val, max_val = spec["composition_ranges"][element]
                range_width = max_val - min_val
                
                # Use beta distribution centered around midpoint
                # This creates more samples near the middle, fewer at extremes
                beta_sample = np.random.beta(2, 2)  # Centered beta distribution
                value = min_val + beta_sample * range_width
                
                composition[element] = round(value, 4)
            
            # Validate composition
            is_valid, error_msg = self.validator.validate_composition(composition, spec)
            if is_valid:
                return composition
            
            # If validation fails, try again
            if attempt == max_retries - 1:
                print(f"⚠️ Warning: Failed to generate valid composition after {max_retries} attempts: {error_msg}")
        
        return composition
    
    def _generate_deviated_composition(self, grade: str, max_retries: int = 10) -> Dict[str, float]:
        """
        Generate a composition with deviations (out of spec)
        Deviations are physics-aware and realistic
        Includes quality validation
        """
        spec = self.grade_generator.get_grade_spec(grade)
        
        for attempt in range(max_retries):
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
            
            # Validate composition
            is_valid, error_msg = self.validator.validate_composition(composition, spec)
            if is_valid:
                return composition
            
            # If validation fails, try again
            if attempt == max_retries - 1:
                print(f"⚠️ Warning: Failed to generate valid deviated composition after {max_retries} attempts: {error_msg}")
        
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
        add_noise: bool = True,
        validate_quality: bool = True
    ) -> pd.DataFrame:
        """
        Generate synthetic dataset with quality validation
        
        Args:
            num_samples: Total number of samples to generate
            normal_ratio: Ratio of normal (in-spec) samples
            add_noise: Whether to add measurement noise
            validate_quality: Whether to perform quality validation
            
        Returns:
            DataFrame with synthetic data
        """
        print(f"\n{'='*70}")
        print(f"GENERATING SYNTHETIC DATASET")
        print(f"{'='*70}")
        print(f"Target samples: {num_samples:,}")
        print(f"Normal ratio: {normal_ratio:.1%}")
        print(f"Measurement noise: {'Enabled' if add_noise else 'Disabled'}")
        print(f"Quality validation: {'Enabled' if validate_quality else 'Disabled'}")
        print(f"{'='*70}\n")
        
        grades = self.grade_generator.get_available_grades()
        num_normal = int(num_samples * normal_ratio)
        num_deviated = num_samples - num_normal
        
        data = []
        start_time = datetime(2024, 1, 1, 0, 0, 0)
        
        # Generate normal samples
        print(f"[1/2] Generating {num_normal:,} normal samples...")
        failed_normal = 0
        for i in range(num_normal):
            if i % 20000 == 0 and i > 0:
                print(f"      Progress: {i:,}/{num_normal:,} ({i/num_normal*100:.1f}%)")
            
            grade = random.choice(grades)
            composition = self._generate_normal_composition(grade)
            
            if add_noise:
                composition = self._add_measurement_noise(composition)
            
            # Validate if enabled
            if validate_quality:
                spec = self.grade_generator.get_grade_spec(grade)
                is_valid, error_msg = self.validator.validate_composition(composition, spec)
                if not is_valid:
                    failed_normal += 1
                    continue
            
            # Add timestamp (one reading every 5 minutes)
            timestamp = start_time + timedelta(minutes=5 * i)
            
            sample = {
                "timestamp": timestamp,
                "grade": grade,
                "is_deviated": False,
                **composition
            }
            data.append(sample)
        
        print(f"      ✅ Completed: {len([d for d in data if not d['is_deviated']]):,} normal samples")
        if failed_normal > 0:
            print(f"      ⚠️  Rejected: {failed_normal} samples failed quality validation")
        
        # Generate deviated samples
        print(f"\n[2/2] Generating {num_deviated:,} deviated samples...")
        failed_deviated = 0
        for i in range(num_deviated):
            if i % 20000 == 0 and i > 0:
                print(f"      Progress: {i:,}/{num_deviated:,} ({i/num_deviated*100:.1f}%)")
            
            grade = random.choice(grades)
            composition = self._generate_deviated_composition(grade)
            
            if add_noise:
                composition = self._add_measurement_noise(composition)
            
            # Validate if enabled
            if validate_quality:
                spec = self.grade_generator.get_grade_spec(grade)
                is_valid, error_msg = self.validator.validate_composition(composition, spec)
                if not is_valid:
                    failed_deviated += 1
                    continue
            
            timestamp = start_time + timedelta(minutes=5 * (num_normal + i))
            
            sample = {
                "timestamp": timestamp,
                "grade": grade,
                "is_deviated": True,
                **composition
            }
            data.append(sample)
        
        print(f"      ✅ Completed: {len([d for d in data if d['is_deviated']]):,} deviated samples")
        if failed_deviated > 0:
            print(f"      ⚠️  Rejected: {failed_deviated} samples failed quality validation")
        
        # Create DataFrame and shuffle
        print(f"\n[3/3] Finalizing dataset...")
        df = pd.DataFrame(data)
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        print(f"\n{'='*70}")
        print(f"DATASET GENERATION COMPLETE")
        print(f"{'='*70}")
        print(f"✅ Total samples generated: {len(df):,}")
        print(f"   • Normal samples: {len(df[df['is_deviated'] == False]):,} ({len(df[df['is_deviated'] == False])/len(df)*100:.1f}%)")
        print(f"   • Deviated samples: {len(df[df['is_deviated'] == True]):,} ({len(df[df['is_deviated'] == True])/len(df)*100:.1f}%)")
        
        # Quality report
        if validate_quality:
            print(f"\n{'='*70}")
            print(f"QUALITY REPORT")
            print(f"{'='*70}")
            quality_report = self.validator.analyze_dataset_quality(df)
            print(f"Quality Score: {quality_report['quality_score']}/100")
            print(f"Negative values: {quality_report['negative_values']}")
            print(f"Total composition out of range: {quality_report['total_out_of_range']}")
            print(f"Extreme outliers: {quality_report['extreme_outliers']}")
            print(f"Duplicate samples: {quality_report['duplicates']}")
        
        print(f"\n{'='*70}")
        print(f"Grade Distribution:")
        for grade, count in df['grade'].value_counts().items():
            print(f"   • {grade}: {count:,} ({count/len(df)*100:.1f}%)")
        print(f"{'='*70}\n")
        
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

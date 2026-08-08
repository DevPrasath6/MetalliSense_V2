"""
Grade Specification Generator for MetalliSense
Generates realistic metallurgical grade specifications
"""
from typing import Dict, List
import json


class GradeSpecificationGenerator:
    """Generates and manages metal grade specifications"""
    
    def __init__(self):
        self.grades = self._generate_specifications()
    
    def _generate_specifications(self) -> Dict[str, Dict]:
        """
        Generate realistic grade specifications for various metal grades
        Based on actual metallurgical standards
        """
        specifications = {
            "SG-IRON": {
                "grade": "SG-IRON",
                "description": "Spheroidal Graphite Cast Iron (Ductile Iron)",
                "composition_ranges": {
                    "Fe": [82.0, 90.0],
                    "C": [3.0, 4.0],
                    "Si": [1.8, 2.8],
                    "Mn": [0.3, 1.0],
                    "P": [0.01, 0.08],
                    "S": [0.01, 0.03]
                }
            },
            "GREY-IRON": {
                "grade": "GREY-IRON",
                "description": "Grey Cast Iron (General Purpose)",
                "composition_ranges": {
                    "Fe": [85.0, 92.0],
                    "C": [2.5, 3.8],
                    "Si": [1.0, 2.5],
                    "Mn": [0.4, 1.2],
                    "P": [0.02, 0.15],
                    "S": [0.02, 0.12]
                }
            },
            "LOW-CARBON-STEEL": {
                "grade": "LOW-CARBON-STEEL",
                "description": "Mild Steel (Carbon < 0.3%)",
                "composition_ranges": {
                    "Fe": [98.0, 99.5],
                    "C": [0.05, 0.25],
                    "Si": [0.1, 0.5],
                    "Mn": [0.3, 0.9],
                    "P": [0.01, 0.04],
                    "S": [0.01, 0.05]
                }
            },
            "MEDIUM-CARBON-STEEL": {
                "grade": "MEDIUM-CARBON-STEEL",
                "description": "Medium Carbon Steel (0.3-0.6% C)",
                "composition_ranges": {
                    "Fe": [97.5, 99.0],
                    "C": [0.3, 0.6],
                    "Si": [0.15, 0.6],
                    "Mn": [0.5, 1.5],
                    "P": [0.01, 0.04],
                    "S": [0.01, 0.05]
                }
            },
            "HIGH-CARBON-STEEL": {
                "grade": "HIGH-CARBON-STEEL",
                "description": "High Carbon Steel (0.6-1.4% C)",
                "composition_ranges": {
                    "Fe": [97.0, 98.5],
                    "C": [0.6, 1.4],
                    "Si": [0.2, 0.8],
                    "Mn": [0.6, 1.8],
                    "P": [0.01, 0.04],
                    "S": [0.01, 0.05]
                }
            }
        }
        
        return specifications
    
    def get_grade_spec(self, grade: str) -> Dict:
        """
        Get specification for a specific grade
        
        Args:
            grade: Grade name (e.g., "SG-IRON")
            
        Returns:
            Grade specification dictionary
        """
        if grade not in self.grades:
            raise ValueError(f"Unknown grade: {grade}. Available grades: {self.get_available_grades()}")
        return self.grades[grade]
    
    def get_available_grades(self) -> List[str]:
        """Get list of all available grades"""
        return list(self.grades.keys())
    
    def get_all_specifications(self) -> Dict[str, Dict]:
        """Get all grade specifications"""
        return self.grades
    
    def get_composition_midpoint(self, grade: str) -> Dict[str, float]:
        """
        Get midpoint values for each element in a grade
        Useful for training alloy correction agent
        
        Args:
            grade: Grade name
            
        Returns:
            Dictionary with midpoint values for each element
        """
        spec = self.get_grade_spec(grade)
        midpoints = {}
        
        for element, (min_val, max_val) in spec["composition_ranges"].items():
            midpoints[element] = (min_val + max_val) / 2.0
        
        return midpoints
    
    def is_composition_in_spec(self, grade: str, composition: Dict[str, float]) -> Dict[str, bool]:
        """
        Check if composition is within specification for each element
        
        Args:
            grade: Grade name
            composition: Dictionary with element percentages
            
        Returns:
            Dictionary indicating which elements are in spec
        """
        spec = self.get_grade_spec(grade)
        in_spec = {}
        
        for element in composition:
            if element not in spec["composition_ranges"]:
                continue
            
            min_val, max_val = spec["composition_ranges"][element]
            value = composition[element]
            in_spec[element] = min_val <= value <= max_val
        
        return in_spec
    
    def get_deviation_from_spec(self, grade: str, composition: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate deviation from specification midpoint
        
        Args:
            grade: Grade name
            composition: Current composition
            
        Returns:
            Dictionary with deviation for each element
        """
        midpoints = self.get_composition_midpoint(grade)
        deviations = {}
        
        for element in composition:
            if element in midpoints:
                deviations[element] = composition[element] - midpoints[element]
        
        return deviations
    
    def save_specifications(self, filepath: str):
        """Save specifications to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.grades, f, indent=2)
    
    def load_specifications(self, filepath: str):
        """Load specifications from JSON file"""
        with open(filepath, 'r') as f:
            self.grades = json.load(f)


# Singleton instance
grade_spec_generator = GradeSpecificationGenerator()


if __name__ == "__main__":
    # Test the generator
    gen = GradeSpecificationGenerator()
    
    print("Available Grades:")
    for grade in gen.get_available_grades():
        print(f"\n{grade}:")
        spec = gen.get_grade_spec(grade)
        print(f"  Description: {spec['description']}")
        print(f"  Composition Ranges:")
        for element, ranges in spec['composition_ranges'].items():
            print(f"    {element}: {ranges[0]} - {ranges[1]}%")

import numpy as np
import cv2
from PIL import Image
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt

class CTScanRulesAnalyzer:
    def __init__(self, rules_file="ct_scan_rules.json"):
        """Initialize with rules from a configuration file"""
        self.rules_file = rules_file
        
        # Default rules if file doesn't exist
        self.rules = {
            # Normal ventricle parameters (area ratio as percentage of brain area)
            "ventricle_size": {
                "normal_max": 5.0,  # Maximum normal ventricle size as % of brain area
                "mild_max": 8.0,     # Mild enlargement cutoff
                "moderate_max": 12.0, # Moderate enlargement cutoff
                "severe_min": 12.0    # Severe enlargement threshold
            },
            
            # Cortical atrophy parameters
            "sulci_width": {
                "normal_max": 3.0,   # Maximum normal sulci width as % of brain width
                "mild_max": 5.0,     # Mild atrophy cutoff
                "moderate_max": 7.0,  # Moderate atrophy cutoff
                "severe_min": 7.0     # Severe atrophy threshold
            },
            
            # Brain symmetry parameters
            "symmetry": {
                "normal_min": 0.85,   # Minimum symmetry score for normal
                "abnormal_max": 0.75   # Maximum symmetry score for abnormal
            },
            
            # Gray-white matter differentiation
            "gray_white_ratio": {
                "normal_min": 1.2,    # Minimum contrast ratio for normal
                "mild_min": 1.1,      # Mild loss cutoff
                "moderate_min": 1.05,  # Moderate loss cutoff
                "severe_max": 1.05     # Severe loss threshold
            },
            
            # Confidence adjustment factors
            "confidence_factors": {
                "ventricle_weight": 0.40,    # Weight for ventricle analysis
                "atrophy_weight": 0.30,      # Weight for cortical atrophy
                "symmetry_weight": 0.15,     # Weight for symmetry analysis
                "gray_white_weight": 0.15,   # Weight for gray-white matter differentiation
                "age_adjustment": {
                    "elderly": 0.8,          # Confidence multiplier for elderly patients (>65)
                    "adult": 1.0,            # For adults (18-65)
                    "child": 1.2             # For children (<18)
                }
            },
            
            # Specific markers for different disorders
            "disorder_markers": {
                "Alzheimer's Disease": {
                    "ventricle_enlarge": True,
                    "temporal_atrophy": True,
                    "hippocampal_atrophy": True,
                    "asymmetry": False
                },
                "Vascular Dementia": {
                    "ventricle_enlarge": True,
                    "temporal_atrophy": False,
                    "white_matter_lesions": True,
                    "asymmetry": True
                },
                "Normal Pressure Hydrocephalus": {
                    "ventricle_enlarge": True,
                    "temporal_atrophy": False,
                    "asymmetry": False,
                    "periventricular_changes": False
                }
            },
            
            # Normal ranges for different age groups
            "age_ranges": {
                "child": {
                    "ventricle_size": {"normal_max": 4.0},
                    "sulci_width": {"normal_max": 2.0}
                },
                "adult": {
                    "ventricle_size": {"normal_max": 5.0},
                    "sulci_width": {"normal_max": 3.0}
                },
                "elderly": {
                    "ventricle_size": {"normal_max": 7.0},
                    "sulci_width": {"normal_max": 4.0}
                }
            }
        }
        
        # Load rules from file if exists
        if os.path.exists(self.rules_file):
            try:
                with open(self.rules_file, 'r') as f:
                    loaded_rules = json.load(f)
                    # Update default rules with loaded values
                    for category, values in loaded_rules.items():
                        if category in self.rules:
                            if isinstance(values, dict):
                                self.rules[category].update(values)
                            else:
                                self.rules[category] = values
            except:
                print(f"Error loading rules from {self.rules_file}, using defaults")
    
    def save_rules(self):
        """Save current rules to the rules file"""
        try:
            with open(self.rules_file, 'w') as f:
                json.dump(self.rules, f, indent=4)
            return True
        except:
            print(f"Error saving rules to {self.rules_file}")
            return False
    
    def analyze_ct_scan(self, image_path, patient_age=None):
        """
        Analyze a CT scan using rule-based approach
        
        Args:
            image_path: Path to the CT scan image
            patient_age: Patient age if known (affects normal ranges)
            
        Returns:
            Dictionary with analysis results
        """
        # Load the image
        img = Image.open(image_path)
        img_np = np.array(img)
        
        # Convert to grayscale if needed
        if len(img_np.shape) == 3 and img_np.shape[2] > 1:
            img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        else:
            img_gray = img_np.astype(np.uint8)
        
        # Determine age group if provided
        age_group = "adult"  # Default
        if patient_age is not None:
            if patient_age < 18:
                age_group = "child"
            elif patient_age > 65:
                age_group = "elderly"
        
        # Apply age-specific normal ranges
        rules = self.rules.copy()
        if age_group in rules["age_ranges"]:
            for category, values in rules["age_ranges"][age_group].items():
                if category in rules:
                    rules[category].update(values)
        
        # Pre-process image for analysis
        processed_img = self._preprocess_image(img_gray)
        
        # Extract key features
        features = self._extract_features(processed_img)
        
        # Apply rules to detect abnormalities
        abnormalities = self._apply_rules(features, rules)
        
        # Determine overall results
        result = self._determine_result(abnormalities, features, rules, age_group)
        
        # Add analysis metadata
        result["analysis_timestamp"] = datetime.now().isoformat()
        result["analyzer_version"] = "1.0"
        result["analyzed_file"] = os.path.basename(image_path)
        
        return result
    
    def _preprocess_image(self, img_gray):
        """Pre-process the CT scan for better feature extraction"""
        # Apply adaptive histogram equalization for better contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        img_enhanced = clahe.apply(img_gray.astype(np.uint8))
        
        # Apply Gaussian blur to reduce noise
        img_blur = cv2.GaussianBlur(img_enhanced, (3, 3), 0)
        
        return img_blur
    
    def _extract_features(self, img):
        """
        Extract key features from the CT scan for rule-based analysis
        
        This extracts:
        1. Ventricle size estimation
        2. Cortical atrophy estimation (sulci width)
        3. Brain symmetry
        4. Gray-white matter differentiation
        5. Potential white matter lesions
        """
        features = {}
        height, width = img.shape
        
        # Segment the brain
        _, brain_mask = cv2.threshold(img, 10, 255, cv2.THRESH_BINARY)
        kernel = np.ones((5,5), np.uint8)
        brain_mask = cv2.morphologyEx(brain_mask, cv2.MORPH_CLOSE, kernel)
        brain_area = np.sum(brain_mask > 0)
        
        # 1. Ventricle segmentation (dark areas within brain)
        # Use a lower threshold for ventricles
        _, ventricle_mask = cv2.threshold(img, 40, 255, cv2.THRESH_BINARY_INV)
        # Refine ventricle mask to only include areas within the brain
        ventricle_mask = cv2.bitwise_and(ventricle_mask, brain_mask)
        # Remove small noise
        ventricle_mask = cv2.morphologyEx(ventricle_mask, cv2.MORPH_OPEN, kernel)
        
        ventricle_area = np.sum(ventricle_mask > 0)
        # Calculate as percentage of brain area
        if brain_area > 0:
            ventricle_percentage = (ventricle_area / brain_area) * 100
        else:
            ventricle_percentage = 0
            
        features["ventricle_size"] = ventricle_percentage
        
        # 2. Cortical atrophy estimation (via sulci identification)
        # Edge detection for sulci
        edges = cv2.Canny(img, 50, 150)
        # Only consider edges within brain boundary, away from ventricles
        outer_brain = cv2.erode(brain_mask, kernel, iterations=3)
        sulci_candidate = cv2.bitwise_and(edges, outer_brain)
        
        # Calculate average sulci width as percentage of brain width
        sulci_pixels = np.sum(sulci_candidate > 0)
        if brain_area > 0:
            sulci_percentage = (sulci_pixels / np.sqrt(brain_area)) * 10  # Normalize by brain size
        else:
            sulci_percentage = 0
            
        features["sulci_width"] = sulci_percentage
        
        # 3. Brain symmetry analysis
        # Find middle column
        midpoint = width // 2
        
        # Get left and right halves
        left_half = img[:, :midpoint]
        right_half = img[:, midpoint:]
        
        # Ensure equal width by trimming if needed
        min_width = min(left_half.shape[1], right_half.shape[1])
        left_half = left_half[:, :min_width]
        right_half_flipped = np.fliplr(right_half[:, :min_width])
        
        # Calculate symmetry score
        diff = np.abs(left_half.astype(float) - right_half_flipped.astype(float))
        
        # Normalize by intensity range
        intensity_range = np.max(img) - np.min(img)
        if intensity_range > 0:
            normalized_diff = diff / intensity_range
        else:
            normalized_diff = diff
            
        # Symmetry score (1 = perfect symmetry, 0 = no symmetry)
        symmetry_score = 1 - np.mean(normalized_diff)
        features["symmetry_score"] = symmetry_score
        
        # 4. Gray-white matter differentiation
        # Use Otsu's thresholding to separate gray and white matter
        _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Create masks for potential gray and white matter
        white_matter_mask = cv2.bitwise_and(thresh, brain_mask)
        gray_matter_mask = cv2.bitwise_and(cv2.bitwise_not(thresh), brain_mask)
        
        # Calculate average intensities
        white_matter_pixels = np.sum(white_matter_mask > 0)
        gray_matter_pixels = np.sum(gray_matter_mask > 0)
        
        if white_matter_pixels > 0 and gray_matter_pixels > 0:
            white_matter_intensity = np.sum(img * (white_matter_mask > 0)) / white_matter_pixels
            gray_matter_intensity = np.sum(img * (gray_matter_mask > 0)) / gray_matter_pixels
            
            if gray_matter_intensity > 0:
                gray_white_ratio = white_matter_intensity / gray_matter_intensity
            else:
                gray_white_ratio = 1.0
        else:
            gray_white_ratio = 1.0
            
        features["gray_white_ratio"] = gray_white_ratio
        
        # 5. Detect potential white matter lesions
        # Look for hypodensities in white matter regions
        _, white_matter_thresh = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)
        # Erode to get inner white matter
        inner_white_matter = cv2.erode(white_matter_thresh, kernel, iterations=2)
        
        # Detect low intensity regions within white matter
        _, white_matter_low = cv2.threshold(img, 60, 255, cv2.THRESH_BINARY_INV)
        white_matter_lesions = cv2.bitwise_and(white_matter_low, inner_white_matter)
        
        lesion_area = np.sum(white_matter_lesions > 0)
        if np.sum(inner_white_matter > 0) > 0:
            lesion_percentage = (lesion_area / np.sum(inner_white_matter > 0)) * 100
        else:
            lesion_percentage = 0
            
        features["white_matter_lesions"] = lesion_percentage
        
        # 6. Detect temporal lobe atrophy (simplified)
        # This is a simplified approximation - would need actual anatomical markers for accuracy
        # Assume temporal regions are in lower middle third of the brain
        h, w = img.shape
        temporal_region = img[int(h*0.6):int(h*0.8), int(w*0.3):int(w*0.7)]
        
        if temporal_region.size > 0:
            # Calculate darkness in temporal region (more darkness = more atrophy)
            temporal_darkness = 255 - np.mean(temporal_region)
            # Normalize by overall brain darkness
            overall_darkness = 255 - np.mean(img * (brain_mask > 0) / 255)
            
            if overall_darkness > 0:
                temporal_atrophy = temporal_darkness / overall_darkness
            else:
                temporal_atrophy = 1.0
        else:
            temporal_atrophy = 1.0
            
        features["temporal_atrophy"] = temporal_atrophy
        
        return features
    
    def _apply_rules(self, features, rules):
        """Apply the defined rules to extracted features"""
        abnormalities = {}
        
        # Check ventricle size
        ventricle_size = features["ventricle_size"]
        if ventricle_size > rules["ventricle_size"]["severe_min"]:
            abnormalities["ventricle_enlargement"] = {
                "severity": "severe",
                "value": ventricle_size,
                "threshold": rules["ventricle_size"]["severe_min"]
            }
        elif ventricle_size > rules["ventricle_size"]["moderate_max"]:
            abnormalities["ventricle_enlargement"] = {
                "severity": "moderate",
                "value": ventricle_size,
                "threshold": rules["ventricle_size"]["moderate_max"]
            }
        elif ventricle_size > rules["ventricle_size"]["mild_max"]:
            abnormalities["ventricle_enlargement"] = {
                "severity": "mild",
                "value": ventricle_size,
                "threshold": rules["ventricle_size"]["mild_max"]
            }
        elif ventricle_size > rules["ventricle_size"]["normal_max"]:
            abnormalities["ventricle_enlargement"] = {
                "severity": "borderline",
                "value": ventricle_size,
                "threshold": rules["ventricle_size"]["normal_max"]
            }
        
        # Check cortical atrophy (sulci width)
        sulci_width = features["sulci_width"]
        if sulci_width > rules["sulci_width"]["severe_min"]:
            abnormalities["cortical_atrophy"] = {
                "severity": "severe",
                "value": sulci_width,
                "threshold": rules["sulci_width"]["severe_min"]
            }
        elif sulci_width > rules["sulci_width"]["moderate_max"]:
            abnormalities["cortical_atrophy"] = {
                "severity": "moderate",
                "value": sulci_width,
                "threshold": rules["sulci_width"]["moderate_max"]
            }
        elif sulci_width > rules["sulci_width"]["mild_max"]:
            abnormalities["cortical_atrophy"] = {
                "severity": "mild",
                "value": sulci_width,
                "threshold": rules["sulci_width"]["mild_max"]
            }
        elif sulci_width > rules["sulci_width"]["normal_max"]:
            abnormalities["cortical_atrophy"] = {
                "severity": "borderline",
                "value": sulci_width,
                "threshold": rules["sulci_width"]["normal_max"]
            }
        
        # Check brain symmetry
        symmetry_score = features["symmetry_score"]
        if symmetry_score < rules["symmetry"]["abnormal_max"]:
            abnormalities["asymmetry"] = {
                "severity": "significant",
                "value": symmetry_score,
                "threshold": rules["symmetry"]["abnormal_max"]
            }
        elif symmetry_score < rules["symmetry"]["normal_min"]:
            abnormalities["asymmetry"] = {
                "severity": "mild",
                "value": symmetry_score,
                "threshold": rules["symmetry"]["normal_min"]
            }
        
        # Check gray-white matter differentiation
        gray_white_ratio = features["gray_white_ratio"]
        if gray_white_ratio < rules["gray_white_ratio"]["severe_max"]:
            abnormalities["gray_white_differentiation"] = {
                "severity": "severe",
                "value": gray_white_ratio,
                "threshold": rules["gray_white_ratio"]["severe_max"]
            }
        elif gray_white_ratio < rules["gray_white_ratio"]["moderate_min"]:
            abnormalities["gray_white_differentiation"] = {
                "severity": "moderate",
                "value": gray_white_ratio,
                "threshold": rules["gray_white_ratio"]["moderate_min"]
            }
        elif gray_white_ratio < rules["gray_white_ratio"]["mild_min"]:
            abnormalities["gray_white_differentiation"] = {
                "severity": "mild",
                "value": gray_white_ratio,
                "threshold": rules["gray_white_ratio"]["mild_min"]
            }
        elif gray_white_ratio < rules["gray_white_ratio"]["normal_min"]:
            abnormalities["gray_white_differentiation"] = {
                "severity": "borderline",
                "value": gray_white_ratio,
                "threshold": rules["gray_white_ratio"]["normal_min"]
            }
        
        # Check for white matter lesions
        lesion_percentage = features["white_matter_lesions"]
        if lesion_percentage > 5.0:  # Arbitrary threshold
            abnormalities["white_matter_lesions"] = {
                "severity": "significant" if lesion_percentage > 10.0 else "mild",
                "value": lesion_percentage
            }
        
        # Check for temporal lobe atrophy
        temporal_atrophy = features["temporal_atrophy"]
        if temporal_atrophy > 1.2:  # Normalized ratio - arbitrary threshold
            abnormalities["temporal_atrophy"] = {
                "severity": "significant" if temporal_atrophy > 1.4 else "mild",
                "value": temporal_atrophy
            }
        
        return abnormalities
    
    def _determine_result(self, abnormalities, features, rules, age_group):
        """Determine overall result based on abnormalities"""
        result = {
            "detection": False,
            "confidence_level": 0,
            "key_observations": [],
            "affected_regions": [],
            "recommendations": []
        }
        
        # If no abnormalities, it's normal
        if not abnormalities:
            result["detection"] = False
            result["confidence_level"] = 90
            result["key_observations"] = ["No significant abnormalities detected"]
            result["recommendations"] = ["Regular follow-up as needed"]
            return result
        
        # Calculate weighted abnormality score
        abnormality_score = 0
        severity_weights = {
            "severe": 1.0,
            "moderate": 0.7,
            "mild": 0.4,
            "borderline": 0.2,
            "significant": 0.8
        }
        
        confidence_factors = rules["confidence_factors"]
        
        # Process ventricle enlargement
        if "ventricle_enlargement" in abnormalities:
            severity = abnormalities["ventricle_enlargement"]["severity"]
            weight = severity_weights.get(severity, 0.3)
            abnormality_score += weight * confidence_factors["ventricle_weight"]
            
            observation = f"{severity.capitalize()} ventricular enlargement"
            result["key_observations"].append(observation)
            result["affected_regions"].append("Ventricles")
        
        # Process cortical atrophy
        if "cortical_atrophy" in abnormalities:
            severity = abnormalities["cortical_atrophy"]["severity"]
            weight = severity_weights.get(severity, 0.3)
            abnormality_score += weight * confidence_factors["atrophy_weight"]
            
            observation = f"{severity.capitalize()} cortical atrophy"
            result["key_observations"].append(observation)
            result["affected_regions"].append("Cerebral cortex")
        
        # Process asymmetry
        if "asymmetry" in abnormalities:
            severity = abnormalities["asymmetry"]["severity"]
            weight = severity_weights.get(severity, 0.3)
            abnormality_score += weight * confidence_factors["symmetry_weight"]
            
            observation = f"{severity.capitalize()} brain asymmetry"
            result["key_observations"].append(observation)
            result["affected_regions"].append("Brain hemispheres")
        
        # Process gray-white matter differentiation
        if "gray_white_differentiation" in abnormalities:
            severity = abnormalities["gray_white_differentiation"]["severity"]
            weight = severity_weights.get(severity, 0.3)
            abnormality_score += weight * confidence_factors["gray_white_weight"]
            
            observation = f"{severity.capitalize()} loss of gray-white matter differentiation"
            result["key_observations"].append(observation)
            result["affected_regions"].append("Gray-white matter junction")
        
        # Process white matter lesions
        if "white_matter_lesions" in abnormalities:
            severity = abnormalities["white_matter_lesions"]["severity"]
            weight = severity_weights.get(severity, 0.3)
            abnormality_score += weight * 0.2  # Additional factor not in main weights
            
            observation = f"{severity.capitalize()} white matter hypodensities"
            result["key_observations"].append(observation)
            result["affected_regions"].append("White matter")
        
        # Process temporal atrophy
        if "temporal_atrophy" in abnormalities:
            severity = abnormalities["temporal_atrophy"]["severity"]
            weight = severity_weights.get(severity, 0.3)
            abnormality_score += weight * 0.2  # Additional factor not in main weights
            
            observation = f"{severity.capitalize()} temporal lobe atrophy"
            result["key_observations"].append(observation)
            result["affected_regions"].append("Temporal lobes")
        
        # Convert abnormality score to confidence (0-100)
        confidence = min(100, abnormality_score * 100)
        
        # Apply age adjustment to confidence
        age_adjustments = confidence_factors["age_adjustment"]
        confidence *= age_adjustments.get(age_group, 1.0)
        
        # If confidence is above threshold, determine detection result
        if confidence >= 40:
            result["detection"] = True
            result["confidence_level"] = confidence
            
            # Determine disorder type based on pattern of abnormalities
            disorder_type = self._determine_disorder_type(abnormalities, features)
            if disorder_type:
                result["disorder_type"] = disorder_type
            else:
                result["disorder_type"] = "Unspecified neurodegenerative disorder"
            
            # Determine progression
            progression = self._determine_progression(abnormalities)
            result["progression_percentage"] = progression
            
            # Determine stage
            if progression < 25:
                result["progression_stage"] = "Early"
            elif progression < 50:
                result["progression_stage"] = "Mild"
            elif progression < 75:
                result["progression_stage"] = "Moderate"
            else:
                result["progression_stage"] = "Severe"
            
            # Add recommendations
            result["recommendations"] = [
                "Consult with a neurologist or specialist for clinical correlation",
                "Consider additional diagnostic tests (MRI, neuropsychological testing)",
                "Follow-up imaging in 3-6 months to assess progression"
            ]
            
            if "disorder_type" in result and result["disorder_type"] == "Alzheimer's Disease":
                result["recommendations"].append("Consider specific Alzheimer's treatments and care planning")
            
        else:
            # Low confidence, but abnormalities present
            result["detection"] = False
            result["confidence_level"] = 100 - confidence  # Confidence in normality
            result["key_observations"].append("Some findings present but below diagnostic threshold")
            result["recommendations"] = [
                "Clinical correlation recommended",
                "Consider follow-up imaging if symptoms present"
            ]
        
        return result
    
    def _determine_disorder_type(self, abnormalities, features):
        """Determine potential disorder type based on pattern of abnormalities"""
        # Check for Alzheimer's pattern
        if ("ventricle_enlargement" in abnormalities and 
            ("cortical_atrophy" in abnormalities or "temporal_atrophy" in abnormalities) and
            features.get("temporal_atrophy", 0) > 1.1):
            return "Alzheimer's Disease"
        
        # Check for Vascular Dementia pattern
        if ("white_matter_lesions" in abnormalities and 
            "asymmetry" in abnormalities):
            return "Vascular Dementia"
        
        # Check for Normal Pressure Hydrocephalus
        if ("ventricle_enlargement" in abnormalities and 
            abnormalities["ventricle_enlargement"]["severity"] in ["moderate", "severe"] and
            "cortical_atrophy" not in abnormalities):
            return "Normal Pressure Hydrocephalus"
        
        # Default if pattern doesn't match known disorders
        return None
    
    def _determine_progression(self, abnormalities):
        """Determine disease progression percentage based on abnormalities"""
        severity_scores = {
            "borderline": 20,
            "mild": 40, 
            "moderate": 70,
            "severe": 90,
            "significant": 75
        }
        
        # Calculate average severity score
        total_score = 0
        count = 0
        
        for abnormality, data in abnormalities.items():
            severity = data["severity"]
            if severity in severity_scores:
                total_score += severity_scores[severity]
                count += 1
        
        if count > 0:
            return total_score / count
        else:
            return 0
    
    def visualize_analysis(self, image_path, result, output_path=None):
        """
        Create a visualization of the analysis results
        
        Args:
            image_path: Path to the original CT scan
            result: Analysis result from analyze_ct_scan
            output_path: Path to save visualization (if None, will be based on image_path)
        
        Returns:
            Path to the saved visualization
        """
        if output_path is None:
            output_path = os.path.splitext(image_path)[0] + "_analysis.png"
        
        # Load the original image
        img = Image.open(image_path)
        img_np = np.array(img)
        
        # Convert to grayscale if needed
        if len(img_np.shape) == 3 and img_np.shape[2] > 1:
            img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        else:
            img_gray = img_np.astype(np.uint8)
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Original image
        axes[0, 0].imshow(img_gray, cmap='gray')
        axes[0, 0].set_title("Original CT Scan")
        axes[0, 0].axis('off')
        
        # Ventricle segmentation
        _, brain_mask = cv2.threshold(img_gray, 10, 255, cv2.THRESH_BINARY)
        kernel = np.ones((5,5), np.uint8)
        brain_mask = cv2.morphologyEx(brain_mask, cv2.MORPH_CLOSE, kernel)
        
        _, ventricle_mask = cv2.threshold(img_gray, 40, 255, cv2.THRESH_BINARY_INV)
        ventricle_mask = cv2.bitwise_and(ventricle_mask, brain_mask)
        ventricle_mask = cv2.morphologyEx(ventricle_mask, cv2.MORPH_OPEN, kernel)
        
        # Create ventricle overlay
        ventricle_overlay = np.zeros((img_gray.shape[0], img_gray.shape[1], 3), dtype=np.uint8)
        ventricle_overlay[ventricle_mask > 0] = [255, 0, 0]  # Red for ventricles
        
        # Show original with ventricle overlay
        axes[0, 1].imshow(img_gray, cmap='gray')
        axes[0, 1].imshow(ventricle_overlay, alpha=0.5)
        axes[0, 1].set_title("Ventricle Detection")
        axes[0, 1].axis('off')
        
        # Cortical atrophy / sulci detection
        edges = cv2.Canny(img_gray, 50, 150)
        outer_brain = cv2.erode(brain_mask, kernel, iterations=3)
        sulci_candidate = cv2.bitwise_and(edges, outer_brain)
        
        # Create sulci overlay
        sulci_overlay = np.zeros((img_gray.shape[0], img_gray.shape[1], 3), dtype=np.uint8)
        sulci_overlay[sulci_candidate > 0] = [0, 255, 0]  # Green for sulci
        
        # Show original with sulci overlay
        axes[1, 0].imshow(img_gray, cmap='gray')
        axes[1, 0].imshow(sulci_overlay, alpha=0.5)
        axes[1, 0].set_title("Cortical Atrophy Analysis")
        axes[1, 0].axis('off')
        
        # Results summary
        axes[1, 1].axis('off')
        if result["detection"]:
            result_text = f"DETECTION: YES\n"
            result_text += f"Confidence: {result['confidence_level']:.1f}%\n"
            result_text += f"Type: {result.get('disorder_type', 'Unknown')}\n"
            result_text += f"Stage: {result.get('progression_stage', 'Unknown')}\n\n"
        else:
            result_text = f"DETECTION: NO\n"
            result_text += f"Confidence: {result['confidence_level']:.1f}%\n\n"
        
        result_text += "Observations:\n"
        for obs in result["key_observations"]:
            result_text += f"• {obs}\n"
        
        if "affected_regions" in result and result["affected_regions"]:
            result_text += "\nAffected Regions:\n"
            for region in result["affected_regions"]:
                result_text += f"• {region}\n"
        
        axes[1, 1].text(0.05, 0.95, result_text, va='top', fontsize=10)
        axes[1, 1].set_title("Analysis Results")
        
        # Add overall header
        if result["detection"]:
            plt.suptitle(f"CT Scan Analysis: {result.get('disorder_type', 'Abnormal')} Detected", 
                         color='red', fontsize=16)
        else:
            plt.suptitle("CT Scan Analysis: No Abnormalities Detected", 
                         color='green', fontsize=16)
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
        
        # Save figure
        plt.savefig(output_path)
        plt.close()
        
        return output_path
    
    def calibrate_rules(self, normal_images, abnormal_images, patient_ages=None):
        """
        Calibrate rules based on known normal and abnormal CT scans
        
        Args:
            normal_images: List of paths to normal CT scans
            abnormal_images: List of paths to abnormal CT scans
            patient_ages: Dictionary mapping image paths to patient ages (optional)
            
        Returns:
            Dictionary with calibration statistics
        """
        print(f"Calibrating rules using {len(normal_images)} normal and {len(abnormal_images)} abnormal scans")
        
        # Extract features from normal scans
        normal_features = []
        for img_path in normal_images:
            try:
                img = Image.open(img_path)
                img_np = np.array(img)
                
                # Convert to grayscale if needed
                if len(img_np.shape) == 3 and img_np.shape[2] > 1:
                    img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
                else:
                    img_gray = img_np.astype(np.uint8)
                
                # Pre-process image
                processed_img = self._preprocess_image(img_gray)
                
                # Extract features
                features = self._extract_features(processed_img)
                normal_features.append(features)
                
            except Exception as e:
                print(f"Error processing {img_path}: {str(e)}")
        
        # Extract features from abnormal scans
        abnormal_features = []
        for img_path in abnormal_images:
            try:
                img = Image.open(img_path)
                img_np = np.array(img)
                
                # Convert to grayscale if needed
                if len(img_np.shape) == 3 and img_np.shape[2] > 1:
                    img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
                else:
                    img_gray = img_np.astype(np.uint8)
                
                # Pre-process image
                processed_img = self._preprocess_image(img_gray)
                
                # Extract features
                features = self._extract_features(processed_img)
                abnormal_features.append(features)
                
            except Exception as e:
                print(f"Error processing {img_path}: {str(e)}")
        
        # Calculate statistics for each feature
        if not normal_features or not abnormal_features:
            return {"error": "Not enough valid images for calibration"}
        
        calibration_stats = {}
        
        # Process ventricle size
        normal_ventricle_sizes = [f["ventricle_size"] for f in normal_features]
        abnormal_ventricle_sizes = [f["ventricle_size"] for f in abnormal_features]
        
        # Set normal_max as 95th percentile of normal scans
        if normal_ventricle_sizes:
            ventricle_normal_max = np.percentile(normal_ventricle_sizes, 95)
        else:
            ventricle_normal_max = self.rules["ventricle_size"]["normal_max"]
            
        # Set abnormal thresholds based on distribution
        if abnormal_ventricle_sizes:
            ventricle_mild_max = np.percentile(abnormal_ventricle_sizes, 25)
            ventricle_moderate_max = np.percentile(abnormal_ventricle_sizes, 50)
            ventricle_severe_min = np.percentile(abnormal_ventricle_sizes, 75)
        else:
            ventricle_mild_max = self.rules["ventricle_size"]["mild_max"]
            ventricle_moderate_max = self.rules["ventricle_size"]["moderate_max"]
            ventricle_severe_min = self.rules["ventricle_size"]["severe_min"]
        
        # Update rules with calibrated values
        self.rules["ventricle_size"]["normal_max"] = ventricle_normal_max
        self.rules["ventricle_size"]["mild_max"] = ventricle_mild_max
        self.rules["ventricle_size"]["moderate_max"] = ventricle_moderate_max
        self.rules["ventricle_size"]["severe_min"] = ventricle_severe_min
        
        # Record statistics
        calibration_stats["ventricle_size"] = {
            "normal_mean": np.mean(normal_ventricle_sizes) if normal_ventricle_sizes else 0,
            "normal_std": np.std(normal_ventricle_sizes) if normal_ventricle_sizes else 0,
            "abnormal_mean": np.mean(abnormal_ventricle_sizes) if abnormal_ventricle_sizes else 0,
            "abnormal_std": np.std(abnormal_ventricle_sizes) if abnormal_ventricle_sizes else 0,
            "thresholds": {
                "normal_max": ventricle_normal_max,
                "mild_max": ventricle_mild_max,
                "moderate_max": ventricle_moderate_max,
                "severe_min": ventricle_severe_min
            }
        }
        
        # Repeat for other features (sulci width, symmetry, etc.)
        # ... similar calibration for other features ...
        
        # Save calibrated rules
        self.save_rules()
        
        return calibration_stats
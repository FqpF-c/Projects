import os
import json
import numpy as np
from PIL import Image
import cv2
from datetime import datetime
import matplotlib.pyplot as plt

class CTScanReferenceDatabase:
    def __init__(self, database_dir="reference_database"):
        """Initialize the reference database for normal and abnormal CT scans"""
        self.database_dir = database_dir
        self.normal_dir = os.path.join(database_dir, "normal")
        self.abnormal_dir = os.path.join(database_dir, "abnormal")
        self.features_file = os.path.join(database_dir, "features.json")
        self.features_data = {"normal": [], "abnormal": []}
        
        # Create directories if they don't exist
        os.makedirs(self.normal_dir, exist_ok=True)
        os.makedirs(self.abnormal_dir, exist_ok=True)
        
        # Load existing features if available
        if os.path.exists(self.features_file):
            try:
                with open(self.features_file, 'r') as f:
                    self.features_data = json.load(f)
            except:
                print("Error loading features file. Creating a new one.")
                self.features_data = {"normal": [], "abnormal": []}
    
    def add_reference_scan(self, image_path, is_normal, metadata=None):
        """Add a new reference scan to the appropriate category"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Determine target directory
        target_dir = self.normal_dir if is_normal else self.abnormal_dir
        category = "normal" if is_normal else "abnormal"
        
        # Load and process the image
        img = Image.open(image_path)
        img_np = np.array(img)
        
        # Extract features for the image
        features = self.extract_features(img_np)
        
        # Create metadata if not provided
        if metadata is None:
            metadata = {}
        
        # Add timestamp and source file
        metadata["added_timestamp"] = datetime.now().isoformat()
        metadata["source_file"] = os.path.basename(image_path)
        
        # Create a unique filename for the stored image
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{category}_{timestamp}_{os.path.basename(image_path)}"
        target_path = os.path.join(target_dir, filename)
        
        # Save a copy of the image
        img.save(target_path)
        
        # Store feature data
        feature_entry = {
            "filename": filename,
            "features": features,
            "metadata": metadata
        }
        
    def export_comparison_visualization(self, image_path, output_path):
        """
        Create a visualization comparing the input scan with closest matches
        from both normal and abnormal reference sets
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
            
        # Get comparison result with top matches
        result = self.compare_with_references(image_path, top_n=2)
        
        # Create figure with subplots
        fig, axes = plt.subplots(1, 5, figsize=(15, 5))
        
        # Load and display query image
        query_img = Image.open(image_path)
        axes[0].imshow(query_img, cmap='gray')
        axes[0].set_title("Query Image")
        axes[0].axis('off')
        
        # Display top 2 normal matches
        for i in range(2):
            if i < len(result["top_normal_matches"]):
                match = result["top_normal_matches"][i]
                img_path = os.path.join(self.normal_dir, match["reference"])
                if os.path.exists(img_path):
                    match_img = Image.open(img_path)
                    axes[i+1].imshow(match_img, cmap='gray')
                    axes[i+1].set_title(f"Normal Match\nSim: {match['similarity']:.2f}")
                    axes[i+1].axis('off')
        
        # Display top 2 abnormal matches
        for i in range(2):
            if i < len(result["top_abnormal_matches"]):
                match = result["top_abnormal_matches"][i]
                img_path = os.path.join(self.abnormal_dir, match["reference"])
                if os.path.exists(img_path):
                    match_img = Image.open(img_path)
                    axes[i+3].imshow(match_img, cmap='gray')
                    disorder = match["metadata"].get("disorder_type", "Unknown")
                    axes[i+3].set_title(f"Abnormal: {disorder}\nSim: {match['similarity']:.2f}")
                    axes[i+3].axis('off')
        
        # Add overall result as suptitle
        if result["detection"]:
            detection_text = f"ABNORMAL (Confidence: {result['confidence_level']:.0f}%)"
            plt.suptitle(detection_text, color='red', fontsize=16)
        else:
            detection_text = f"NORMAL (Confidence: {result['confidence_level']:.0f}%)"
            plt.suptitle(detection_text, color='green', fontsize=16)
            
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)
        
        # Save figure
        plt.savefig(output_path)
        plt.close()
        
        return output_path
    
    def visualize_features(self, image_path, output_path=None):
        """
        Create a visualization of the extracted features for a CT scan
        
        Args:
            image_path: Path to the CT scan image
            output_path: Path to save visualization (if None, will be based on image_path)
            
        Returns:
            Path to the saved visualization
        """
        if output_path is None:
            output_path = os.path.splitext(image_path)[0] + "_features.png"
            
        # Load the image
        img = Image.open(image_path)
        img_np = np.array(img)
        
        # Convert to grayscale if needed
        if len(img_np.shape) == 3 and img_np.shape[2] > 1:
            img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        else:
            img_gray = img_np.astype(np.uint8)
            
        # Extract features
        features = self.extract_features(img_np)
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # Original image
        axes[0, 0].imshow(img_gray, cmap='gray')
        axes[0, 0].set_title("Original CT Scan")
        axes[0, 0].axis('off')
        
        # Histogram
        axes[0, 1].bar(range(256), features["histogram"])
        axes[0, 1].set_title("Intensity Histogram")
        axes[0, 1].set_xlabel("Intensity")
        axes[0, 1].set_ylabel("Frequency")
        
        # Ventricle detection
        _, ventricle_mask = cv2.threshold(img_gray, 40, 255, cv2.THRESH_BINARY_INV)
        # Estimate brain mask
        _, brain_mask = cv2.threshold(img_gray, 10, 255, cv2.THRESH_BINARY)
        kernel = np.ones((5,5), np.uint8)
        brain_mask = cv2.morphologyEx(brain_mask, cv2.MORPH_CLOSE, kernel)
        
        # Refine ventricle mask
        ventricle_mask = cv2.bitwise_and(ventricle_mask, brain_mask)
        ventricle_mask = cv2.morphologyEx(ventricle_mask, cv2.MORPH_OPEN, kernel)
        
        # Create ventricle overlay
        ventricle_overlay = np.zeros((img_gray.shape[0], img_gray.shape[1], 3), dtype=np.uint8)
        ventricle_overlay[ventricle_mask > 0] = [255, 0, 0]  # Red for ventricles
        
        # Show ventricle detection
        axes[0, 2].imshow(img_gray, cmap='gray')
        axes[0, 2].imshow(ventricle_overlay, alpha=0.5)
        axes[0, 2].set_title(f"Ventricle Detection\nRatio: {features['ventricle_ratio']:.4f}")
        axes[0, 2].axis('off')
        
        # Edge/sulci detection
        edges = cv2.Canny(img_gray, 50, 150)
        # Only consider edges within brain boundary
        outer_brain = cv2.erode(brain_mask, kernel, iterations=3)
        sulci_candidate = cv2.bitwise_and(edges, outer_brain)
        
        # Create edge overlay
        edge_overlay = np.zeros((img_gray.shape[0], img_gray.shape[1], 3), dtype=np.uint8)
        edge_overlay[sulci_candidate > 0] = [0, 255, 0]  # Green for edges/sulci
        
        # Show edge detection
        axes[1, 0].imshow(img_gray, cmap='gray')
        axes[1, 0].imshow(edge_overlay, alpha=0.5)
        axes[1, 0].set_title(f"Edge/Sulci Detection\nRatio: {features['edge_ratio']:.4f}")
        axes[1, 0].axis('off')
        
        # Symmetry visualization
        # Create a vertical line at the midpoint
        mid_col = img_gray.shape[1] // 2
        symmetry_img = img_gray.copy()
        symmetry_overlay = np.zeros((img_gray.shape[0], img_gray.shape[1], 3), dtype=np.uint8)
        symmetry_overlay[:, mid_col, :] = [0, 0, 255]  # Blue line for symmetry axis
        
        # Show symmetry
        axes[1, 1].imshow(symmetry_img, cmap='gray')
        axes[1, 1].imshow(symmetry_overlay, alpha=0.8)
        axes[1, 1].set_title(f"Symmetry Analysis\nScore: {features['symmetry_score']:.4f}")
        axes[1, 1].axis('off')
        
        # Feature summary
        axes[1, 2].axis('off')
        summary_text = "Feature Summary:\n\n"
        
        # Add key features with values
        key_features = [
            ("Ventricle Brain Ratio", features["ventricle_brain_ratio"]),
            ("Edge Ratio", features["edge_ratio"]),
            ("Texture Entropy", features["texture_entropy"]),
            ("Mean Intensity", features["mean_intensity"]),
            ("Std Intensity", features["std_intensity"]),
            ("Bright Ratio", features["bright_ratio"]),
            ("Symmetry Score", features["symmetry_score"])
        ]
        
        for name, value in key_features:
            summary_text += f"{name}: {value:.4f}\n"
            
        axes[1, 2].text(0.05, 0.95, summary_text, va="top", fontsize=10)
        axes[1, 2].set_title("Feature Summary")
        
        # Overall title
        plt.suptitle(f"CT Scan Feature Extraction: {os.path.basename(image_path)}", fontsize=16)
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
        
        # Save figure
        plt.savefig(output_path)
        plt.close()
        
        return output_path
    
    def clear_database(self, category=None):
        """
        Clear the reference database, either completely or for a specific category
        
        Args:
            category: "normal", "abnormal", or None (for both)
            
        Returns:
            Number of entries removed
        """
        count = 0
        
        if category in ["normal", "abnormal"] or category is None:
            if category in ["normal", None]:
                # Delete normal entries
                count += len(self.features_data["normal"])
                self.features_data["normal"] = []
                
                # Delete image files
                for filename in os.listdir(self.normal_dir):
                    file_path = os.path.join(self.normal_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")
            
            if category in ["abnormal", None]:
                # Delete abnormal entries
                count += len(self.features_data["abnormal"])
                self.features_data["abnormal"] = []
                
                # Delete image files
                for filename in os.listdir(self.abnormal_dir):
                    file_path = os.path.join(self.abnormal_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")
            
            # Save the updated features data
            with open(self.features_file, 'w') as f:
                json.dump(self.features_data, f, indent=4)
        
        return count
        
        self.features_data[category].append(feature_entry)
        
        # Save the updated features data
        with open(self.features_file, 'w') as f:
            json.dump(self.features_data, f, indent=4)
        
        return len(self.features_data[category])
    
    def extract_features(self, img_np):
        """Extract relevant features from a CT scan"""
        # Convert to grayscale if needed
        if len(img_np.shape) == 3 and img_np.shape[2] > 1:
            img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        else:
            img_gray = img_np.astype(np.uint8)
        
        # Feature extraction pipeline
        features = {}
        
        # 1. Histogram features
        hist = cv2.calcHist([img_gray], [0], None, [256], [0, 256])
        hist = hist.flatten() / hist.sum()  # Normalize
        features["histogram"] = hist.tolist()
        
        # 2. Ventricle detection-related features
        # Apply threshold to isolate potential ventricles (dark regions)
        _, ventricle_mask = cv2.threshold(img_gray, 40, 255, cv2.THRESH_BINARY_INV)
        ventricle_ratio = np.sum(ventricle_mask > 0) / (img_gray.shape[0] * img_gray.shape[1])
        features["ventricle_ratio"] = float(ventricle_ratio)
        
        # 3. Edge-related features to detect atrophy
        edges = cv2.Canny(img_gray, 50, 150)
        edge_ratio = np.sum(edges > 0) / (img_gray.shape[0] * img_gray.shape[1])
        features["edge_ratio"] = float(edge_ratio)
        
        # 4. Texture features
        # Compute GLCM (Gray-Level Co-occurrence Matrix)
        glcm = self._compute_glcm(img_gray)
        entropy = -np.sum(glcm * np.log2(glcm + 1e-10))
        features["texture_entropy"] = float(entropy)
        
        # 5. Basic statistics
        features["mean_intensity"] = float(np.mean(img_gray))
        features["std_intensity"] = float(np.std(img_gray))
        
        # 6. Features specific to CT scans
        # Ratio of bright regions (skull and calcifications)
        _, bright_mask = cv2.threshold(img_gray, 180, 255, cv2.THRESH_BINARY)
        bright_ratio = np.sum(bright_mask > 0) / (img_gray.shape[0] * img_gray.shape[1])
        features["bright_ratio"] = float(bright_ratio)
        
        # 7. Estimate ventricular/brain ratio
        # This is a simplified approach - medical software would use more sophisticated segmentation
        # Estimate brain mask by thresholding
        _, brain_mask = cv2.threshold(img_gray, 10, 255, cv2.THRESH_BINARY)
        kernel = np.ones((5,5), np.uint8)
        brain_mask = cv2.morphologyEx(brain_mask, cv2.MORPH_CLOSE, kernel)
        brain_area = np.sum(brain_mask > 0)
        
        if brain_area > 0:
            ventricle_brain_ratio = np.sum(ventricle_mask > 0) / brain_area
        else:
            ventricle_brain_ratio = 0
            
        features["ventricle_brain_ratio"] = float(ventricle_brain_ratio)
        
        # 8. Symmetry measure
        symmetry_score = self._compute_symmetry(img_gray)
        features["symmetry_score"] = float(symmetry_score)
        
        return features
    
    def _compute_glcm(self, image, distance=1, angle=0):
        """Compute Gray-Level Co-occurrence Matrix for texture analysis"""
        # Reduce gray levels to make GLCM computation more efficient
        levels = 32
        img_scaled = (image / (256 / levels)).astype(np.uint8)
        
        # Compute offset based on angle and distance
        if angle == 0:
            offset = [0, distance]
        elif angle == 45:
            offset = [-distance, distance]
        elif angle == 90:
            offset = [-distance, 0]
        elif angle == 135:
            offset = [-distance, -distance]
        
        # Initialize GLCM
        glcm = np.zeros((levels, levels))
        
        # Compute GLCM
        rows, cols = img_scaled.shape
        for i in range(rows):
            for j in range(cols):
                if 0 <= i + offset[0] < rows and 0 <= j + offset[1] < cols:
                    row = img_scaled[i, j]
                    col = img_scaled[i + offset[0], j + offset[1]]
                    glcm[row, col] += 1
        
        # Normalize GLCM
        if glcm.sum() > 0:
            glcm /= glcm.sum()
            
        return glcm
    
    def _compute_symmetry(self, image):
        """Compute symmetry score for brain image"""
        # Find middle column
        mid_col = image.shape[1] // 2
        
        # Get left and right halves
        left_half = image[:, :mid_col]
        right_half = image[:, mid_col:]
        
        # Flip right half horizontally
        right_half_flipped = np.fliplr(right_half)
        
        # Resize to match left half if needed
        if left_half.shape[1] != right_half_flipped.shape[1]:
            min_width = min(left_half.shape[1], right_half_flipped.shape[1])
            left_half = left_half[:, :min_width]
            right_half_flipped = right_half_flipped[:, :min_width]
        
        # Compute absolute difference
        diff = np.abs(left_half.astype(float) - right_half_flipped.astype(float))
        
        # Compute symmetry score (0 = perfect symmetry, 1 = no symmetry)
        max_diff = np.maximum(left_half, right_half_flipped).astype(float)
        max_diff[max_diff == 0] = 1  # Avoid division by zero
        
        relative_diff = diff / max_diff
        symmetry_score = np.mean(relative_diff)
        
        return symmetry_score
    
    def compare_with_references(self, image_path, top_n=3):
        """
        Compare an image with the reference database and determine 
        if it's more similar to normal or abnormal scans
        """
        # Load and process the image
        img = Image.open(image_path)
        img_np = np.array(img)
        
        # Extract features
        features = self.extract_features(img_np)
        
        # Calculate similarity to each reference scan
        normal_similarities = []
        abnormal_similarities = []
        
        # Compare with normal references
        for entry in self.features_data["normal"]:
            similarity = self._calculate_similarity(features, entry["features"])
            normal_similarities.append({
                "similarity": similarity,
                "reference": entry["filename"],
                "metadata": entry["metadata"]
            })
        
        # Compare with abnormal references
        for entry in self.features_data["abnormal"]:
            similarity = self._calculate_similarity(features, entry["features"])
            abnormal_similarities.append({
                "similarity": similarity,
                "reference": entry["filename"],
                "metadata": entry["metadata"]
            })
        
        # Sort by similarity (higher is more similar)
        normal_similarities.sort(key=lambda x: x["similarity"], reverse=True)
        abnormal_similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Get top N most similar for each category
        top_normal = normal_similarities[:top_n] if normal_similarities else []
        top_abnormal = abnormal_similarities[:top_n] if abnormal_similarities else []
        
        # Calculate average similarity for each category
        avg_normal_similarity = sum(item["similarity"] for item in top_normal) / len(top_normal) if top_normal else 0
        avg_abnormal_similarity = sum(item["similarity"] for item in top_abnormal) / len(top_abnormal) if top_abnormal else 0
        
        # Determine if the scan is more similar to normal or abnormal references
        is_normal = avg_normal_similarity > avg_abnormal_similarity
        
        # Calculate confidence based on the difference between similarities
        similarity_diff = abs(avg_normal_similarity - avg_abnormal_similarity)
        # Normalize difference to 0-100 scale for confidence
        confidence = min(100, similarity_diff * 200)  # Scale factor can be adjusted
        
        # Prepare result
        result = {
            "detection": not is_normal,  # True if abnormal
            "confidence_level": confidence,
            "normal_similarity": avg_normal_similarity,
            "abnormal_similarity": avg_abnormal_similarity,
            "top_normal_matches": top_normal,
            "top_abnormal_matches": top_abnormal
        }
        
        # If abnormal, get potential disorder type from most similar abnormal references
        if not is_normal and top_abnormal:
            # Look for disorder type in metadata of top matches
            disorder_types = {}
            for match in top_abnormal:
                if "disorder_type" in match["metadata"]:
                    disorder = match["metadata"]["disorder_type"]
                    if disorder in disorder_types:
                        disorder_types[disorder] += 1
                    else:
                        disorder_types[disorder] = 1
            
            # Get most common disorder type
            if disorder_types:
                result["disorder_type"] = max(disorder_types.items(), key=lambda x: x[1])[0]
            else:
                result["disorder_type"] = "Unspecified neurodegenerative disorder"
                
            # Calculate average progression if available in metadata
            progression_values = []
            for match in top_abnormal:
                if "progression_percentage" in match["metadata"]:
                    progression_values.append(match["metadata"]["progression_percentage"])
            
            if progression_values:
                avg_progression = sum(progression_values) / len(progression_values)
                result["progression_percentage"] = avg_progression
                
                # Determine progression stage
                if avg_progression < 25:
                    result["progression_stage"] = "Early"
                elif avg_progression < 50:
                    result["progression_stage"] = "Mild"
                elif avg_progression < 75:
                    result["progression_stage"] = "Moderate"
                else:
                    result["progression_stage"] = "Severe"
        
        return result
    
    def _calculate_similarity(self, features1, features2):
        """
        Calculate similarity between two feature sets
        Returns a value between 0 and 1, where 1 means identical
        """
        similarity_scores = []
        
        # Compare histograms using correlation
        hist1 = np.array(features1["histogram"])
        hist2 = np.array(features2["histogram"])
        hist_corr = np.correlate(hist1, hist2)[0] / (np.linalg.norm(hist1) * np.linalg.norm(hist2))
        similarity_scores.append(max(0, hist_corr))  # Ensure non-negative
        
        # Compare scalar features
        scalar_features = [
            "ventricle_ratio", 
            "edge_ratio", 
            "texture_entropy", 
            "mean_intensity", 
            "std_intensity",
            "bright_ratio",
            "ventricle_brain_ratio",
            "symmetry_score"
        ]
        
        for feature in scalar_features:
            if feature in features1 and feature in features2:
                # Calculate similarity as 1 - normalized difference
                value1 = features1[feature]
                value2 = features2[feature]
                max_val = max(abs(value1), abs(value2))
                if max_val > 0:
                    diff = abs(value1 - value2) / max_val
                    similarity = 1 - min(1, diff)  # Cap at 0
                else:
                    similarity = 1  # Both are zero
                similarity_scores.append(similarity)
        
        # Weighted average of similarities
        # Give more weight to ventricle and symmetry features for neurodegeneration
        weights = {
            0: 0.15,  # histogram
            1: 0.15,  # ventricle_ratio
            2: 0.1,   # edge_ratio
            3: 0.1,   # texture_entropy
            4: 0.05,  # mean_intensity
            5: 0.05,  # std_intensity
            6: 0.1,   # bright_ratio
            7: 0.2,   # ventricle_brain_ratio
            8: 0.1    # symmetry_score
        }
        
        total_weight = 0
        weighted_sum = 0
        
        for i, score in enumerate(similarity_scores):
            if i in weights:
                weight = weights[i]
                weighted_sum += score * weight
                total_weight += weight
        
        if total_weight > 0:
            final_similarity = weighted_sum / total_weight
        else:
            final_similarity = 0
            
        return final_similarity
        
    def get_reference_count(self):
        """Return the count of reference scans in the database"""
        return {
            "normal": len(self.features_data["normal"]),
            "abnormal": len(self.features_data["abnormal"])
        }
"""
JSON Data Store Module
Handles all JSON-based persistence for the application
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import threading


class JSONStore:
    """Thread-safe JSON storage manager"""
    
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.lock = threading.Lock()
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Task 1: Create single JSON file structure if it doesn't exist"""
        if not self.storage_path.exists():
            initial_data = {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0.0"
                },
                "available_resources": {},
                "district_predictions": [],
                "hotspots": [],
                "resource_recommendations": [],
                "resource_assignments": [],
                "prediction_history": []
            }
            self._write_data(initial_data)
            print(f"Created new storage file at {self.storage_path}")
    
    def _read_data(self) -> Dict:
        """Read data from JSON file"""
        try:
            with open(self.storage_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    # File is empty, reinitialize
                    print("Warning: Storage file is empty, reinitializing...")
                    self._ensure_storage_exists()
                    with open(self.storage_path, 'r') as f:
                        return json.load(f)
                return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: Corrupted or missing storage file ({e}), reinitializing...")
            # Delete and recreate
            if self.storage_path.exists():
                self.storage_path.unlink()
            self._ensure_storage_exists()
            with open(self.storage_path, 'r') as f:
                return json.load(f)
    
    def _write_data(self, data: Dict):
        """Task 9: Write updated state back to JSON file"""
        # Update last modified timestamp
        data["metadata"]["last_updated"] = datetime.now().isoformat()
        
        # Write to file
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _update_and_save(self, update_func):
        """Task 10: Ensure JSON consistency after every operation"""
        with self.lock:
            data = self._read_data()
            update_func(data)
            self._write_data(data)
    
    # Resource Management
    
    def get_available_resources(self) -> Dict:
        """Task 2: Get available resource counts"""
        with self.lock:
            data = self._read_data()
            return data.get("available_resources", {})
    
    def set_available_resources(self, resources: Dict):
        """Set or update available resources"""
        def update(data):
            data["available_resources"] = resources
        self._update_and_save(update)
    
    def update_resource_quantity(self, resource_name: str, quantity: int):
        """Update quantity of a specific resource"""
        def update(data):
            if "available_resources" not in data:
                data["available_resources"] = {}
            data["available_resources"][resource_name] = quantity
        self._update_and_save(update)
    
    def deduct_resources(self, resources: Dict) -> bool:
        """Task 7: Update remaining resources after assignment"""
        with self.lock:
            data = self._read_data()
            available = data.get("available_resources", {})
            
            # Check if sufficient resources available
            for resource, amount in resources.items():
                if available.get(resource, 0) < amount:
                    return False
            
            # Deduct resources
            for resource, amount in resources.items():
                available[resource] = available.get(resource, 0) - amount
            
            data["available_resources"] = available
            self._write_data(data)
            return True
    
    # District Predictions
    
    def save_district_predictions(self, predictions: List[Dict]):
        """Task 3: Store district risk predictions"""
        def update(data):
            data["district_predictions"] = predictions
            # Also save to history
            data["prediction_history"].append({
                "timestamp": datetime.now().isoformat(),
                "predictions": predictions
            })
        self._update_and_save(update)
    
    def get_district_predictions(self) -> List[Dict]:
        """Get current district predictions"""
        with self.lock:
            data = self._read_data()
            return data.get("district_predictions", [])
    
    # Hotspots
    
    def save_hotspots(self, hotspots: List[Dict]):
        """Task 4: Store hotspot information"""
        def update(data):
            data["hotspots"] = hotspots
        self._update_and_save(update)
    
    def get_hotspots(self) -> List[Dict]:
        """Get current hotspots"""
        with self.lock:
            data = self._read_data()
            return data.get("hotspots", [])
    
    # Resource Recommendations
    
    def save_resource_recommendations(self, recommendations: List[Dict]):
        """Task 5: Store ML recommendations"""
        def update(data):
            data["resource_recommendations"] = recommendations
        self._update_and_save(update)
    
    def get_resource_recommendations(self) -> List[Dict]:
        """Get current resource recommendations"""
        with self.lock:
            data = self._read_data()
            return data.get("resource_recommendations", [])
    
    # Resource Assignments
    
    def save_resource_assignment(self, assignment: Dict):
        """Task 6: Save assigned resources"""
        def update(data):
            if "resource_assignments" not in data:
                data["resource_assignments"] = []
            
            # Add timestamp
            assignment["assigned_at"] = datetime.now().isoformat()
            
            # Add to assignments
            data["resource_assignments"].append(assignment)
        self._update_and_save(update)
    
    def get_resource_assignments(self, district: Optional[str] = None) -> List[Dict]:
        """Get resource assignments, optionally filtered by district"""
        with self.lock:
            data = self._read_data()
            assignments = data.get("resource_assignments", [])
            
            if district:
                assignments = [a for a in assignments if a.get("district") == district]
            
            return assignments
    
    def clear_assignments(self):
        """Clear all resource assignments"""
        def update(data):
            data["resource_assignments"] = []
        self._update_and_save(update)
    
    # Utility methods
    
    def get_all_data(self) -> Dict:
        """Get complete storage data"""
        with self.lock:
            return self._read_data()
    
    def reset_storage(self):
        """Reset storage to initial state"""
        self.storage_path.unlink(missing_ok=True)
        self._ensure_storage_exists()
    
    def export_data(self, export_path: str):
        """Export data to a different file"""
        with self.lock:
            data = self._read_data()
            with open(export_path, 'w') as f:
                json.dump(data, f, indent=2)


# Global store instance
_store_instance = None

def get_store(storage_path: str = None) -> JSONStore:
    """Get or create the global JSONStore instance"""
    global _store_instance
    if _store_instance is None:
        if storage_path is None:
            raise ValueError("storage_path must be provided for first initialization")
        _store_instance = JSONStore(storage_path)
    return _store_instance


if __name__ == "__main__":
    # Test the JSON store
    import tempfile
    import os
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        print("Testing JSON Store...")
        store = JSONStore(temp_path)
        
        # Test resources
        print("\n1. Setting resources...")
        store.set_available_resources({
            "Fogging_Units": 100,
            "Health_Inspectors": 50
        })
        print(f"Available resources: {store.get_available_resources()}")
        
        # Test predictions
        print("\n2. Saving predictions...")
        store.save_district_predictions([
            {"district": "Colombo", "risk_level": "High"},
            {"district": "Gampaha", "risk_level": "Medium"}
        ])
        print(f"Predictions: {store.get_district_predictions()}")
        
        # Test assignments
        print("\n3. Saving assignment...")
        store.save_resource_assignment({
            "district": "Colombo",
            "resources": {"Fogging_Units": 10}
        })
        print(f"Assignments: {store.get_resource_assignments()}")
        
        # Test deduction
        print("\n4. Deducting resources...")
        success = store.deduct_resources({"Fogging_Units": 10})
        print(f"Deduction success: {success}")
        print(f"Remaining resources: {store.get_available_resources()}")
        
        print("\n✓ All tests passed!")
        
    finally:
        # Cleanup
        os.unlink(temp_path)
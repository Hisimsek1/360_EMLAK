"""
Data Manager for 360 Emlak Platform
Advanced JSON database manager with file locking, backups, and CRUD operations
Windows-compatible implementation
"""
import json
import os
import shutil
from datetime import datetime
from typing import Optional, List, Dict, Any, Callable
from threading import Lock
from pathlib import Path


class DataManager:
    """
    Advanced JSON data manager with thread-safe operations,
    automatic backups, and CRUD operations
    """
    
    def __init__(self, data_file: str, backup_enabled: bool = True, max_backups: int = 5):
        """
        Initialize DataManager
        
        Args:
            data_file: Path to JSON data file
            backup_enabled: Enable automatic backups
            max_backups: Maximum number of backup files to keep
        """
        self.data_file = Path(data_file)
        self.backup_enabled = backup_enabled
        self.max_backups = max_backups
        self.lock = Lock()
        
        # Create data directory if not exists
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize data file if not exists
        self._initialize_data_file()
    
    def _initialize_data_file(self):
        """Create initial data file if it doesn't exist"""
        if not self.data_file.exists():
            initial_data = {
                "users": [],
                "properties": [],
                "settings": {},
                "pages": {},
                "categories": [],
                "cities": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            self._write_json(initial_data)
    
    def _read_json(self) -> Dict[str, Any]:
        """
        Read JSON data from file
        
        Returns:
            Dict: Parsed JSON data
        """
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading data file: {e}")
            return self._get_empty_data()
    
    def _write_json(self, data: Dict[str, Any]):
        """
        Write JSON data to file
        
        Args:
            data: Data to write
        """
        # Update timestamp
        data['updated_at'] = datetime.now().isoformat()
        
        # Write to temporary file first (atomic write)
        temp_file = self.data_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Replace original file
        shutil.move(str(temp_file), str(self.data_file))
    
    def _get_empty_data(self) -> Dict[str, Any]:
        """Get empty data structure"""
        return {
            "users": [],
            "properties": [],
            "settings": {},
            "pages": {},
            "categories": [],
            "cities": []
        }
    
    def _create_backup(self):
        """Create backup of current data file"""
        if not self.backup_enabled or not self.data_file.exists():
            return
        
        try:
            # Create backup directory
            backup_dir = self.data_file.parent / 'backups'
            backup_dir.mkdir(exist_ok=True)
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_dir / f"data_backup_{timestamp}.json"
            
            # Copy current file to backup
            shutil.copy2(self.data_file, backup_file)
            
            # Clean old backups
            self._cleanup_old_backups(backup_dir)
            
            print(f"Backup created: {backup_file.name}")
        except Exception as e:
            print(f"Error creating backup: {e}")
    
    def _cleanup_old_backups(self, backup_dir: Path):
        """Remove old backup files, keeping only max_backups most recent"""
        backups = sorted(backup_dir.glob('data_backup_*.json'), reverse=True)
        
        # Remove old backups
        for old_backup in backups[self.max_backups:]:
            try:
                old_backup.unlink()
                print(f"Removed old backup: {old_backup.name}")
            except Exception as e:
                print(f"Error removing old backup: {e}")
    
    # Core CRUD Operations
    
    def read_all(self) -> Dict[str, Any]:
        """
        Read all data (thread-safe)
        
        Returns:
            Dict: All data
        """
        with self.lock:
            return self._read_json()
    
    def write_all(self, data: Dict[str, Any]):
        """
        Write all data (thread-safe)
        
        Args:
            data: Complete data structure
        """
        with self.lock:
            self._create_backup()
            self._write_json(data)
    
    def get_collection(self, collection_name: str) -> List[Dict]:
        """
        Get a collection
        
        Args:
            collection_name: Name of collection
        
        Returns:
            List: Collection items
        """
        data = self.read_all()
        return data.get(collection_name, [])
    
    def set_collection(self, collection_name: str, collection_data: List[Dict]):
        """
        Replace entire collection
        
        Args:
            collection_name: Name of collection
            collection_data: New collection data
        """
        with self.lock:
            data = self._read_json()
            self._create_backup()
            data[collection_name] = collection_data
            self._write_json(data)
    
    def find_one(self, collection_name: str, filter_func: Callable[[Dict], bool]) -> Optional[Dict]:
        """
        Find single item in collection
        
        Args:
            collection_name: Name of collection
            filter_func: Function to filter items
        
        Returns:
            Optional[Dict]: Found item or None
        """
        collection = self.get_collection(collection_name)
        for item in collection:
            if filter_func(item):
                return item
        return None
    
    def find_many(self, collection_name: str, filter_func: Callable[[Dict], bool]) -> List[Dict]:
        """
        Find multiple items in collection
        
        Args:
            collection_name: Name of collection
            filter_func: Function to filter items
        
        Returns:
            List[Dict]: Found items
        """
        collection = self.get_collection(collection_name)
        return [item for item in collection if filter_func(item)]
    
    def insert_one(self, collection_name: str, item: Dict) -> Dict:
        """
        Insert single item into collection
        
        Args:
            collection_name: Name of collection
            item: Item to insert
        
        Returns:
            Dict: Inserted item
        """
        with self.lock:
            data = self._read_json()
            self._create_backup()
            
            if collection_name not in data:
                data[collection_name] = []
            
            # Add timestamps
            item['created_at'] = datetime.now().isoformat()
            item['updated_at'] = datetime.now().isoformat()
            
            data[collection_name].append(item)
            self._write_json(data)
            
            return item
    
    def update_one(self, collection_name: str, filter_func: Callable[[Dict], bool], 
                   update_data: Dict) -> bool:
        """
        Update single item in collection
        
        Args:
            collection_name: Name of collection
            filter_func: Function to find item
            update_data: Data to update
        
        Returns:
            bool: True if updated, False otherwise
        """
        with self.lock:
            data = self._read_json()
            collection = data.get(collection_name, [])
            
            for i, item in enumerate(collection):
                if filter_func(item):
                    self._create_backup()
                    # Update item
                    update_data['updated_at'] = datetime.now().isoformat()
                    collection[i] = {**item, **update_data}
                    data[collection_name] = collection
                    self._write_json(data)
                    return True
            
            return False
    
    def delete_one(self, collection_name: str, filter_func: Callable[[Dict], bool]) -> bool:
        """
        Delete single item from collection
        
        Args:
            collection_name: Name of collection
            filter_func: Function to find item
        
        Returns:
            bool: True if deleted, False otherwise
        """
        with self.lock:
            data = self._read_json()
            collection = data.get(collection_name, [])
            initial_length = len(collection)
            
            # Filter out matching item
            collection = [item for item in collection if not filter_func(item)]
            
            if len(collection) < initial_length:
                self._create_backup()
                data[collection_name] = collection
                self._write_json(data)
                return True
            
            return False
    
    def delete_many(self, collection_name: str, filter_func: Callable[[Dict], bool]) -> int:
        """
        Delete multiple items from collection
        
        Args:
            collection_name: Name of collection
            filter_func: Function to filter items
        
        Returns:
            int: Number of deleted items
        """
        with self.lock:
            data = self._read_json()
            collection = data.get(collection_name, [])
            initial_length = len(collection)
            
            # Filter out matching items
            collection = [item for item in collection if not filter_func(item)]
            deleted_count = initial_length - len(collection)
            
            if deleted_count > 0:
                self._create_backup()
                data[collection_name] = collection
                self._write_json(data)
            
            return deleted_count
    
    def count(self, collection_name: str, filter_func: Optional[Callable[[Dict], bool]] = None) -> int:
        """
        Count items in collection
        
        Args:
            collection_name: Name of collection
            filter_func: Optional filter function
        
        Returns:
            int: Item count
        """
        collection = self.get_collection(collection_name)
        
        if filter_func is None:
            return len(collection)
        
        return len([item for item in collection if filter_func(item)])
    
    # Specialized operations
    
    def get_settings(self) -> Dict:
        """Get site settings"""
        data = self.read_all()
        return data.get('settings', {})
    
    def update_settings(self, settings: Dict):
        """Update site settings"""
        with self.lock:
            data = self._read_json()
            self._create_backup()
            data['settings'] = {**data.get('settings', {}), **settings}
            self._write_json(data)
    
    def get_page(self, slug: str) -> Optional[Dict]:
        """Get page by slug"""
        data = self.read_all()
        pages = data.get('pages', {})
        return pages.get(slug)
    
    def restore_from_backup(self, backup_filename: str) -> bool:
        """
        Restore data from backup file
        
        Args:
            backup_filename: Name of backup file
        
        Returns:
            bool: True if successful
        """
        try:
            backup_dir = self.data_file.parent / 'backups'
            backup_file = backup_dir / backup_filename
            
            if not backup_file.exists():
                print(f"Backup file not found: {backup_filename}")
                return False
            
            # Create backup of current state before restoring
            self._create_backup()
            
            # Copy backup to main file
            shutil.copy2(backup_file, self.data_file)
            print(f"Data restored from: {backup_filename}")
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    def list_backups(self) -> List[str]:
        """
        List available backup files
        
        Returns:
            List[str]: Backup filenames
        """
        backup_dir = self.data_file.parent / 'backups'
        if not backup_dir.exists():
            return []
        
        backups = sorted(backup_dir.glob('data_backup_*.json'), reverse=True)
        return [backup.name for backup in backups]


# Global instance
_data_manager: Optional[DataManager] = None


def init_data_manager(data_file: str, backup_enabled: bool = True, max_backups: int = 5):
    """
    Initialize global data manager
    
    Args:
        data_file: Path to JSON data file
        backup_enabled: Enable automatic backups
        max_backups: Maximum number of backup files
    """
    global _data_manager
    _data_manager = DataManager(data_file, backup_enabled, max_backups)


def get_data_manager() -> DataManager:
    """
    Get global data manager instance
    
    Returns:
        DataManager: Global instance
    """
    if _data_manager is None:
        from flask import current_app
        init_data_manager(
            current_app.config['DATA_FILE'],
            backup_enabled=True,
            max_backups=5
        )
    return _data_manager

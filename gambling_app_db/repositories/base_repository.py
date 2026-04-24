"""
Base repository class implementing the Repository Pattern.
Provides CRUD operations abstraction.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from gambling_app_db.database import DatabaseConnection


class BaseRepository(ABC):
    """Abstract base repository for CRUD operations."""
    
    def __init__(self):
        """Initialize repository with database connection."""
        self.db = DatabaseConnection.get_instance()
    
    @abstractmethod
    def table_name(self) -> str:
        """Get the table name for this repository."""
        pass
    
    def create(self, data: Dict[str, Any]) -> int:
        """
        Create a new record.
        
        Args:
            data: Dictionary of field values
        
        Returns:
            ID of created record
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {self.table_name()} ({columns}) VALUES ({placeholders})"
        
        return self.db.execute_insert(query, tuple(data.values()))
    
    def read(self, id_value: Any, id_field: str = None) -> Optional[Dict[str, Any]]:
        """
        Read a single record by ID.
        
        Args:
            id_value: ID value to search for
            id_field: Name of the ID field (defaults to {table}_id)
        
        Returns:
            Record dictionary or None if not found
        """
        if id_field is None:
            id_field = f"{self.table_name().rstrip('s')}_id"
        
        query = f"SELECT * FROM {self.table_name()} WHERE {id_field} = %s"
        results = self.db.execute_query(query, (id_value,))
        
        return self._row_to_dict(results[0]) if results else None
    
    def update(self, id_value: Any, data: Dict[str, Any], id_field: str = None) -> int:
        """
        Update a record.
        
        Args:
            id_value: ID of record to update
            data: Dictionary of fields to update
            id_field: Name of the ID field
        
        Returns:
            Number of affected rows
        """
        if id_field is None:
            id_field = f"{self.table_name().rstrip('s')}_id"
        
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE {self.table_name()} SET {set_clause} WHERE {id_field} = %s"
        
        values = list(data.values()) + [id_value]
        return self.db.execute_update(query, tuple(values))
    
    def delete(self, id_value: Any, id_field: str = None) -> int:
        """
        Delete a record.
        
        Args:
            id_value: ID of record to delete
            id_field: Name of the ID field
        
        Returns:
            Number of affected rows
        """
        if id_field is None:
            id_field = f"{self.table_name().rstrip('s')}_id"
        
        query = f"DELETE FROM {self.table_name()} WHERE {id_field} = %s"
        return self.db.execute_delete(query, (id_value,))
    
    def read_all(self) -> List[Dict[str, Any]]:
        """
        Read all records.
        
        Returns:
            List of all records
        """
        query = f"SELECT * FROM {self.table_name()}"
        results = self.db.execute_query(query)
        return [self._row_to_dict(row) for row in results]
    
    def execute_custom_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute a custom SELECT query.
        
        Args:
            query: SQL query
            params: Query parameters
        
        Returns:
            List of results
        """
        results = self.db.execute_query(query, params)
        return [self._row_to_dict(row) for row in results]
    
    @staticmethod
    def _row_to_dict(row: tuple) -> Dict[str, Any]:
        """
        Convert row tuple to dictionary.
        Note: This is a simple implementation. 
        Override in subclasses for custom mapping.
        """
        return dict(row) if isinstance(row, dict) else {"row": row}

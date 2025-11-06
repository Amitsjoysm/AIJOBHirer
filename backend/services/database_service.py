from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import os
import uuid

class DatabaseService:
    def __init__(self, db):
        self.db = db
    
    # Generic CRUD operations
    async def create_document(self, collection: str, data: dict) -> dict:
        """Create a new document in the specified collection"""
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        if 'created_at' not in data:
            data['created_at'] = datetime.now(timezone.utc).isoformat()
        if 'updated_at' not in data:
            data['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        result = await self.db[collection].insert_one(data)
        return data
    
    async def get_document(self, collection: str, query: dict) -> Optional[dict]:
        """Get a single document from the specified collection"""
        doc = await self.db[collection].find_one(query, {"_id": 0})
        return doc
    
    async def get_documents(self, collection: str, query: dict = {}, limit: int = 1000, skip: int = 0, sort: List[tuple] = None) -> List[dict]:
        """Get multiple documents from the specified collection"""
        cursor = self.db[collection].find(query, {"_id": 0})
        
        if sort:
            cursor = cursor.sort(sort)
        
        cursor = cursor.skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        return documents
    
    async def update_document(self, collection: str, query: dict, update_data: dict) -> bool:
        """Update a document in the specified collection"""
        update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        result = await self.db[collection].update_one(query, {"$set": update_data})
        return result.modified_count > 0
    
    async def delete_document(self, collection: str, query: dict) -> bool:
        """Delete a document from the specified collection"""
        result = await self.db[collection].delete_one(query)
        return result.deleted_count > 0
    
    async def count_documents(self, collection: str, query: dict = {}) -> int:
        """Count documents in the specified collection"""
        count = await self.db[collection].count_documents(query)
        return count

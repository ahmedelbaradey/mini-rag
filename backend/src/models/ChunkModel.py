from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DatabaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne



class ChunkModel(BaseDataModel):

    def __init__(self, db_client:object):
        super().__init__(db_client=db_client)
        self.collection= self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
    
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_colections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_PROJECT_NAME not in all_colections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
            indexes = DataChunk.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique =index["unique"]
                )

    async def create_chunk(self,chunk :DataChunk):
        result= await self.collection.insert_one(chunk.dict(by_alias=True,exclude_unset = True))
        chunk._id = result.inserted_id
        return chunk
    
    async def get_chunk(self,chunk_id:str):
        result = await self.collection.find_one({
            "_id":ObjectId(chunk_id)
        })
        if result is None:
            return None
        return DataChunk(**result)
    
    async def insert_many_chunks(self,chunks:list,batch_size:int = 100):

        for i in range(0,len(chunks),batch_size):
            batch = chunks[i:i+batch_size]

            operations = [
                InsertOne(chunk.dict(by_alias=True,exclude_unset = True))
                for chunk in batch
            ]
            if operations:  # Only execute if there are operations
                await self.collection.bulk_write(operations)

        return len(chunks)

    async def delete_chunks_by_project_id(self,project_id:ObjectId):
        result = await self.collection.delete_many({
            "chunk_project_id":project_id
        })
        return result.deleted_count
    
    async def get_project_chunks(self, project_id: ObjectId, last_id: ObjectId = None, page_size: int = 500):
        query = {"chunk_project_id": project_id}
        if last_id:
            query["_id"] = {"$gt": last_id} # Only get records AFTER the last one
        
        results = await self.collection.find(query).sort("_id", 1).limit(page_size).to_list(length=None)
        return [DataChunk(**record) for record in results]
    
 

    


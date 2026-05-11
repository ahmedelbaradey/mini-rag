from qdrant_client import models, QdrantClient 
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
import logging
from typing import List
from models.db_schemes import RetrievedDocument

class QdrantDBProvider(VectorDBInterface):

    def __init__(self, db_path: str, distance_method: str):

        self.client = None
        self.db_path = db_path
        self.distance_method = None
 
        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)
    
    def list_all_collections(self) -> List:
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)
    
    def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name):
            return self.client.delete_collection(collection_name=collection_name)
        
    def create_collection(self, collection_name: str, 
                                embedding_size: int,
                                do_reset: bool = False):
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)
        
        if not self.is_collection_existed(collection_name):
            self.logger.info(f"Creating new Qdrant collection: {collection_name}")
            _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method,
                    multivector_config=models.MultiVectorConfig(
                    comparator=models.MultiVectorComparator.MAX_SIM
                   )
                )
            )

            return True
        
        return False
    
    def insert_one(self, collection_name: str, text: str, vector: list,
                         metadata: dict = None, 
                         record_id: str = None):
        
        if not self.is_collection_existed(collection_name):
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False
        
        try:
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id=[record_id],
                        vector=vector,
                        payload={
                            "text": text, "metadata": metadata
                        }
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error while inserting batch: {e}")
            return False

        return True
    
    def insert_many(self, collection_name: str, texts: list, vectors: list, metadata: list = None, record_ids: list = None):
        # Ensure metadata and ids match the batch size if not provided
        if metadata is None: metadata = [None] * len(texts)
        if record_ids is None: record_ids = list(range(0, len(texts)))
    
        # 1. Map your lists into PointStruct objects
        points = [
            models.PointStruct(
                id=record_ids[x],
                vector=vectors[x],
                payload={
                    "text": texts[x],
                    "metadata": metadata[x]
                }
            )
            for x in range(len(texts))
        ]


    
        try:
            # 2. Use upsert for pre-batched PointStructs
            self.client.upsert(
                collection_name=collection_name,
                points=points,
                wait=False  # Crucial for speed when handling millions of records
            )
            return True
        except Exception as e:
            self.logger.error(f"Error while inserting batch: {e}")
            return False
        
    def search_by_vector(self, collection_name: str, vector: list, limit: int):
        try:
            results =  self.client.query_points(
                collection_name=collection_name,
                query=vector,
                limit=limit
            )
            if not results:
                return None
            result =  [
                RetrievedDocument(**{
                    "score": result.score,
                    "text": result.payload["text"],
                })
                for result in results.points
            ]


            return result
        except Exception as e:
            self.logger.error(f"Error while search vector: {e}")
            return False
        
    

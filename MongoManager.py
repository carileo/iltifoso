from pymongo import MongoClient
from pymongo.server_api import ServerApi


class MongoDBManager:
    def __init__(self, uri, db_name, collection_name):
        self.client = MongoClient(uri,server_api=ServerApi('1'))
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_document(self, document):
        """Inserisce un documento nella collezione."""
        result = self.collection.insert_one(document)
        return result.inserted_id

    def find_document(self, query={}):
        """Trova il primo documento che corrisponde alla query."""
        return self.collection.find_one(query)

    def find_all_documents(self, query={}):
        """Trova tutti i documenti che corrispondono alla query."""
        return list(self.collection.find(query))

    def update_document(self, query, new_values):
        """Aggiorna un documento che corrisponde alla query."""
        updated_doc = {"$set": new_values}
        result = self.collection.update_one(query, updated_doc)
        return result.modified_count

    def delete_document(self, query):
        """Elimina un documento che corrisponde alla query."""
        result = self.collection.delete_one(query)
        return result.deleted_count
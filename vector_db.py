from typing import List, Dict

import config
from langchain_chroma import Chroma


class VectorDB:
    def __init__(self):
        self.vectordb = Chroma(
            persist_directory=config.PERSIST_DIR,
            collection_name=config.COLLECTION_NAME,
            embedding_function=config.EMBEDDER
        )

    def similarity_search(self, query: str, k: int = 5):

        return self.vectordb.similarity_search(query=query, k=k)

    def have_data(self):
        count = self.vectordb._collection.count()

        if count == 0:
            print(f"Collection '{config.COLLECTION_NAME}' exists but is empty.")
        else:
            print(f"Collection '{config.COLLECTION_NAME}' has {count} documents.")
            sample_docs = self.vectordb._collection.peek(limit=3)
            print("Sample documents:", sample_docs)

        return count

    def upload_data(self, db_entries: List[Dict]):

        texts = [entry["page_content"] for entry in db_entries]
        metadatas = [entry["metadata"] for entry in db_entries]
        embeddings = [entry["vector"] for entry in db_entries]

        self.vectordb.add_texts(
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )


if __name__ == "__main__":
    vector_db = VectorDB()

    results = vector_db.similarity_search(query="покарання за крадіжку", k=5)
    # results = vector_db.similarity_search(query="що буде у разі призначення більш м'якого покарання", k=5)
    for i, doc in enumerate(results):
        print(f"Result {i + 1}")
        print(f"Content: {doc.page_content}...")
        print(f"Metadata: {doc.metadata}")

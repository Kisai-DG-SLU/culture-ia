import os
import json
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()


class VectorStoreManager:
    def __init__(self, index_path="data/faiss_index"):
        self.index_path = index_path
        self.embeddings = self._get_embeddings()

    def _get_embeddings(self):
        mistral_key = os.getenv("MISTRAL_API_KEY")
        if mistral_key and mistral_key != "votre_cle_mistral_ici":
            print("Using Mistral AI Embeddings")
            return MistralAIEmbeddings(api_key=mistral_key)

        print(
            "MISTRAL_API_KEY not found or default. Falling back to Sentence-Transformers (Local)."
        )
        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def create_index(self, processed_events_file="data/processed_events.json"):
        if not os.path.exists(processed_events_file):
            print(f"File {processed_events_file} not found.")
            return

        with open(processed_events_file, "r", encoding="utf-8") as f:
            events = json.load(f)

        documents = []
        for event in events:
            doc = Document(page_content=event["text"], metadata=event["metadata"])
            documents.append(doc)

        if not documents:
            print("No documents to index.")
            return

        # Découpage en chunks pour gérer les textes longs
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        split_docs = text_splitter.split_documents(documents)
        print(f"Split {len(documents)} events into {len(split_docs)} chunks.")

        vectorstore = FAISS.from_documents(split_docs, self.embeddings)
        vectorstore.save_local(self.index_path)
        print(f"Index created and saved to {self.index_path}")

    def load_index(self):
        if os.path.exists(self.index_path):
            return FAISS.load_local(
                self.index_path, self.embeddings, allow_dangerous_deserialization=True
            )

        print(f"Index path {self.index_path} does not exist.")
        return None


if __name__ == "__main__":
    manager = VectorStoreManager()
    manager.create_index()

import os
import locale
from datetime import datetime
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from src.core.vectorstore import VectorStoreManager

load_dotenv()

# Essayer de mettre la locale en français pour la date, sinon défaut
try:
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
except locale.Error:
    pass  # On reste sur la locale par défaut si fr_FR n'est pas dispo


class RAGChain:
    def __init__(self):
        self.vectorstore_manager = VectorStoreManager()
        self.vectorstore = self.vectorstore_manager.load_index()
        if self.vectorstore is None:
            raise ValueError("Vector store not found. Please run vectorstore.py first.")

        # K=2 est le compromis idéal pour ce petit dataset (2 événements au total)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 2})
        self.llm = self._init_llm()
        self.prompt = self._get_prompt_template()
        self.chain = self._build_chain()

    def _init_llm(self):
        mistral_key = os.getenv("MISTRAL_API_KEY")
        return ChatMistralAI(api_key=mistral_key, model="mistral-tiny")

    def _get_prompt_template(self):
        template = """
        Tu es un assistant expert en événements culturels pour Puls-Events.
        Nous sommes le : {current_date}.
        
        CONSIGNES STRICTES :
        1. Utilise EXCLUSIVEMENT les éléments de contexte ci-dessous.
        2. Si la réponse n'est pas dans le contexte, dis : "Désolé, je n'ai pas cette information dans ma base."
        3. Ne cite que les dates futures ou en cours par rapport à la date du jour.
        4. Sois précis et factuel. Pas d'interprétation.

        CONTEXTE :
        {context}

        QUESTION : {question}

        RÉPONSE :
        """
        return ChatPromptTemplate.from_template(template)

    def _get_current_date(self, _):
        """Retourne la date actuelle formatée."""
        return datetime.now().strftime("%A %d %B %Y")

    def _format_docs(self, docs):
        # Déduplication basée sur l'URL pour ne pas répéter le même événement complet
        unique_docs = {}
        for doc in docs:
            url = doc.metadata.get("url")
            if url and url not in unique_docs:
                unique_docs[url] = doc.metadata.get("full_context", doc.page_content)
            elif not url:
                # Fallback si pas d'URL (ne devrait pas arriver avec nos données)
                unique_docs[str(hash(doc.page_content))] = doc.page_content

        return "\n\n".join(unique_docs.values())

    def _build_chain(self):
        chain = (
            {
                "context": self.retriever | self._format_docs,
                "question": RunnablePassthrough(),
                "current_date": self._get_current_date,
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        return chain

    def ask(self, query: str):
        return self.chain.invoke(query)


if __name__ == "__main__":
    rag = RAGChain()
    response = rag.ask("Quels sont les événements sur la cuisine sauvage ?")
    print("Question: Quels sont les événements sur la cuisine sauvage ?")
    print(f"Réponse: {response}")

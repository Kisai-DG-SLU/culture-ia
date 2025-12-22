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
        # Température à 0 pour une fidélité maximale aux données
        return ChatMistralAI(api_key=mistral_key, model="mistral-tiny", temperature=0)

    def _get_prompt_template(self):
        template = """
        Tu es Sophia, l'assistante experte en événements culturels pour Puls-Events.
        Nous sommes le : {current_date}.
        
        CONSIGNES STRICTES :
        1. **ANALYSE L'INTENTION** :
           - Si l'utilisateur dit simplement "Bonjour", "Salut", "Coucou" ou demande comment tu vas **SANS** poser de question spécifique :
             Réponds chaleureusement, présente-toi brièvement et demande quel type de sortie il recherche.
             **NE LISTE PAS D'ÉVÉNEMENTS DANS CE CAS.**
           - Si l'utilisateur pose une question ou cherche une sortie, passe à l'étape 2.

        2. **RECOMMANDATION (Uniquement si demandé)** :
           - Tu dois RECOMMANDER uniquement des événements dont la date est FUTURE ou AUJOURD'HUI par rapport à la date actuelle ({current_date}).
           - REGARDE la section "Détail des dates" dans le contexte.
             - Si une date est sous "ARCHIVES" ou "DATES PASSÉES", IGNORE-LA.
             - Si une date est sous "DATES À VENIR", tu peux la proposer.
           - Si l'utilisateur demande "ce week-end", calcule la date du prochain samedi/dimanche et vérifie si elle est listée.
           - NE JAMAIS inventer de dates. Si aucune date future ne correspond, dis clairement : "Je n'ai pas trouvé d'événement pour cette date."
           - Sois précis : donne le jour, le numéro et le mois (ex: "Lundi 22 Décembre").

        CONTEXTE :
        {context}

        QUESTION : {question}

        RÉPONSE FACTUELLE :
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

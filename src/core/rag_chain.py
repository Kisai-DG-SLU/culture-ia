import os
import locale
from datetime import datetime, timedelta
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

    def _get_weekend_dates(self, _):
        """Calcule les dates du prochain week-end (Samedi et Dimanche)."""
        now = datetime.now()
        # 5 = Samedi, 6 = Dimanche
        days_ahead = 5 - now.weekday()
        if days_ahead <= 0:  # Si on est samedi (0) ou dimanche (-1)
            # Dimanche -> Samedi prochain (ou on considère le WE actuel fini ?)
            # Simplification : Si Dimanche, on donne le WE prochain
            if days_ahead < 0:
                days_ahead += 7

        if now.weekday() >= 5:  # Si on est déjà le WE
            # On donne les dates du WE en cours pour être pertinent
            saturday = now - timedelta(days=now.weekday() - 5)
        else:
            saturday = now + timedelta(days=days_ahead)

        sunday = saturday + timedelta(days=1)
        return f"Samedi {saturday.strftime('%d/%m')} et Dimanche {sunday.strftime('%d/%m')}"

    def _get_prompt_template(self):
        template = """
        Tu es l'assistant expert en événements culturels pour Puls-Events.
        Nous sommes le : {current_date}.
        Pour info, le prochain week-end est : {weekend_dates}.
        
        CONSIGNES STRICTES :
        1. **ANALYSE L'INTENTION** :
           - Si l'utilisateur dit simplement "Bonjour", "Salut" (Salutations pures) :
             Réponds poliment, présente-toi comme l'assistant Puls-Events, et demande ce qu'il cherche.
             **NE PROPOSE AUCUN ÉVÉNEMENT.**
           - Sinon, passe à l'étape 2.

        2. **RECOMMANDATION (Uniquement si demandé)** :
           - Tu dois RECOMMANDER uniquement des événements dont la date est FUTURE ou AUJOURD'HUI.
           - REGARDE la section "Détail des dates" dans le contexte.
             - Si une date est sous "ARCHIVES", C'EST INTERDIT.
             - Si une date est sous "DATES À VENIR", c'est autorisé.
           - Si l'utilisateur demande "ce week-end", cherche EXACTEMENT les dates {weekend_dates} dans la liste.
           - **INTERDICTION TOTALE D'INVENTER DES DATES.** Si la date demandée n'est pas écrite NOIR SUR BLANC dans "Détail des dates", dis que tu n'as rien trouvé.

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
                "weekend_dates": self._get_weekend_dates,
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

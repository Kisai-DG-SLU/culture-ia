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

# Configuration locale pour le français
try:
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, "fr_FR")
    except locale.Error:
        pass


class RAGChain:
    def __init__(self):
        self.vectorstore_manager = VectorStoreManager()
        self.vectorstore = self.vectorstore_manager.load_index()
        if self.vectorstore is None:
            raise ValueError("Vector store not found. Please run vectorstore.py first.")

        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        self.llm = self._init_llm()
        self.prompt = self._get_prompt_template()
        self.chain = self._build_chain()

    def _init_llm(self):
        mistral_key = os.getenv("MISTRAL_API_KEY")
        return ChatMistralAI(api_key=mistral_key, model="mistral-tiny", temperature=0)

    def _get_date_range_from_query(self, query: str):
        now = datetime.now()
        query_lower = query.strip().lower()

        # Salutations
        greetings = ["bonjour", "salut", "coucou", "hello", "bonsoir", "merci"]
        if query_lower in greetings or len(query_lower.split()) <= 1:
            return {"type": "greeting", "display": "Salutation"}

        # Demain
        if "demain" in query_lower:
            tomorrow = now + timedelta(days=1)
            return {
                "type": "day",
                "start_ts": tomorrow.replace(hour=0, minute=0, second=0).timestamp(),
                "end_ts": tomorrow.replace(hour=23, minute=59, second=59).timestamp(),
                "display": tomorrow.strftime("%A %d %B %Y"),
            }

        # Ce week-end (Samedi et Dimanche de la semaine ISO courante)
        if (
            "ce week-end" in query_lower
            or "ce weekend" in query_lower
            or "ce we" in query_lower
        ):
            # On cherche le samedi (5) de la semaine actuelle
            days_to_saturday = 5 - now.weekday()
            saturday = (now + timedelta(days=days_to_saturday)).replace(
                hour=0, minute=0, second=0
            )
            sunday = (saturday + timedelta(days=1)).replace(
                hour=23, minute=59, second=59
            )

            return {
                "type": "weekend",
                "start_ts": saturday.timestamp(),
                "end_ts": sunday.timestamp(),
                "display": f"le week-end du {saturday.strftime('%d/%m')} au {sunday.strftime('%d/%m')}",
            }

        # Défaut
        return {
            "type": "any_future",
            "start_ts": now.timestamp(),
            "end_ts": float("inf"),
            "display": "",
        }

    def _filter_retrieved_docs(self, docs: list, date_context: dict):
        if date_context.get("type") == "greeting":
            return []

        start_ts = date_context.get("start_ts", 0)
        end_ts = date_context.get("end_ts", float("inf"))

        filtered = []
        for doc in docs:
            sessions = doc.metadata.get("all_sessions_ts", [])
            if sessions:
                if any(start_ts <= ts <= end_ts for ts in sessions):
                    filtered.append(doc)
            else:
                # Fallback plage globale
                e_start = doc.metadata.get("start_ts", 0)
                e_end = doc.metadata.get("end_ts", float("inf"))
                if e_start <= end_ts and e_end >= start_ts:
                    filtered.append(doc)
        return filtered

    def _get_prompt_template(self):
        template = """
        Tu es l'assistant de l'agenda Puls-Events.
        Nous sommes aujourd'hui le : {current_date}.

        REGLES CRITIQUES :
        1. Si le CONTEXTE contient "AUCUN ÉVÉNEMENT TROUVÉ", réponds : "Désolé, il n'y a aucune animation disponible pour [la période demandée]. N'hésitez pas à me solliciter pour une autre date !"
        2. NE JAMAIS INVENTER DE DATE. Si l'utilisateur demande "ce week-end", et qu'il n'y a rien, dis qu'il n'y a rien.
        3. Si la question est une salutation simple, réponds : "Bonjour ! Je suis l'assistant Puls-Events. Comment puis-je vous aider dans votre recherche de sorties ?"
        4. Si la question porte sur une ville absente du contexte (ex: Lyon), réponds : "Je n'ai accès qu'aux événements de l'agenda Puls-Events (principalement Paris/Vincennes). Je ne peux pas vous renseigner sur d'autres localités."

        CONTEXTE :
        {context}

        QUESTION : {question}

        RÉPONSE :
        """
        return ChatPromptTemplate.from_template(template)

    def _get_current_date(self, _):
        return datetime.now().strftime("%A %d %B %Y")

    def _format_docs(self, docs: list, date_context: dict):
        if not docs:
            period = date_context.get("display", "")
            return f"AUCUN ÉVÉNEMENT TROUVÉ POUR {period.upper() if period else 'CETTE RECHERCHE'}."

        unique_contents = {
            doc.metadata.get("url")
            or doc.page_content: doc.metadata.get("full_context", doc.page_content)
            for doc in docs
        }
        return "\n\n---\n\n".join(unique_contents.values())

    def _build_chain(self):
        chain = (
            {
                "question": RunnablePassthrough(),
                "current_date": self._get_current_date,
            }
            | RunnablePassthrough.assign(
                date_context=lambda x: self._get_date_range_from_query(x["question"])
            )
            | RunnablePassthrough.assign(
                retrieved_docs=lambda x: self._filter_retrieved_docs(
                    self.retriever.invoke(x["question"]), x["date_context"]
                )
            )
            | {
                "context": lambda x: self._format_docs(
                    x["retrieved_docs"], x["date_context"]
                ),
                "question": lambda x: x["question"],
                "current_date": lambda x: x["current_date"],
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
    print(rag.ask("Bonjour"))
    print(rag.ask("C'est quoi les sorties ce week-end ?"))

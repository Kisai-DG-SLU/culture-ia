import os
import locale
import calendar
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
        """Extrait une intention de date précise de la requête utilisateur."""
        now = datetime.now()
        query_lower = query.strip().lower()

        # Valeur par défaut : Tout le futur
        result = {
            "type": "any_future",
            "start_ts": now.timestamp(),
            "end_ts": float("inf"),
            "display": "",
        }

        # 1. Salutations simples (Chit-chat)
        greetings = ["bonjour", "salut", "coucou", "hello", "bonsoir", "merci"]
        if query_lower in greetings or len(query_lower.split()) <= 1:
            return {"type": "greeting", "display": "Salutation"}

        # 2. Demain
        if "demain" in query_lower:
            tomorrow = now + timedelta(days=1)
            result = {
                "type": "day",
                "start_ts": tomorrow.replace(hour=0, minute=0, second=0).timestamp(),
                "end_ts": tomorrow.replace(hour=23, minute=59, second=59).timestamp(),
                "display": tomorrow.strftime("%A %d %B %Y"),
            }

        # 3. Ce week-end (Samedi et Dimanche de la semaine ISO courante)
        elif (
            "ce week-end" in query_lower
            or "ce weekend" in query_lower
            or "ce we" in query_lower
        ):
            days_to_saturday = 5 - now.weekday()
            sat = (now + timedelta(days=days_to_saturday)).replace(
                hour=0, minute=0, second=0
            )
            sun = (sat + timedelta(days=1)).replace(hour=23, minute=59, second=59)
            result = {
                "type": "weekend",
                "start_ts": sat.timestamp(),
                "end_ts": sun.timestamp(),
                "display": f"le week-end du {sat.strftime('%d/%m')} au {sun.strftime('%d/%m')}",
            }

        # 4. Le mois prochain
        elif "mois prochain" in query_lower:
            m, y = (now.month + 1, now.year) if now.month < 12 else (1, now.year + 1)
            first = datetime(y, m, 1)
            _, last_num = calendar.monthrange(y, m)
            result = {
                "type": "month",
                "start_ts": first.timestamp(),
                "end_ts": datetime(y, m, last_num, 23, 59, 59).timestamp(),
                "display": first.strftime("%B %Y"),
            }

        # 5. Été (Juin à Septembre)
        elif "été" in query_lower:
            y = now.year if now.month <= 9 else now.year + 1
            s = datetime(y, 6, 21, 0, 0, 0)
            e = datetime(y, 9, 21, 23, 59, 59)
            result = {
                "type": "season",
                "start_ts": s.timestamp(),
                "end_ts": e.timestamp(),
                "display": f"l'été {y}",
            }

        # 6. Noms de mois spécifiques (ex: "en janvier")
        else:
            months = [
                "janvier",
                "février",
                "mars",
                "avril",
                "mai",
                "juin",
                "juillet",
                "août",
                "septembre",
                "octobre",
                "novembre",
                "décembre",
            ]
            for i, m in enumerate(months):
                if m in query_lower:
                    m_num = i + 1
                    y = now.year if m_num >= now.month else now.year + 1
                    first = datetime(y, m_num, 1)
                    _, last_num = calendar.monthrange(y, m_num)
                    result = {
                        "type": "specific_month",
                        "start_ts": first.timestamp(),
                        "end_ts": datetime(y, m_num, last_num, 23, 59, 59).timestamp(),
                        "display": first.strftime("%B %Y"),
                    }
                    break
        return result

    def _filter_retrieved_docs(self, docs: list, date_context: dict):
        """Filtre les documents retournés par FAISS pour ne garder que les sessions pertinentes."""
        if date_context.get("type") == "greeting":
            return []

        start_ts = date_context.get("start_ts", 0)
        end_ts = date_context.get("end_ts", float("inf"))

        filtered = []
        for doc in docs:
            sessions = doc.metadata.get("all_sessions_ts", [])
            if sessions:
                # On valide si au moins une session tombe dans la plage demandée
                if any(start_ts <= ts <= end_ts for ts in sessions):
                    filtered.append(doc)
            else:
                # Fallback plage globale (compatibilité)
                e_start = doc.metadata.get("start_ts", 0)
                e_end = doc.metadata.get("end_ts", float("inf"))
                if e_start <= end_ts and e_end >= start_ts:
                    filtered.append(doc)
        return filtered

    def _get_prompt_template(self):
        template = """
        Tu es l'assistant expert de l'agenda Puls-Events.
        Nous sommes aujourd'hui le : {current_date}.

        REGLES CRITIQUES :
        1. Si le CONTEXTE contient "AUCUN ÉVÉNEMENT TROUVÉ", réponds : "Désolé, il n'y a aucune animation disponible pour [la période demandée]. N'hésitez pas à me solliciter pour une autre date !"
        2. NE CITE QUE les dates de sessions qui figurent explicitement dans le CONTEXTE et qui correspondent à la demande.
        3. Si l'utilisateur demande une période précise (ex: un mois), ne liste QUE les dates de ce mois.
        4. Si la question est une salutation simple (Bonjour, Merci...), réponds poliment sans citer d'événements.
        5. Pour toute question hors-sujet (Lyon, Cinéma si non présent...), indique que tu ne gères que l'agenda Puls-Events.

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

        unique_contents = {}
        for doc in docs:
            url = doc.metadata.get("url")
            content = doc.metadata.get("full_context", doc.page_content)
            if url:
                unique_contents[url] = content
            else:
                unique_contents[content] = content

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
                    self.retriever.invoke(x["question"]),
                    x["date_context"],
                )
            )
            | {
                "context": lambda x: self._format_docs(
                    x["retrieved_docs"],
                    x["date_context"],
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
    print(rag.ask("le mois prochain ?"))

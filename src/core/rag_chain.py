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

# Essayer de mettre la locale en français pour la date
try:
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
except locale.Error:
    pass


class RAGChain:
    def __init__(self):
        self.vectorstore_manager = VectorStoreManager()
        self.vectorstore = self.vectorstore_manager.load_index()
        if self.vectorstore is None:
            raise ValueError("Vector store not found. Please run vectorstore.py first.")

        # K=3 pour avoir un peu plus de contexte pour filtrer géographiquement si besoin
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        self.llm = self._init_llm()
        self.prompt = self._get_prompt_template()
        self.chain = self._build_chain()

    def _init_llm(self):
        mistral_key = os.getenv("MISTRAL_API_KEY")
        return ChatMistralAI(api_key=mistral_key, model="mistral-tiny", temperature=0)

    def _get_date_range_from_query(self, query: str):
        """Extrait une intention de date (demain, ce week-end) de la requête."""
        now = datetime.now()
        query_lower = query.strip().lower()

        # Détection de salutation simple (sans demande d'info)
        greetings = ["bonjour", "salut", "coucou", "hello", "bonsoir", "merci"]
        # Si la requête est juste un mot de salutation ou très courte
        if query_lower in greetings or len(query_lower.split()) <= 1:
            return {
                "type": "greeting",
                "start_ts": None,
                "end_ts": None,
                "display": "Salutation",
            }

        # Pour 'demain'
        if "demain" in query_lower:
            tomorrow = now + timedelta(days=1)
            return {
                "type": "day",
                "start_ts": tomorrow.replace(
                    hour=0, minute=0, second=0, microsecond=0
                ).timestamp(),
                "end_ts": tomorrow.replace(
                    hour=23, minute=59, second=59, microsecond=999999
                ).timestamp(),
                "display": tomorrow.strftime("%A %d %B %Y"),
            }

        # Pour 'ce week-end'
        if "ce week-end" in query_lower or "ce weekend" in query_lower:
            # En Python : Lundi=0 ... Dimanche=6
            weekday = now.weekday()

            # Calcul du Samedi de la semaine courante
            # Si on est Dimanche (6), le Samedi était hier (-1 jour)
            # Si on est Samedi (5), c'est aujourd'hui
            # Si on est Vendredi (4), c'est demain (+1)
            days_until_saturday = 5 - weekday

            # Cas particulier du Dimanche soir : "Ce week-end" réfère souvent au WE qui se termine
            # Mais si on est Lundi, "Ce week-end" réfère au suivant.
            # Logique simple : On prend le Samedi et Dimanche de la semaine ISO courante.

            saturday = (now + timedelta(days=days_until_saturday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            sunday = (saturday + timedelta(days=1)).replace(
                hour=23, minute=59, second=59, microsecond=999999
            )

            return {
                "type": "weekend",
                "start_ts": saturday.timestamp(),
                "end_ts": sunday.timestamp(),
                "display": f"Samedi {saturday.strftime('%d/%m')} et Dimanche {sunday.strftime('%d/%m')}",
            }

        # Défaut : Futur
        return {
            "type": "any_future",
            "start_ts": now.timestamp(),
            "end_ts": float("inf"),
            "display": "",
        }

    def _filter_retrieved_docs(self, docs: list, date_context: dict):
        """Filtre les documents par date."""
        if date_context.get("type") == "greeting":
            return []

        start_ts = date_context.get("start_ts", 0)
        end_ts = date_context.get("end_ts", float("inf"))

        filtered_docs = []
        for doc in docs:
            # Sécurité : vérifier que les métadonnées existent
            event_start_ts = doc.metadata.get("start_ts", 0)
            event_end_ts = doc.metadata.get("end_ts", float("inf"))

            # Chevauchement des périodes :
            # (Debut_Event <= Fin_Requete) ET (Fin_Event >= Debut_Requete)
            if event_start_ts <= end_ts and event_end_ts >= start_ts:
                filtered_docs.append(doc)
        return filtered_docs

    def _get_prompt_template(self):
        template = """
        Tu es l'assistant officiel de l'agenda **Puls-Events**.
        Date système : {current_date}.
        
        TES RESPONSABILITÉS :
        1. **FILTRE HORS-SUJET / HORS-SCOPE** :
           - Tu ne connais QUE les événements fournis dans le CONTEXTE ci-dessous.
           - Si l'utilisateur demande des événements dans une **Ville** (ex: Lyon, Bordeaux) qui n'est pas mentionnée dans le CONTEXTE : Réponds que tu ne gères pas l'agenda de cette ville.
           - Si l'utilisateur demande un **Thème** (ex: Cinéma, Foot) qui n'est pas dans le CONTEXTE : Réponds que cet agenda ne couvre pas ce type d'activité.
           - Si la question est générale (Chit-chat, salutations) : Réponds poliment et propose ton aide pour trouver une sortie culturelle.

        2. **RÉPONSE FACTUELLE SUR LES ÉVÉNEMENTS** :
           - Utilise **uniquement** les informations du CONTEXTE.
           - Si le CONTEXTE est vide après filtrage (indiqué par "Aucun événement trouvé...") : Dis simplement que tu n'as pas d'événements pour cette recherche spécifique (date/lieu/thème). **N'INVENTE RIEN.**
           - Si tu as des événements : Présente-les avec leur Titre, Lieu, et Date précise.

        CONTEXTE (Événements filtrés) :
        {context}

        QUESTION UTILISATEUR : {question}

        TA RÉPONSE :
        """
        return ChatPromptTemplate.from_template(template)

    def _get_current_date(self, _):
        return datetime.now().strftime("%A %d %B %Y")

    def _format_docs(self, docs: list[dict], date_context: dict):
        unique_docs = {}
        for doc in docs:
            url = doc.metadata.get("url")
            content = doc.metadata.get("full_context", doc.page_content)
            if url:
                unique_docs[url] = content
            else:
                unique_docs[content] = content

        if not unique_docs:
            period = date_context.get("display", "")
            if period:
                return f"Aucun événement trouvé pour la période : {period}."
            return "Aucun événement correspondant aux critères trouvés dans la base."

        return "\n\n".join(unique_docs.values())

    def _build_chain(self):
        # 1. Analyse date
        date_context_extractor = RunnablePassthrough.assign(
            date_context=lambda x: self._get_date_range_from_query(x["question"])
        )

        # 2. Retrieval + Filtrage Python
        filtered_retriever_step = RunnablePassthrough.assign(
            retrieved_docs=lambda x: self._filter_retrieved_docs(
                self.retriever.invoke(x["question"]),
                x["date_context"],
            )
        )

        chain = (
            {
                "question": RunnablePassthrough(),
                "current_date": self._get_current_date,
            }
            | date_context_extractor
            | filtered_retriever_step
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
    # Test rapide
    chain = RAGChain()
    print("Test WE:", chain.ask("C'est quoi les sorties ce week-end ?"))

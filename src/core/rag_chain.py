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

    def _get_date_range_from_query(self, query: str):
        """Extrait une intention de date (demain, ce week-end) de la requête et retourne une plage de timestamps."""
        now = datetime.now()
        query_lower = query.lower()

        # Pour 'demain'
        if "demain" in query_lower:
            tomorrow = now + timedelta(days=1)
            # La plage couvre toute la journée de demain
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

        # Pour 'ce week-end' ou 'ce weekend'
        if "ce week-end" in query_lower or "ce weekend" in query_lower:
            # Calcul du prochain samedi et dimanche à partir d'aujourd'hui
            # Si on est Samedi, le WE commence aujourd'hui
            # Si on est Dimanche, le WE commence hier (Samedi)
            # Sinon, on prend le Samedi et Dimanche de la semaine prochaine
            days_until_saturday = (5 - now.weekday() + 7) % 7  # 5 = Samedi

            if now.weekday() == 5:  # C'est Samedi
                saturday = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif now.weekday() == 6:  # C'est Dimanche
                saturday = (now - timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            else:  # Jour de semaine, on cherche le prochain Samedi
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

        # Pour les requêtes générales ou sans intention de date spécifique, on donne une plage large (futur)
        # La date de fin de l'événement doit être >= à maintenant (pour ne pas proposer du passé)
        return {
            "type": "any_future",
            "start_ts": now.timestamp(),
            "end_ts": float("inf"),
            "display": "",
        }

    def _filter_retrieved_docs(self, docs: list, date_context: dict):
        """Filtre les documents récupérés en fonction du contexte de date fourni par _get_date_range_from_query."""
        start_ts = date_context.get(
            "start_ts", 0
        )  # Si pas de start_ts, on prend tout (ou 0 pour l'historique)
        end_ts = date_context.get(
            "end_ts", float("inf")
        )  # Si pas d'end_ts, on prend tout le futur

        filtered_docs = []
        for doc in docs:
            event_start_ts = doc.metadata.get("start_ts", 0)
            event_end_ts = doc.metadata.get("end_ts", float("inf"))

            # Un événement est pertinent si sa période chevauche la période demandée
            # Et que l'événement n'est pas entièrement dans le passé par rapport à la start_ts demandée
            if event_end_ts >= start_ts and event_start_ts <= end_ts:
                filtered_docs.append(doc)
        return filtered_docs

    def _get_prompt_template(self):
        template = """
        Tu es l'assistant expert en événements culturels pour Puls-Events.
        Nous sommes le : {current_date}.
        
        CONSIGNES STRICTES :
        1. **ANALYSE L'INTENTION ET RÉPONSE INITIALE** :
           - Si la QUESTION est une simple salutation ("Bonjour", "Salut", "Coucou") **SANS AUTRE DEMANDE** :
             Réponds poliment en tant qu'assistant Puls-Events et demande quel type de sortie l'utilisateur recherche.
             **NE MENTIONNE AUCUN ÉVÉNEMENT NI AUCUNE DATE NON SOLLICITÉE.**
           - Si la QUESTION CONTIENT une demande spécifique, passe à l'étape 2.

        2. **RECOMMANDATION D'ÉVÉNEMENTS (Contexte pré-filtré)** :
           - Le CONTEXTE ci-dessous ne contient QUE les événements qui correspondent à la demande de l'utilisateur (par exemple, pour "demain" ou "ce week-end").
           - Si le CONTEXTE est vide, cela signifie qu'aucun événement pertinent n'a été trouvé pour la demande spécifique. Dans ce cas, réponds : "Désolé, je n'ai pas trouvé d'événement pour [période de la demande si connue, sinon 'votre demande']."
           - **INTERDICTION TOTALE D'INVENTER DES ÉVÉNEMENTS OU DES DATES.** Base-toi STRICTEMENT et UNIQUEMENT sur le CONTEXTE fourni.
           - Si le CONTEXTE contient des événements, résume-les clairement, donne les dates EXACTES (issues du contexte) et les URLs.

        CONTEXTE DES ÉVÉNEMENTS (pré-filtré par Python) :
        {context}

        QUESTION : {question}

        RÉPONSE FACTUELLE :
        """
        return ChatPromptTemplate.from_template(template)

    def _get_current_date(self, _):
        """Retourne la date actuelle formatée."""
        return datetime.now().strftime("%A %d %B %Y")

    def _format_docs(self, docs: list[dict], date_context: dict):
        # Déduplication basée sur l'URL pour ne pas répéter le même événement complet
        unique_docs = {}
        for doc in docs:
            url = doc.metadata.get("url")
            if url and url not in unique_docs:
                unique_docs[url] = doc.metadata.get("full_context", doc.page_content)
            elif not url:
                # Fallback si pas d'URL (ne devrait pas arriver avec nos données)
                unique_docs[str(hash(doc.page_content))] = doc.page_content

        if not unique_docs:
            # Si aucun document pertinent n'a été filtré, indique-le pour le LLM
            period_display = date_context.get("display")
            if period_display:
                return f"Aucun événement trouvé pour {period_display}."
            return "Aucun événement pertinent trouvé."

        return "\n\n".join(unique_docs.values())

    def _build_chain(self):
        # 1. Extraction du contexte de date de la question (en Python)
        date_context_extractor = RunnablePassthrough.assign(
            date_context=lambda x: self._get_date_range_from_query(x["question"])
        )

        # 2. Récupération des documents AVANT filtrage (k documents par le retriever)
        # 3. Filtrage des documents par Python en fonction du contexte de date
        filtered_retriever_step = RunnablePassthrough.assign(
            retrieved_docs=lambda x: self._filter_retrieved_docs(
                self.retriever.invoke(x["question"]), x["date_context"]
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
    rag = RAGChain()
    response = rag.ask("Quels sont les événements sur la cuisine sauvage ?")
    print("Question: Quels sont les événements sur la cuisine sauvage ?")
    print(f"Réponse: {response}")

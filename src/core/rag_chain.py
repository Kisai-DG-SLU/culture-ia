import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from src.core.vectorstore import VectorStoreManager

load_dotenv()

class RAGChain:
    def __init__(self):
        self.vectorstore_manager = VectorStoreManager()
        self.vectorstore = self.vectorstore_manager.load_index()
        if self.vectorstore is None:
            raise ValueError("Vector store not found. Please run vectorstore.py first.")
        
        self.llm = self._init_llm()
        self.prompt = self._get_prompt_template()
        self.chain = self._build_chain()

    def _init_llm(self):
        mistral_key = os.getenv("MISTRAL_API_KEY")
        return ChatMistralAI(api_key=mistral_key, model="mistral-tiny")

    def _get_prompt_template(self):
        template = """
        Tu es un assistant expert en événements culturels pour Puls-Events.
        Utilise les éléments de contexte suivants pour répondre à la question de l'utilisateur.
        Si tu ne connais pas la réponse, dis simplement que tu ne sais pas, n'invente pas de réponse.
        Réponds de manière concise et amicale.

        Contexte:
        {context}

        Question: {question}

        Réponse:
        """
        return ChatPromptTemplate.from_template(template)

    def _format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def _build_chain(self):
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        
        chain = (
            {"context": retriever | self._format_docs, "question": RunnablePassthrough()}
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
    print(f"Question: Quels sont les événements sur la cuisine sauvage ?")
    print(f"Réponse: {response}")

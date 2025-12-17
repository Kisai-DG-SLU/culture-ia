from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.core.rag_chain import RAGChain
from src.collector import OpenAgendaCollector
from src.processor import EventProcessor
from src.core.vectorstore import VectorStoreManager

app = FastAPI(title="Culture IA API", description="Assistant de recommandation d'événements culturels")

# Initialize RAG Chain
try:
    rag_chain = RAGChain()
except Exception as e:
    print(f"Warning: RAGChain could not be initialized: {e}")
    rag_chain = None

class Query(BaseModel):
    question: str

class Response(BaseModel):
    answer: str

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Culture IA !"}

@app.post("/ask", response_model=Response)
def ask_question(query: Query):
    if not query.question or not query.question.strip():
        raise HTTPException(status_code=400, detail="La question ne peut pas être vide.")

    if rag_chain is None:
        raise HTTPException(status_code=503, detail="RAG Chain not initialized. Please rebuild index.")
    
    try:
        answer = rag_chain.ask(query.question)
        return Response(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rebuild")
def rebuild_index():
    try:
        # 1. Collect
        collector = OpenAgendaCollector()
        events = collector.fetch_events()
        recent_events = collector.filter_recent_events(events)
        collector.save_to_json(recent_events)
        
        # 2. Process
        processor = EventProcessor()
        processor.process()
        
        # 3. Vectorize
        vector_manager = VectorStoreManager()
        vector_manager.create_index()
        
        # 4. Reload RAG Chain
        global rag_chain
        rag_chain = RAGChain()
        
        return {"message": "Index vectoriel reconstruit avec succès !"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

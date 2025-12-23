import os
import json
from dotenv import load_dotenv
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from src.core.rag_chain import RAGChain

load_dotenv()


class RAGEvaluator:
    def __init__(self):
        self.rag_chain = RAGChain()
        self.mistral_key = os.getenv("MISTRAL_API_KEY")
        self.llm = ChatMistralAI(api_key=self.mistral_key, model="mistral-large-latest")
        self.embeddings = MistralAIEmbeddings(api_key=self.mistral_key)

        # Définition du chemin racine du projet
        # src/core/evaluator.py -> ../.. = project root
        self.project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../..")
        )

    def prepare_dataset(self, test_file="tests/evaluation_dataset.json"):
        # Construction du chemin absolu
        abs_test_file = os.path.join(self.project_root, test_file)

        if not os.path.exists(abs_test_file):
            # Fallback : essayer un chemin relatif si le chemin absolu échoue (cas de tests locaux)
            abs_test_file = test_file

        with open(abs_test_file, "r", encoding="utf-8") as f:
            test_data = json.load(f)

        questions = []
        answers = []
        contexts = []
        ground_truths = []

        for item in test_data:
            question = item["question"]

            # For simplicity, I'll manually retrieve context here for evaluation dataset
            retriever = self.rag_chain.vectorstore.as_retriever(search_kwargs={"k": 3})
            docs = retriever.invoke(question)
            context = [doc.page_content for doc in docs]

            answer = self.rag_chain.ask(question)

            questions.append(question)
            answers.append(answer)
            contexts.append(context)
            ground_truths.append(item["ground_truth"])

        data = {
            "user_input": questions,
            "response": answers,
            "retrieved_contexts": contexts,
            "reference": ground_truths,
        }
        return Dataset.from_dict(data)

    def run_evaluation(self, test_file="tests/evaluation_dataset.json"):
        print("Preparing evaluation dataset...")
        dataset = self.prepare_dataset(test_file)

        print("Running Ragas evaluation...")
        result = evaluate(
            dataset=dataset,
            metrics=[
                faithfulness,
                answer_relevancy,
                context_recall,
                context_precision,
            ],
            llm=self.llm,
            embeddings=self.embeddings,
        )

        print("\nEvaluation results:")
        print(result)

        # Save results
        output_file = os.path.join(self.project_root, "data/evaluation_results.json")

        # Force conversion to dictionary to avoid list-related errors in frontend
        # Ragas Result object usually acts as a dict for average scores
        try:
            # We explicitly extract the metrics we care about to ensure valid JSON structure
            scores = {
                "faithfulness": result.get("faithfulness", 0.0),
                "answer_relevancy": result.get("answer_relevancy", 0.0),
                "context_recall": result.get("context_recall", 0.0),
                "context_precision": result.get("context_precision", 0.0),
            }
        except Exception as e:
            print(
                f"Warning: Error extracting scores: {e}. Saving raw result cast to dict."
            )
            # Fallback: try to cast the whole object to dict if specific keys fail
            try:
                scores = dict(result)
            except Exception:
                # Debugging: save type and dir of result to understand what it is
                scores = {
                    "error": "Could not serialize Ragas result",
                    "type": str(type(result)),
                    "dir": str(dir(result)),
                    "str_representation": str(result),
                }

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(scores, f, ensure_ascii=False, indent=4)
        print(f"Results saved to {output_file}")
        return result


if __name__ == "__main__":
    evaluator = RAGEvaluator()
    evaluator.run_evaluation()

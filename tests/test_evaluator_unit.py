from unittest.mock import MagicMock, patch
import pytest
from src.core.evaluator import RAGEvaluator


@pytest.fixture
def mock_evaluator():
    with patch("src.core.evaluator.RAGChain"), patch(
        "src.core.evaluator.ChatMistralAI"
    ), patch("src.core.evaluator.MistralAIEmbeddings"):
        evaluator = RAGEvaluator()
        return evaluator


def test_evaluator_init(mock_evaluator):
    """Vérifie l'initialisation de l'évaluateur."""
    assert mock_evaluator.rag_chain is not None
    assert mock_evaluator.llm is not None


@patch("src.core.evaluator.json")
@patch("src.core.evaluator.evaluate")
@patch("src.core.evaluator.RAGEvaluator.prepare_dataset")
def test_run_evaluation_logic(mock_prep, mock_evaluate, mock_json, mock_evaluator):
    """Vérifie la logique de sauvegarde des résultats de l'évaluation."""
    # Mock des données retournées par Ragas
    mock_result = MagicMock()
    # On simule l'absence de l'attribut .scores pour tester le fallback de ma correction
    del mock_result.scores
    mock_result.keys.return_value = ["faithfulness", "answer_relevancy"]
    mock_result.__getitem__.side_effect = lambda k: 0.9 if k == "faithfulness" else 0.8

    mock_evaluate.return_value = mock_result
    mock_prep.return_value = MagicMock()

    # Mock de l'écriture de fichier
    with patch("builtins.open", MagicMock()):
        mock_evaluator.run_evaluation("dummy_file.json")

    # Vérification que json.dump a été appelé avec un dictionnaire
    assert mock_json.dump.called
    args, _ = mock_json.dump.call_args
    scores = args[0]
    assert isinstance(scores, dict)
    assert "faithfulness" in scores


@patch("builtins.open")
@patch("src.core.evaluator.json")
@patch("src.core.evaluator.Dataset")
def test_prepare_dataset(mock_dataset, mock_json, mock_open, mock_evaluator):
    """Vérifie la préparation du dataset pour l'évaluation."""
    # Setup des mocks
    mock_json.load.return_value = [
        {"question": "Q1", "ground_truth": "A1"},
        {"question": "Q2", "ground_truth": "A2"},
    ]

    # Mock du retriever
    mock_retriever = MagicMock()
    mock_doc = MagicMock()
    mock_doc.page_content = "Context content"
    mock_retriever.invoke.return_value = [mock_doc]
    mock_evaluator.rag_chain.vectorstore.as_retriever.return_value = mock_retriever

    # Mock de rag_chain.ask
    mock_evaluator.rag_chain.ask.return_value = "Generated Answer"

    # Exécution
    mock_evaluator.prepare_dataset("dummy_path.json")

    # Vérifications
    assert mock_open.called
    assert mock_json.load.called
    assert mock_evaluator.rag_chain.ask.call_count == 2

    # Vérifier que Dataset.from_dict a reçu les bonnes données
    assert mock_dataset.from_dict.called
    args, _ = mock_dataset.from_dict.call_args
    data = args[0]
    assert len(data["user_input"]) == 2
    assert len(data["response"]) == 2
    assert len(data["retrieved_contexts"]) == 2
    assert len(data["reference"]) == 2
    assert data["retrieved_contexts"][0] == ["Context content"]

    @patch("src.core.evaluator.evaluate")
    @patch("src.core.evaluator.RAGEvaluator.prepare_dataset")
    def test_run_evaluation_exception(mock_prep, mock_evaluate, mock_evaluator):
        """Vérifie que l'évaluation gère gracieusement les erreurs de format de résultat."""
        # Simulation d'un résultat qui provoque une erreur lors de l'extraction
        mock_result = MagicMock()
        # On fait en sorte que .get() lève une exception
        mock_result.get.side_effect = Exception("Format inattendu")

        # Le fallback "dict(result)" doit aussi échouer pour tomber dans le cas d'erreur final
        # MagicMock.__iter__ existe par défaut, on le fait planter
        mock_result.__iter__.side_effect = TypeError("Not iterable")

        mock_evaluate.return_value = mock_result
        mock_prep.return_value = MagicMock()

        with patch("builtins.open", MagicMock()) as mock_file_open:
            mock_evaluator.run_evaluation("dummy.json")

            # Vérifie qu'on a essayé d'écrire quelque chose (probablement le message d'erreur)
            mock_file_open.assert_called()
        # On vérifie que le fichier a quand même été ouvert pour écrire quelque chose
        assert mock_file_open.called

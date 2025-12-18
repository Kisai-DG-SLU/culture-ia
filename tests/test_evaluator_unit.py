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

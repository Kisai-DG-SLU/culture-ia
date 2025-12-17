from unittest import mock
from src.main import main


def test_main(capsys):
    # We just test the print since uvicorn.run would block
    with mock.patch("uvicorn.run"):
        main()
        captured = capsys.readouterr()
        assert "Lancement de l'API Culture IA..." in captured.out

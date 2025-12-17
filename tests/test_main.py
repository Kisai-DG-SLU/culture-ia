def test_main(capsys):
    # We just test the print since uvicorn.run would block
    from src.main import main
    import unittest.mock as mock
    
    with mock.patch("uvicorn.run"):
        main()
        captured = capsys.readouterr()
        assert "Lancement de l'API Culture IA..." in captured.out

import os
import sys
import uvicorn


def main():
    print("Lancement de l'API Culture IA...")
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    # Ensure PYTHONPATH includes current directory for imports
    sys.path.append(os.getcwd())
    main()

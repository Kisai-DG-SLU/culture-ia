import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

# Configuration de la page
st.set_page_config(page_title="Puls-Events Assistant", page_icon="🎭", layout="wide")

# API Configuration
API_URL = "http://localhost:8000"

# Header
st.title("🎭 Culture IA - Assistant Puls-Events")
st.markdown("---")

# Onglets
tab1, tab2, tab3 = st.tabs(["🤖 Assistant", "⚙️ Administration", "📊 Performances RAG"])

# --- TAB 1: ASSISTANT ---
with tab1:
    st.header("Discutez avec l'assistant")

    # Historique de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input utilisateur
    if prompt := st.chat_input("Posez votre question sur les événements culturels..."):
        # Afficher message user
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Appel API
        with st.chat_message("assistant"):
            try:
                with st.spinner("Recherche en cours..."):
                    response = requests.post(
                        f"{API_URL}/ask", json={"question": prompt}
                    )
                    if response.status_code == 200:
                        answer = response.json()["answer"]
                        st.markdown(answer)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": answer}
                        )
                    else:
                        error_msg = (
                            f"Erreur API: {response.status_code} - {response.text}"
                        )
                        st.error(error_msg)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": error_msg}
                        )
            except requests.exceptions.ConnectionError:
                st.error(
                    "❌ Impossible de contacter l'API. Vérifiez qu'elle est bien lancée."
                )

# --- TAB 2: ADMINISTRATION ---
with tab2:
    st.header("État du Système")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Statut API")
        try:
            res = requests.get(f"{API_URL}/")
            if res.status_code == 200:
                st.success("✅ API en ligne")
            else:
                st.warning(f"⚠️ API répond avec code {res.status_code}")
        except:
            st.error("❌ API Hors-ligne")

    with col2:
        st.subheader("Actions")
        if st.button("🔄 Reconstruire l'Index Vectoriel", type="primary"):
            with st.status("Reconstruction en cours...", expanded=True) as status:
                st.write("📡 Collecte des données OpenAgenda...")
                time.sleep(1)  # Fake UX delay
                st.write("🧠 Vectorisation des événements...")

                try:
                    res = requests.post(f"{API_URL}/rebuild")
                    if res.status_code == 200:
                        status.update(
                            label="Index reconstruit avec succès !",
                            state="complete",
                            expanded=False,
                        )
                        st.balloons()
                    else:
                        status.update(
                            label="Erreur lors de la reconstruction", state="error"
                        )
                        st.error(res.text)
                except Exception as e:
                    status.update(label="Erreur de connexion", state="error")
                    st.error(str(e))

# --- TAB 3: PERFORMANCES ---
with tab3:
    st.header("Métriques d'Évaluation (Ragas)")

    # Bouton pour lancer l'évaluation
    if st.button(
        "🚀 Lancer une nouvelle évaluation complète",
        help="Exécute le moteur Ragas sur le jeu de test. Cela peut prendre 1 à 2 minutes.",
    ):
        with st.status("Évaluation en cours...", expanded=True) as status:
            st.write("📡 Envoi des questions au LLM Mistral...")
            st.write("📊 Calcul des scores Fidélité, Pertinence et Rappel...")

            try:
                import subprocess

                # Exécution directe du script python
                process = subprocess.Popen(
                    ["python", "src/core/evaluator.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                stdout, stderr = process.communicate()

                if process.returncode == 0:
                    status.update(
                        label="Évaluation terminée avec succès !",
                        state="complete",
                        expanded=False,
                    )
                    st.toast("Scores mis à jour !")
                    time.sleep(1)
                    st.rerun()
                else:
                    status.update(label="Erreur lors de l'évaluation", state="error")
                    st.error(f"Erreur: {stderr}\nOutput: {stdout}")
            except Exception as e:
                status.update(label="Erreur système", state="error")
                st.error(str(e))

    try:
        res = requests.get(f"{API_URL}/metrics")
        if res.status_code == 200:
            metrics = res.json()

            # KPI Cards
            c1, c2, c3, c4 = st.columns(4)
            c1.metric(
                "Fidélité (Faithfulness)", f"{metrics.get('faithfulness', 0):.2%}"
            )
            c2.metric(
                "Pertinence (Relevancy)", f"{metrics.get('answer_relevancy', 0):.2%}"
            )
            c3.metric("Rappel (Recall)", f"{metrics.get('context_recall', 0):.2%}")
            c4.metric(
                "Précision (Precision)", f"{metrics.get('context_precision', 0):.2%}"
            )

            st.markdown("---")

            # Radar Chart
            st.subheader("Visualisation Radar")

            df = pd.DataFrame(
                dict(
                    r=[
                        metrics.get("faithfulness", 0),
                        metrics.get("answer_relevancy", 0),
                        metrics.get("context_recall", 0),
                        metrics.get("context_precision", 0),
                    ],
                    theta=["Fidélité", "Pertinence", "Rappel", "Précision"],
                )
            )

            fig = px.line_polar(
                df, r="r", theta="theta", line_close=True, range_r=[0, 1]
            )
            fig.update_traces(fill="toself")
            st.plotly_chart(fig, width="stretch")

            st.caption(
                "*Note : Une précision de 50% avec une base de 2 documents est structurellement normale (voir Rapport Technique).*"
            )

        else:
            st.warning("Impossible de récupérer les métriques.")
    except Exception as e:
        st.error(f"Erreur d'affichage des métriques : {e}")

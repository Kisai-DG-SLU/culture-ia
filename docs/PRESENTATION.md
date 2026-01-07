---
marp: true
theme: gaia
paginate: true
backgroundImage: url('images/background.png')
color: #333
style: |
  section {
    justify-content: center;
    padding: 70px;
  }
  section::before {
    content: ' ';
    position: absolute;
    top: 20px;
    left: 20px;
    width: 80px;
    height: 80px;
    background-image: url('images/logo_projet.png');
    background-size: contain;
    background-repeat: no-repeat;
  }
  footer {
    position: absolute;
    bottom: 20px;
    right: 20px;
    font-size: 0.8em;
  }
  /* Pousse le contenu vers le bas pour un meilleur centrage visuel */
  section:not(.lead) h1 {
    margin-top: 1.5em; 
  }
  section.lead h1 {
    font-size: 2.0em;
    color: #2c3e50;
    margin-top: 0;
  }
  section.lead h2 {
    font-size: 1.5em;
    color: #e74c3c;
  }
  .catchphrase {
    color: #e74c3c;
    font-size: 1.4em;
    font-weight: bold;
    margin-top: 20px;
    display: inline-block;
    transform: rotate(-2deg);
    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
  }
  .split-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 40px;
    width: 100%;
  }
  .split-text {
    flex: 1;
  }
  .split-image {
    flex: 1;
    display: flex;
    justify-content: flex-end;
  }
  .split-image img {
    max-height: 300px;
    max-width: 100%;
    object-fit: contain;
  }
  .center-container {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    margin-top: 20px;
  }
  .center-container img {
    max-height: 450px;
    max-width: 100%;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  }
---

<!-- _class: lead -->

# Assistant Culture IA
## Projet 7 - Puls-Events

**Damien Guesdon**
Janvier 2026

![bg right:30% fit](images/logo_projet.png)

---

# 1. Le Problème
<p class="catchphrase">Une base de données riche, mais une expérience utilisateur pauvre.</p>

![bg right:40% fit](images/problem_visual.png)

---

# 2. La Solution
<p class="catchphrase">Le RAG : Connecter l'intelligence du LLM à nos données réelles.</p>

![bg right:40% fit](images/architecture_rag.png)

---

# 3. La Stack Technique
<p class="catchphrase">Souveraineté, Performance et Simplicité.</p>

![bg right:40% fit](images/stack_tech.png)

---

# 4. Le Pipeline de Données (ETL)
<p class="catchphrase">"Garbage In, Garbage Out" : La qualité avant tout.</p>

![bg right:40% fit](images/pipeline_etl.png)

---

# 5. Défi Technique :<br>Le Temps
<p class="catchphrase">Un événement passé n'a aucune valeur.</p>

![bg right:40% fit](images/calendar_visual.png)

---

<!-- _class: lead -->

# DÉMONSTRATION

<div class="center-container">
  <img src="images/demo_screenshot.png" />
</div>

---

# 7. Évaluation (Ragas)

<div class="split-container">
  <div class="split-text">
    <p class="catchphrase">On ne devine pas la qualité, on la mesure.</p>
  </div>
  <div class="split-image">
    <img src="images/ragas_radar.png" />
  </div>
</div>

---

# 8. Industrialisation
<p class="catchphrase">Docker : "Build once, run anywhere".</p>

![bg right:40% fit](images/docker_visual.png)

---

# 9. Limites & Perspectives
<p class="catchphrase">Roadmap vers la V2.</p>

![bg right:40% fit](images/roadmap_visual.png)

---

<!-- _class: lead -->

# CONCLUSION
POC Validé. Prêt pour la production.

**Merci de votre écoute.**
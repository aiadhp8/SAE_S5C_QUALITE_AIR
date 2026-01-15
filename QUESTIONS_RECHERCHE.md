# Questions de recherche - SAE S5.C.01
## Analyse de la qualité de l'air : Questions pour guider l'analyse

---

## 1) Questions "cadre" (définir ce que vous mesurez)

### Q1. Quels polluants (PM2.5, NO₂, O₃, SO₂, CO) sont les plus pertinents pour comparer des villes à l'échelle mondiale ?

### Q2. Est-ce qu'on mesure la "qualité de l'air" via moyenne, médiane, ou pics (ex : 95e percentile) ? Qu'est-ce que ça change ?

### Q3. À partir de quel seuil de couverture (ex : ≥12 mois de données) une ville devient "analysable" sans trop de biais ?

---

## 2) Questions descriptives (avant toute corrélation)

### Q4. Quelles villes/pays ont les niveaux les plus élevés de PM2.5 / NO₂ sur la période étudiée ?

### Q5. Observe-t-on une saisonnalité (hiver/été) des polluants selon les régions ?

### Q6. Les distributions de PM2.5 et NO₂ sont-elles "skewed" (très asymétriques) ? Faut-il passer en log ou utiliser Spearman ?

---

## 3) Questions "urbaines" (World Cities)

### Q7. La taille de la ville (population) est-elle liée aux niveaux de NO₂ (trafic) et PM2.5 ?

### Q8. Les capitales ont-elles un profil de pollution différent des villes non-capitales à population comparable ?

### Q9. L'altitude (si vous l'intégrez) est-elle associée à des niveaux plus faibles (dispersion) ou plus élevés (vallées/piégeage) ?

### Q10. Les villes "très grandes" sont-elles plus variables (écart-type/pics) que les villes moyennes ?

---

## 4) Questions "sociales/éco" (World Bank)

### Q11. La motorisation (ou proxies transport) est-elle associée au NO₂ (plus que PM2.5) ?

### Q12. Une part plus forte d'industrie est-elle associée à PM2.5 ou SO₂ ?

### Q13. Le PIB/habitant est-il corrélé à une meilleure qualité de l'air (hypothèse type "courbe environnementale") ou l'inverse ?

### Q14. Le taux d'urbanisation est-il associé à une hausse de PM2.5 (densification) ou à une baisse (meilleures infrastructures) ?

### Q15. Les émissions de CO₂/hab sont-elles un bon proxy de pollution locale (PM2.5/NO₂) ou est-ce décorrélé ?

---

## 5) Questions multivariées (ACP / réduction de dimension)

### Q16. Quels sont les 2–3 axes principaux qui expliquent la variance entre villes (ex : "transport/urbanisation" vs "industrie/énergie") ?

### Q17. Les villes se regroupent-elles naturellement par niveau de revenu, continent, ou plutôt par profil d'émissions ?

### Q18. Est-ce que l'ACP change fortement si on retire/ajoute 1 indicateur (robustesse des axes) ?

---

## 6) Questions "graphes de similarité" (profils de villes)

### Q19. Quelles villes sont les plus "similaires" en profil pollution + socio-éco, même si elles sont géographiquement éloignées ?

### Q20. Les communautés détectées dans le graphe (k-NN) correspondent-elles à des catégories compréhensibles (industrie lourde, mégapoles, etc.) ?

### Q21. Une ville "atypique" (outlier) apparaît-elle comme isolée dans le graphe ? Peut-on expliquer pourquoi (données, géographie, économie) ?

---

## 7) Questions prédictives (modèles simples, orienté process)

### Q22. Peut-on prédire le PM2.5 moyen d'une ville à partir de variables urbaines + WB (même grossièrement) ?

### Q23. Quelles variables sont les plus déterminantes selon les modèles (régression vs arbres) ? Les conclusions sont-elles stables ?

### Q24. Le modèle généralise-t-il à des villes/pays "non vus" ou est-ce surtout du surapprentissage lié à la couverture des données ?

---

## 8) Questions "qualité / biais / limites" (super important pour votre projet)

### Q25. Les résultats changent-ils si on change le seuil de complétude (≥12 mois vs ≥24 mois) ?

### Q26. Est-ce que les villes avec stations OpenAQ sont représentatives, ou biaisées vers certains pays/régions ?

### Q27. Problème clé : WB est au niveau pays, pollution au niveau ville → dans quelle mesure ça limite l'interprétation (risque d'agrégation) ?

---

## 📊 RÉPARTITION DES QUESTIONS PAR ÉQUIPE

### Équipe A : Analyses descriptives
**Questions : Q4, Q5, Q6, Q7, Q8, Q9, Q10**
- Statistiques descriptives
- Distributions
- Visualisations géographiques
- Effet taille des villes

---

### Équipe B : Corrélations et relations
**Questions : Q11, Q12, Q13, Q14, Q15**
- Corrélations polluants vs indicateurs socio-économiques
- Relation PIB vs pollution
- Impact urbanisation
- Motorisation vs NO₂

---

### Équipe C : ACP et réduction de dimension
**Questions : Q16, Q17, Q18**
- Analyse en Composantes Principales
- Interprétation des axes
- Robustesse du modèle
- Regroupements naturels

---

### Équipe D : Graphes de similarité (optionnel)
**Questions : Q19, Q20, Q21**
- Graphes k-NN
- Détection de communautés
- Identification outliers

---

### Équipe E : Modèles prédictifs
**Questions : Q22, Q23, Q24**
- Modèles de régression
- Random Forest
- Feature importance
- Généralisation

---

### Toute l'équipe : Qualité et limites
**Questions : Q1, Q2, Q3, Q25, Q26, Q27**
- Définir les métriques
- Évaluer les biais
- Documenter les limitations
- Analyser la robustesse

---

## 🎯 UTILISATION DE CES QUESTIONS

### Phase d'exploration (J1-J3)
Utilisez **Q1, Q2, Q3** pour :
- Décider quels polluants prioriser
- Choisir les métriques (moyenne, médiane, percentiles)
- Définir le seuil de couverture minimal

### Phase d'analyse descriptive (J11-J12)
Équipe A répond à **Q4-Q10**

### Phase d'analyse corrélations (J12-J13)
Équipe B répond à **Q11-Q15**

### Phase ACP (J13)
Équipe C répond à **Q16-Q18**

### Phase modélisation (J13-J14)
Équipe E répond à **Q22-Q24**

### Rédaction du rapport (J14-J15)
**TOUTE l'équipe** doit adresser **Q25, Q26, Q27** dans la section "Discussion et limites"

---

## 💡 CONSEILS POUR RÉPONDRE AUX QUESTIONS

### ✅ Bonnes pratiques

1. **Pour chaque question** :
   - Formuler une hypothèse claire
   - Analyser les données
   - Créer une visualisation
   - Interpréter les résultats
   - Documenter les limitations

2. **Documenter systématiquement** :
   - Le code utilisé
   - Les résultats numériques
   - Les graphiques générés
   - Les conclusions tirées

3. **Être critique** :
   - Les résultats sont-ils statistiquement significatifs ?
   - Y a-t-il des biais dans les données ?
   - Les conclusions sont-elles généralisables ?

### ⚠️ Pièges à éviter

❌ Ne pas confondre corrélation et causalité  
❌ Ne pas ignorer les valeurs manquantes  
❌ Ne pas sur-interpréter des résultats non significatifs  
❌ Ne pas oublier la limitation "données pays vs ville" (Q27)  

---

## 📝 TEMPLATE DE RÉPONSE

Pour chaque question, structurez votre réponse ainsi :

```markdown
### Q[numéro]. [Question]

**Hypothèse :**
[Votre hypothèse avant l'analyse]

**Méthode :**
[Comment vous avez analysé : code, statistiques, visualisations]

**Résultats :**
- [Résultat 1]
- [Résultat 2]
- [Graphique/tableau si pertinent]

**Interprétation :**
[Ce que signifient les résultats]

**Limitations :**
[Biais, limites, précautions dans l'interprétation]
```

---

## 🔗 LIENS AVEC LES LIVRABLES

### Rapport scientifique (10 pages max)
Les réponses aux questions **Q4-Q24** constituent le cœur de votre rapport.

Structure suggérée :
1. **Introduction** : Q1, Q2, Q3 (définir ce qu'on mesure)
2. **Résultats descriptifs** : Q4-Q10
3. **Analyses multivariées** : Q11-Q18
4. **Modélisation** : Q22-Q24
5. **Discussion** : Q25-Q27 (limites et biais)

### Présentation orale (30 min)
Sélectionnez les **5-6 questions les plus intéressantes** avec les résultats les plus marquants.

### Base de données
Votre schéma doit permettre de répondre facilement à toutes ces questions via des requêtes SQL.

---

## 🎓 QUESTIONS PRIORITAIRES

Si vous manquez de temps, priorisez ces questions :

### ⭐ Priorité HAUTE (OBLIGATOIRES)
- Q1, Q2, Q3 (définir le cadre)
- Q4 (villes les plus polluées)
- Q7 (population vs pollution)
- Q13 (PIB vs pollution)
- Q22 (modèle prédictif)
- Q25, Q26, Q27 (limites)

### ⭐⭐ Priorité MOYENNE (FORTEMENT RECOMMANDÉES)
- Q5 (saisonnalité)
- Q11 (motorisation vs NO₂)
- Q16 (axes principaux ACP)
- Q23 (variables importantes)

### ⭐⭐⭐ Priorité BASSE (Si temps disponible)
- Q6, Q8, Q9, Q10 (analyses détaillées)
- Q17, Q18 (robustesse ACP)
- Q19, Q20, Q21 (graphes)
- Q24 (généralisation)

---

**Ces questions sont votre feuille de route pour l'analyse. Gardez-les toujours à portée de main ! 📍**

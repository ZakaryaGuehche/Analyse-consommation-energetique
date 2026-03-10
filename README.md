\# Analyse de la Consommation Energetique



\## Description

Analyse exploratoire de donnees de consommation energetique d'un parc de 8 batiments sur 2 ans. Identification des patterns de consommation, des pics energetiques et recommandations d'optimisation pour reduire les couts.



\## Objectifs

\- Explorer les patterns de consommation horaire, journaliere et mensuelle

\- Identifier les pics de consommation et leurs causes

\- Analyser l'impact de la temperature sur la consommation

\- Comparer les profils de consommation par type de batiment

\- Formuler des recommandations d'optimisation



\## Dataset

\- 8 batiments (Bureaux, Residentiels, Commerciaux, Industriel)

\- 2 ans de donnees horaires (2023-2024)

\- 140 000+ enregistrements

\- Variables : consommation kWh, temperature, cout, type de tarif



\## Technologies

\- Python

\- Pandas (manipulation de donnees temporelles)

\- Matplotlib (visualisations)

\- Seaborn (visualisations statistiques)

\- SciPy (tests statistiques)



\## Insights cles

\- Pic de consommation entre 9h-12h et 18h-21h

\- Correlation significative temperature-consommation

\- Les bureaux consomment 40% de plus que les residences

\- Potentiel d'economie de 15-20% identifie



\## Visualisations



\### Profil de Consommation Horaire

!\[Consommation](outputs/consommation\_journaliere.png)



\### Heatmap Jour x Heure

!\[Heatmap](outputs/heatmap\_horaire.png)



\### Saisonnalite et Temperature

!\[Saisonnalite](outputs/saisonnalite.png)



\### Pics de Consommation

!\[Pics](outputs/pics\_consommation.png)



\## Installation

```bash

pip install -r requirements.txt

python generate\_data.py

python analysis.py


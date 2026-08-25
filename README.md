# 🌦️ Climat de Madagascar — Dashboard interactif

Dashboard interactif présentant l'évolution des températures et précipitations
dans les 23 régions de Madagascar entre 2005 et 2024, construit à partir des
données satellite [NASA POWER](https://power.larc.nasa.gov/).

## Démo en ligne

👉 [Lien à ajouter après déploiement sur Streamlit Cloud]

## Fonctionnalités

- 🗺️ Carte choroplèthe interactive (température / précipitation)
- 📈 Évolution mensuelle avec tendance linéaire, filtrable par région et période
- 📊 Classement comparatif des 23 régions
- 🌦️ Comparaison saison sèche vs saison pluvieuse
- 🧾 Table de données filtrable + export CSV

## Stack technique

- Python, Pandas, NumPy
- Streamlit (interface)
- Plotly (visualisations interactives)
- Données géographiques : [geoBoundaries](https://www.geoboundaries.org/) (ADM1, Madagascar)

## Lancer en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Structure

```
├── app.py                  # Application Streamlit principale
├── requirements.txt
└── data/
    ├── madagascar_climate_processed.csv
    └── madagascar_regions_simplified.geojson
```

## Note sur les régions

Madagascar compte officiellement 23 régions depuis 2021 (scission de
Vatovavy-Fitovinany). Les données climatiques distinguent bien les 23 régions
partout dans le dashboard, à l'exception de la carte, où Vatovavy et
Fitovinany sont fusionnées (moyenne des deux) car les contours géographiques
publics standards n'ont pas encore été mis à jour pour refléter cette
scission.

## Source des données

NASA POWER Project, paramètres `T2M` (température à 2m) et `PRECTOTCORR`
(précipitation corrigée), résolution mensuelle, 2005–2024.

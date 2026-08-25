# Madagascar Climate Dashboard

Interactive dashboard presenting temperature and precipitation trends across
Madagascar's 23 regions between 2005 and 2024, built from
[NASA POWER](https://power.larc.nasa.gov/) satellite data.

## Live demo

[Link to add after deployment on Streamlit Cloud]

## Features

- Interactive choropleth map (temperature / precipitation)
- Monthly evolution with linear trend, filterable by region and period
- Comparative ranking of all 23 regions
- Dry season vs rainy season comparison
- Filterable data table with CSV export

## Tech stack

- Python, Pandas, NumPy
- Streamlit (interface)
- Plotly (interactive visualizations)
- Geographic data: [geoBoundaries](https://www.geoboundaries.org/) (ADM1, Madagascar)

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```
├── app.py                  # Main Streamlit application
├── requirements.txt
└── data/
    ├── madagascar_climate_processed.csv
    └── madagascar_regions.geojson
```

## Note on regions

Madagascar has officially had 23 regions since 2021 (Vatovavy-Fitovinany was
split in two). The climate data distinguishes all 23 regions throughout the
dashboard, except on the map, where Vatovavy and Fitovinany are merged
(average of the two) because standard public geographic boundaries have not
yet been updated to reflect this split.

## Data source

NASA POWER Project, parameters `T2M` (temperature at 2m) and `PRECTOTCORR`
(corrected precipitation), monthly resolution, 2005–2024.


# Global Seismic Trends: Data-Driven Earthquake Insights

Complete Python + Pandas + Regex + MySQL + Streamlit project.

## Folder structure

global_seismic_trends_project/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── src/
│   ├── 01_fetch_usgs.py
│   ├── 02_clean_data.py
│   ├── 03_mysql_setup.py
│   └── 04_load_mysql.py
├── sql/
│   ├── 01_create_database.sql
│   └── 02_analysis_queries.sql
├── notebooks/
│   └── colab_full_project.py
├── docs/
│   ├── PROJECT_FLOW.md
│   ├── FEATURES.md
│   └── README_EVALUATION.md
└── data/
    ├── raw/
    └── processed/

## Database
Database name: earthquakedb
Table name: earthquakes

## Run order
1. python src/01_fetch_usgs.py
2. python src/02_clean_data.py
3. Configure .env
4. python src/03_mysql_setup.py
5. python src/04_load_mysql.py
6. streamlit run app.py

The project specification requires USGS API retrieval, preprocessing, MySQL storage, SQL analytics and Streamlit. fileciteturn0file0L30-L46

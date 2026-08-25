import os
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

st.set_page_config(
    page_title="Global Seismic Trends",
    page_icon="🌍",
    layout="wide"
)

@st.cache_resource
def get_engine():
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD", "")
    host = os.getenv("MYSQL_HOST", "127.0.0.1").strip()
    port = os.getenv("MYSQL_PORT", "3306")
    database = os.getenv("MYSQL_DATABASE", "earthquakedb")

    if user:
        try:
            engine = create_engine(
                f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}",
                future=True
            )
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except Exception:
            pass

    csv_path = os.path.join(os.path.dirname(__file__), "data", "processed", "earthquakes_clean.csv")
    sqlite_path = os.path.join(os.path.dirname(__file__), "data", "processed", "earthquakes_local.db")

    if os.path.exists(sqlite_path):
        engine = create_engine(f"sqlite:///{sqlite_path}", future=True)
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1 FROM earthquakes LIMIT 1"))
            return engine
        except Exception:
            pass

    df = pd.read_csv(csv_path)
    engine = create_engine(f"sqlite:///{sqlite_path}", future=True)
    df.to_sql("earthquakes", engine, index=False, if_exists="replace")
    return engine

@st.cache_data(ttl=300)
def run_query(sql):
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn)

st.title("🌍 Global Seismic Trends")
st.subheader("Data-Driven Earthquake Insights")
st.caption("USGS API • Python • Pandas • Regex • MySQL • Streamlit")

try:
    total = run_query(
        "SELECT COUNT(*) AS value FROM earthquakes"
    ).iloc[0, 0]

    avg_mag = run_query(
        "SELECT AVG(mag) AS value FROM earthquakes"
    ).iloc[0, 0]

    max_mag = run_query(
        "SELECT MAX(mag) AS value FROM earthquakes"
    ).iloc[0, 0]

    tsunami = run_query(
        "SELECT COALESCE(SUM(tsunami), 0) AS value FROM earthquakes"
    ).iloc[0, 0]

except Exception as error:
    st.error("MySQL connection failed. Check your .env file.")
    st.exception(error)
    st.stop()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Earthquakes", f"{int(total):,}")
c2.metric("Average Magnitude", f"{avg_mag:.2f}")
c3.metric("Maximum Magnitude", f"{max_mag:.2f}")
c4.metric("Tsunami Events", f"{int(tsunami):,}")

st.divider()

year_df = run_query("""
    SELECT year, COUNT(*) AS count
    FROM earthquakes
    GROUP BY year
    ORDER BY year
""")

st.plotly_chart(
    px.line(
        year_df,
        x="year",
        y="count",
        markers=True,
        title="Earthquakes per Year"
    ),
    use_container_width=True
)

col1, col2 = st.columns(2)

with col1:
    mag_type = run_query("""
        SELECT magType, COUNT(*) AS count
        FROM earthquakes
        WHERE magType IS NOT NULL
        GROUP BY magType
        ORDER BY count DESC
        LIMIT 10
    """)

    st.plotly_chart(
        px.bar(
            mag_type,
            x="magType",
            y="count",
            title="Magnitude Type Distribution"
        ),
        use_container_width=True
    )

with col2:
    depth = run_query("""
        SELECT depth_category, COUNT(*) AS count
        FROM earthquakes
        WHERE depth_category IS NOT NULL
        GROUP BY depth_category
    """)

    st.plotly_chart(
        px.bar(
            depth,
            x="depth_category",
            y="count",
            title="Earthquake Depth Category"
        ),
        use_container_width=True
    )

st.subheader("Top 10 Strongest Earthquakes")

top10 = run_query("""
    SELECT time, mag, depth_km, place, country_region
    FROM earthquakes
    ORDER BY mag DESC
    LIMIT 10
""")

st.dataframe(top10, use_container_width=True)

st.subheader("Earthquake Map")

map_df = run_query("""
    SELECT latitude, longitude, mag, depth_km, place
    FROM earthquakes
    WHERE latitude IS NOT NULL
      AND longitude IS NOT NULL
    ORDER BY mag DESC
    LIMIT 5000
""")

if not map_df.empty:
    st.map(
        map_df.rename(
            columns={"latitude": "lat", "longitude": "lon"}
        )
    )

st.subheader("Most Active Reporting Networks")

net_df = run_query("""
    SELECT net, COUNT(*) AS count
    FROM earthquakes
    WHERE net IS NOT NULL
    GROUP BY net
    ORDER BY count DESC
    LIMIT 15
""")

st.bar_chart(net_df.set_index("net"))

st.subheader("Project Data Note")

st.info(
    "The supplied project specification requests casualties, economic loss, "
    "continent and alert-level analysis. Those are not among the specified "
    "26 USGS source features, so this project keeps them NULL rather than "
    "inventing values. They can be populated later using an enrichment dataset."
)

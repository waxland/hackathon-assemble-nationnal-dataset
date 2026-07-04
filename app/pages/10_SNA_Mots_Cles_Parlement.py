import json
import os
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_sidebar import render_sidebar


DB_PATH = "data/france2030.sqlite"
THEMES_PATH = "data/themes.json"
KEYWORDS_PATH = "data/keywords.json"
STRATEGIES_PATH = "data/acceleration_strategies.json"


@st.cache_data
def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


@st.cache_data
def load_parliament_mentions():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()

    query = """
        select
            mentionId,
            date,
            chamber,
            speakerName,
            politicalGroup,
            matchedKeyword,
            relatedThemeId,
            relatedProgrammeCode,
            interventionText,
            contextBefore,
            contextAfter,
            sourceUrl,
            confidenceScore,
            validationStatus
        from parliament_mentions
        where matchedKeyword is not null
        order by date
    """

    with sqlite3.connect(DB_PATH) as connection:
        return pd.read_sql_query(query, connection)


def clean_theme_name(value):
    if not isinstance(value, str):
        return "Theme inconnu"
    return value.split(". ", 1)[1] if ". " in value[:4] else value


st.set_page_config(
    page_title="SNA - Mots cles parlementaires",
    page_icon="app/content/favicon.ico",
    layout="wide",
)
render_sidebar("SNA Mots Cles Parlement")

col_img, col_text = st.columns([1, 10])
with col_img:
    st.image("app/content/favicon.svg", width=80)
with col_text:
    st.title("Strategies nationales d'acceleration - mots cles parlementaires")

st.markdown("---")

themes = pd.DataFrame(load_json(THEMES_PATH))
keywords = pd.DataFrame(load_json(KEYWORDS_PATH))
strategies = pd.DataFrame(load_json(STRATEGIES_PATH))
mentions = load_parliament_mentions()

if mentions.empty:
    st.warning("Aucune mention parlementaire disponible dans `data/france2030.sqlite`.")
    st.stop()

theme_lookup = {}
if not themes.empty and {"themeId", "themeName"}.issubset(themes.columns):
    themes = themes[["themeId", "themeName"]].copy()
    themes["actionName"] = themes["themeName"].map(clean_theme_name)
    theme_lookup = themes.set_index("themeId")["actionName"].to_dict()

mentions["date"] = pd.to_datetime(mentions["date"], errors="coerce")
mentions = mentions.dropna(subset=["date", "matchedKeyword", "relatedThemeId"]).copy()
mentions["month"] = mentions["date"].dt.to_period("M").dt.to_timestamp()
mentions["actionName"] = mentions["relatedThemeId"].map(theme_lookup).fillna(
    mentions["relatedThemeId"]
)
mentions["politicalGroup"] = mentions["politicalGroup"].fillna("Inconnu")
mentions["matchedKeyword"] = mentions["matchedKeyword"].astype(str)

if not keywords.empty and {"label", "relatedThemeId", "type"}.issubset(keywords.columns):
    keyword_types = keywords.copy()
    keyword_types["labelNorm"] = keyword_types["label"].astype(str).str.lower().str.strip()
    keyword_types = keyword_types[["labelNorm", "relatedThemeId", "type"]].drop_duplicates()
    mentions["labelNorm"] = mentions["matchedKeyword"].str.lower().str.strip()
    mentions = mentions.merge(
        keyword_types,
        how="left",
        on=["labelNorm", "relatedThemeId"],
    )
    mentions["type"] = mentions["type"].fillna("detected")
else:
    mentions["type"] = "detected"

available_actions = sorted(mentions["actionName"].dropna().unique())
available_groups = sorted(mentions["politicalGroup"].dropna().unique())

col_filters_1, col_filters_2, col_filters_3 = st.columns([2, 2, 1])
with col_filters_1:
    selected_actions = st.multiselect(
        "Actions SNA",
        available_actions,
        default=available_actions,
    )
with col_filters_2:
    selected_groups = st.multiselect(
        "Groupes politiques",
        available_groups,
        default=available_groups,
    )
with col_filters_3:
    min_confidence = st.slider(
        "Confiance min.",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.05,
    )

filtered = mentions[
    mentions["actionName"].isin(selected_actions)
    & mentions["politicalGroup"].isin(selected_groups)
    & (mentions["confidenceScore"].fillna(0) >= min_confidence)
].copy()

if filtered.empty:
    st.warning("Aucune mention ne correspond aux filtres.")
    st.stop()

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("Mentions parlementaires", len(filtered))
metric_2.metric("Actions SNA couvertes", filtered["actionName"].nunique())
metric_3.metric("Mots cles detectes", filtered["matchedKeyword"].nunique())
metric_4.metric("Groupes politiques", filtered["politicalGroup"].nunique())

scatter_data = (
    filtered.groupby(
        ["month", "actionName", "matchedKeyword", "politicalGroup", "relatedThemeId"],
        dropna=False,
    )
    .agg(
        mentions=("mentionId", "count"),
        confidenceScore=("confidenceScore", "mean"),
        firstSourceUrl=("sourceUrl", "first"),
    )
    .reset_index()
)

st.subheader("Nuage de points mensuel")

scatter_fig = px.scatter(
    scatter_data,
    x="month",
    y="actionName",
    size="mentions",
    color="actionName",
    symbol="politicalGroup",
    hover_name="matchedKeyword",
    hover_data={
        "month": "|%Y-%m",
        "actionName": True,
        "politicalGroup": True,
        "mentions": True,
        "confidenceScore": ":.2f",
        "firstSourceUrl": True,
        "relatedThemeId": False,
    },
    labels={
        "month": "Mois",
        "actionName": "Action SNA",
        "matchedKeyword": "Mot cle",
        "politicalGroup": "Groupe politique",
        "mentions": "Occurrences",
    },
)
scatter_fig.update_traces(marker={"sizemin": 8, "opacity": 0.82})
scatter_fig.update_layout(
    height=max(520, 95 * scatter_data["actionName"].nunique()),
    legend_title_text="Action SNA",
    margin={"l": 20, "r": 20, "t": 40, "b": 20},
)
st.plotly_chart(scatter_fig, use_container_width=True)

st.subheader("Timeline des usages parlementaires")

timeline_data = (
    filtered.groupby(["month", "actionName"], dropna=False)
    .size()
    .reset_index(name="mentions")
)

timeline_fig = px.bar(
    timeline_data,
    x="month",
    y="mentions",
    color="actionName",
    labels={
        "month": "Mois",
        "mentions": "Mentions",
        "actionName": "Action SNA",
    },
)
timeline_fig.update_layout(
    barmode="stack",
    height=420,
    legend_title_text="Action SNA",
    margin={"l": 20, "r": 20, "t": 40, "b": 20},
)
st.plotly_chart(timeline_fig, use_container_width=True)

col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("Mots cles les plus utilises")
    keyword_summary = (
        filtered.groupby(["actionName", "matchedKeyword"], dropna=False)
        .agg(
            mentions=("mentionId", "count"),
            firstMention=("date", "min"),
            lastMention=("date", "max"),
            averageConfidence=("confidenceScore", "mean"),
        )
        .reset_index()
        .sort_values(["mentions", "actionName", "matchedKeyword"], ascending=[False, True, True])
    )
    keyword_summary["firstMention"] = keyword_summary["firstMention"].dt.strftime("%Y-%m-%d")
    keyword_summary["lastMention"] = keyword_summary["lastMention"].dt.strftime("%Y-%m-%d")
    keyword_summary["averageConfidence"] = keyword_summary["averageConfidence"].round(2)
    st.dataframe(keyword_summary, use_container_width=True, hide_index=True)

with col_right:
    st.subheader("Referentiel SNA charge")
    if strategies.empty:
        st.info("Aucun fichier `data/acceleration_strategies.json` exploitable.")
    else:
        strategy_cols = [
            column
            for column in ["strategyId", "strategyName", "sourceScope", "sourceUrl"]
            if column in strategies.columns
        ]
        st.dataframe(strategies[strategy_cols], use_container_width=True, hide_index=True)

st.subheader("Mentions sourcees")
detail_columns = [
    "date",
    "actionName",
    "matchedKeyword",
    "speakerName",
    "politicalGroup",
    "relatedProgrammeCode",
    "confidenceScore",
    "validationStatus",
    "sourceUrl",
]
details = filtered[detail_columns].sort_values("date", ascending=False).copy()
details["date"] = details["date"].dt.strftime("%Y-%m-%d")
st.dataframe(details, use_container_width=True, hide_index=True)

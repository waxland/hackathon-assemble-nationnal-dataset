import os
import re

import pandas as pd
import streamlit as st
from streamlit_sidebar import render_sidebar


DOC_PATH = "DOCS_DATA_USAGE.md"


def read_doc(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def parse_markdown_tables(markdown):
    tables = []
    current = []

    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            current.append(stripped)
        elif current:
            tables.append(current)
            current = []

    if current:
        tables.append(current)

    parsed = []
    for table in tables:
        if len(table) < 3:
            continue

        header = [cell.strip() for cell in table[0].strip("|").split("|")]
        separator = table[1].strip("|").split("|")
        if not all(re.fullmatch(r"\s*:?-{3,}:?\s*", cell) for cell in separator):
            continue

        rows = []
        for row in table[2:]:
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            if len(cells) == len(header):
                rows.append(cells)

        if rows:
            parsed.append(pd.DataFrame(rows, columns=header))

    return parsed


def strip_markdown_links(value):
    return re.sub(r"`([^`]+)`", r"\1", value)


st.set_page_config(
    page_title="Documentation des sources et URLs",
    page_icon="app/content/favicon.ico",
    layout="wide",
)
render_sidebar("Docs Data Usage")

col_img, col_text = st.columns([1, 10])
with col_img:
    st.image("app/content/favicon.svg", width=80)
with col_text:
    st.title("Documentation des sources et URLs")

st.markdown("---")

content = read_doc(DOC_PATH)

if content is None:
    st.error(f"Le fichier `{DOC_PATH}` est introuvable.")
    st.stop()

st.caption(
    "Memo de tracabilite : URLs consultees, elements recuperes, ressources exactes et JSON cibles."
)

tables = parse_markdown_tables(content)

if tables:
    main_table = tables[0].copy()
    st.subheader("Synthese filtrable des sources")

    query = st.text_input(
        "Filtrer par source, URL, element recupere ou JSON cible",
        placeholder="Ex: ADEME, PLF 2026, Cour des comptes, i-Nov...",
    )

    if query:
        mask = main_table.apply(
            lambda row: row.astype(str).str.contains(query, case=False, regex=False).any(),
            axis=1,
        )
        main_table = main_table[mask]

    if hasattr(main_table, "map"):
        display_table = main_table.map(strip_markdown_links)
    else:
        display_table = main_table.apply(lambda column: column.map(strip_markdown_links))
    st.dataframe(display_table, use_container_width=True, hide_index=True)

    st.caption(f"{len(display_table)} source(s) affichee(s).")

st.subheader("Document complet")
with st.expander("Afficher le markdown source", expanded=True):
    st.markdown(content)

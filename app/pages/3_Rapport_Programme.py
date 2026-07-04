import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from app import load_front_dataset
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Couleurs DSFR
COLOR_BLEU_FRANCE = "#000091"
COLOR_ROUGE_MARIANNE = "#e1000f"

POSITIVE_TERMS = [
    "accélérer", "ambition", "ambitieux", "crucial", "essentiel", "favoriser",
    "prioritaire", "renforcer", "soutenir", "souveraineté", "nécessaire",
]
NEGATIVE_TERMS = [
    "alerte", "abandon", "coût", "dénonce", "insuffisant", "inquiétude",
    "oppose", "regrette", "risque", "supprimer", "retard",
]


def classify_tone(text):
    text_lower = (text or "").lower()
    positive_hits = sum(term in text_lower for term in POSITIVE_TERMS)
    negative_hits = sum(term in text_lower for term in NEGATIVE_TERMS)
    if positive_hits > negative_hits:
        return "favorable"
    if negative_hits > positive_hits:
        return "critique"
    return "neutre"


@st.cache_data
def load_local_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def programme_in_list(item, programme_code):
    codes = item.get("relatedProgrammeCodes") or []
    return str(programme_code) in [str(code) for code in codes]

col_img, col_text = st.columns([1, 10])
with col_img:
    st.image("app/content/icon-minerve.png", width=80)
with col_text:
    st.header("3. Rapport par Programme")

programs_data = load_front_dataset("catalog/investment-programmes.json")
budget_data = load_front_dataset("budget/france-2030-budget-lines.json")
parliament_data = load_front_dataset("sources/parliamentary-documents.json")
companies_data = load_front_dataset("sources/sirene-companies.json")
audit_findings = load_local_json("data/audit_findings.json")
acceleration_strategies = load_local_json("data/acceleration_strategies.json")

if programs_data:
    prog_options = {p.get("programmeCode"): f"Programme {p.get('programmeCode')} - {p.get('programmeName')}" for p in programs_data}
    selected_prog_code = st.selectbox("Sélectionnez un Programme :", options=list(prog_options.keys()), format_func=lambda x: prog_options[x])
    
    st.divider()
    st.subheader(f"Dossier Programme {selected_prog_code}")
    
    col_g, col_d = st.columns([1, 1])
    
    with col_g:
        st.markdown("### 💰 Budget & Subventions")
        prog_budget = [b for b in budget_data if str(b.get("programmeCode")) == selected_prog_code]
        if prog_budget:
            df_prog_bud = pd.DataFrame(prog_budget)
            amount_cols = [col for col in ["amount2024", "amount2025", "amount2026"] if col in df_prog_bud.columns]
            df_budget_long = df_prog_bud.melt(
                id_vars=["expenseCategoryName"],
                value_vars=amount_cols,
                var_name="year",
                value_name="amount",
            )
            df_budget_long["year"] = df_budget_long["year"].str.replace("amount", "", regex=False)
            df_budget_long["amount"] = pd.to_numeric(df_budget_long["amount"], errors="coerce")
            df_budget_long = df_budget_long.dropna(subset=["amount"])

            fig_bar = px.bar(
                df_budget_long,
                x="expenseCategoryName",
                y="amount",
                color="year",
                barmode="group",
                title="Répartition par type de dépense",
                color_discrete_sequence=[COLOR_BLEU_FRANCE, COLOR_ROUGE_MARIANNE, "#6a6af4"],
            )
            fig_bar.update_yaxes(title="Montant CP (€)", tickformat=",")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.write("Aucun budget identifié.")
            
        st.markdown("### 🚀 Écosystème & Entreprises")
        prog_comp = next((p for p in companies_data if str(p.get("programmeCode")) == selected_prog_code), {})
        companies = prog_comp.get("companies", [])
        if companies:
            st.dataframe(pd.DataFrame(companies), hide_index=True)
        else:
            st.write("Aucune entreprise identifiée.")

    with col_d:
        st.markdown("### 🏛️ Écho Parlementaire (Assemblée)")
        prog_mentions = next((p for p in parliament_data if str(p.get("programmeCode")) == selected_prog_code), {})
        docs = prog_mentions.get("documents", [])
        if docs:
            df_docs = pd.DataFrame(docs)
            fig_time = px.histogram(df_docs, x="date", color="politicalGroup", 
                                    title="Chronologie des interventions", nbins=10)
            st.plotly_chart(fig_time, use_container_width=True)

            df_docs["dateParsed"] = pd.to_datetime(df_docs["date"], errors="coerce")
            df_docs["year"] = df_docs["dateParsed"].dt.year.astype("Int64")
            mentions_by_year = (
                df_docs.dropna(subset=["year"])
                .groupby("year", as_index=False)
                .size()
                .rename(columns={"size": "mentions"})
            )

            if prog_budget:
                budget_by_year = []
                for year in ["2024", "2025", "2026"]:
                    col = f"amount{year}"
                    if col in df_prog_bud.columns:
                        amount = pd.to_numeric(df_prog_bud[col], errors="coerce").sum()
                        if pd.notna(amount) and amount > 0:
                            budget_by_year.append({"year": int(year), "budgetMds": amount / 1e9})
                df_budget_year = pd.DataFrame(budget_by_year)
                fig_overlay = go.Figure()
                if not df_budget_year.empty:
                    fig_overlay.add_trace(
                        go.Bar(
                            x=df_budget_year["year"],
                            y=df_budget_year["budgetMds"],
                            name="Budget CP (Mds €)",
                            marker_color=COLOR_BLEU_FRANCE,
                        )
                    )
                if not mentions_by_year.empty:
                    fig_overlay.add_trace(
                        go.Scatter(
                            x=mentions_by_year["year"],
                            y=mentions_by_year["mentions"],
                            name="Mentions",
                            yaxis="y2",
                            mode="lines+markers",
                            line=dict(color=COLOR_ROUGE_MARIANNE, width=3),
                        )
                    )
                fig_overlay.update_layout(
                    title="Budget et écho parlementaire par année",
                    yaxis=dict(title="Budget CP (Mds €)"),
                    yaxis2=dict(title="Mentions", overlaying="y", side="right", rangemode="tozero"),
                    legend=dict(orientation="h"),
                )
                st.plotly_chart(fig_overlay, use_container_width=True)

            tones = [classify_tone(text) for text in df_docs["text"].fillna("")]
            tone_counts = pd.Series(tones).value_counts().reindex(["favorable", "neutre", "critique"], fill_value=0)
            st.markdown("**Tonalité locale des verbatims :**")
            tone_cols = st.columns(3)
            tone_cols[0].metric("Favorable", int(tone_counts["favorable"]))
            tone_cols[1].metric("Neutre", int(tone_counts["neutre"]))
            tone_cols[2].metric("Critique", int(tone_counts["critique"]))
            
            # Wordcloud
            st.markdown("**Nuage de mots des débats :**")
            all_text = " ".join([doc.get("text", "") for doc in docs])
            if len(all_text) > 10:
                wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='Blues').generate(all_text)
                fig_wc, ax = plt.subplots(figsize=(8, 4))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig_wc)
            
            st.markdown("**Derniers verbatims extraits :**")
            page_size = 10
            total_pages = len(docs) // page_size + (1 if len(docs) % page_size > 0 else 0)
            page = st.number_input("Page de verbatims", min_value=1, max_value=max(1, total_pages), value=1)
            
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            for doc in docs[start_idx:end_idx]:
                with st.expander(f"🗣️ {doc.get('speakerName')} ({doc.get('politicalGroup')}) - {doc.get('date')}"):
                    st.markdown(f"**Mot-clé détecté :** `{doc.get('matchedKeyword')}`")
                    st.markdown(f"**Tonalité locale :** `{classify_tone(doc.get('text'))}`")
                    st.info(doc.get('text'))
        else:
            st.write("Aucun écho parlementaire trouvé.")

    st.divider()
    st.subheader("Alertes, audits et strategies nationales")

    audit_matches = [
        finding
        for finding in audit_findings
        if programme_in_list(finding, selected_prog_code)
    ]

    col_audit, col_sna = st.columns([3, 2])

    with col_audit:
        st.markdown("### Alertes & Audits")
        if audit_matches:
            for finding in audit_matches:
                risk_level = (finding.get("riskLevel") or "unknown").lower()
                message = (
                    f"**{finding.get('findingType', 'constat')} - risque {risk_level}**\n\n"
                    f"{finding.get('findingText', 'Constat non renseigne')}"
                )
                if risk_level == "high":
                    st.error(message)
                elif risk_level == "medium":
                    st.warning(message)
                else:
                    st.info(message)

                st.caption(
                    " | ".join(
                        [
                            f"Document: {finding.get('auditDocumentId', 'n/a')}",
                            f"Page: {finding.get('sourcePage', 'n/a')}",
                            f"Confiance: {finding.get('confidenceScore', 'n/a')}",
                        ]
                    )
                )
                if finding.get("evidenceSummary"):
                    st.write(finding.get("evidenceSummary"))
        else:
            st.success("Aucune alerte Cour des comptes explicitement rattachee a ce programme.")

    with col_sna:
        st.markdown("### Strategies Nationales d'Acceleration")
        linked_strategies = [
            strategy
            for strategy in acceleration_strategies
            if programme_in_list(strategy, selected_prog_code)
        ]

        if linked_strategies:
            st.dataframe(
                pd.DataFrame(linked_strategies),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info(
                "Aucune liaison explicite `strategy -> programme` n'est presente dans les donnees."
            )
            if acceleration_strategies:
                with st.expander("Voir le referentiel SNA disponible"):
                    cols = [
                        col
                        for col in ["strategyId", "strategyName", "sourceScope", "sourceUrl"]
                        if col in pd.DataFrame(acceleration_strategies).columns
                    ]
                    st.dataframe(
                        pd.DataFrame(acceleration_strategies)[cols],
                        use_container_width=True,
                        hide_index=True,
                    )
else:
    st.warning("Veuillez générer les fichiers JSON du contrat front d'abord.")

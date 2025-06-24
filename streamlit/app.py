#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author     Romaric Besançon <romaric.besancon@gmail.fr>
# date       Tue Jun 24 2025
#

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime


def plot_pie(column, name, max=30):
    if column in df.columns:
        freqs_all = df[column].value_counts()

        # Slider to choose how many values in pie
        max_values = st.slider(
            f"Nombre de {name} à afficher",
            min_value=3,
            max_value=min(max, len(freqs_all)),
            value=15,
        )

        freqs = freqs_all.nlargest(max_values)

        fig3, ax3 = plt.subplots()
        ax3.pie(freqs, labels=freqs.index, autopct="%1.1f%%", startangle=90)
        ax3.axis("equal")  # Camembert bien rond
        st.pyplot(fig3)
    else:
        st.warning(f"La colonne '{column}' n'existe pas dans ce fichier.")


def plotly_pie(column, name, max=30):
    if column in df.columns:
        freqs_all = df[column].value_counts()

        # Slider to choose how many values in pie
        max_values = st.slider(
            f"Nombre de {name} à afficher",
            min_value=3,
            max_value=min(30, len(freqs_all)),
            value=15,
        )

        freqs = freqs_all.nlargest(max_values).reset_index()
        freqs.columns = ["name", "count"]

        fig3 = px.pie(
            freqs,
            names="name",
            values="count",
            title=f"Top {max_values} {name} les plus fréquents",
            hole=0.3,  # Donut style (optional)
        )

        fig3.update_traces(
            textinfo="label+value",  # name and value only
            textposition="outside",
            pull=[0.02] * len(freqs),  # space between slices
            marker=dict(line=dict(color="white", width=1)),
        )

        # no legend
        fig3.update_layout(showlegend=False)

        st.plotly_chart(fig3, use_container_width=True)

    else:
        st.warning(f"La colonne '{column}' n'existe pas dans ce fichier.")


# --- Configuration ---
st.set_page_config(page_title="Dashboard AAC Loans", layout="wide")

# --- Title ---
st.title("📊 Emprunts Visualisation de Données")


DATES = ["Date début", "Date fin", "Date retour"]


# --- upload file ---
@st.cache_data
def upload(csv_file):
    df = pd.read_csv(csv_file, sep=";")
    # normalization of certain columns
    # dates
    for d in DATES:
        df[d] = pd.to_datetime(df[d], errors="coerce")

    # Add binary column on late status
    df["late"] = (
        (df["Date fin"] < datetime.today()) & (df["Status"] == "Prêté")
    ).astype(int)
    return df


def view_stats(column, name):
    nb_values = df[column].notnull().sum()
    unique_values_count = df[column].nunique(dropna=True)
    st.write(f"{nb_values} emprunts de {unique_values_count} {name} uniques")


# Interface utilisateur pour charger le fichier
csv_file = st.file_uploader("Téléverser un fichier CSV", type="csv")

if csv_file is not None:
    df = upload(csv_file)

    st.sidebar.header("🗓️ Filtre par dates")

    start = "Date début"
    end = "Date fin"

    # use start date for filters
    df_valid = df.dropna(subset=[start])

    possible_years = sorted(df_valid[start].dt.year.dropna().unique())
    possible_months = {
        1: "Janvier",
        2: "Février",
        3: "Mars",
        4: "Avril",
        5: "Mai",
        6: "Juin",
        7: "Juillet",
        8: "Août",
        9: "Septembre",
        10: "Octobre",
        11: "Novembre",
        12: "Décembre",
    }

    # Menu déroulant pour l’année
    selected_year = st.sidebar.selectbox(
        "Année", options=["Tous"] + list(possible_years)
    )

    # Menu déroulant pour le mois
    selected_month = st.sidebar.selectbox(
        "Mois", options=["Tous"] + list(possible_months.values())
    )

    if selected_year != "Tous":
        df = df[df[start].dt.year == int(selected_year)]

    if selected_month != "Tous":
        mois_num = list(possible_months.keys())[
            list(possible_months.values()).index(selected_month)
        ]
        df = df[df[start].dt.month == mois_num]

    st.sidebar.header("✅ Statut de l'emprunt")

    ongoing = st.sidebar.checkbox("En cours")
    if ongoing:
        df = df[df["Status"] == "Prêté"]

    late = st.sidebar.checkbox("En retard")
    if late:
        df = df[df["late"] == True]

    # --- pie charts loans ---
    st.subheader("🥧 Emprunts par utilisateur")
    view_stats("Emprunteur nom", "Emprunteurs")

    plotly_pie("Emprunteur nom", "noms", max=30)

    # --- pie charts loans ---
    st.subheader("🥧 Fréquence d'emprunts par jeu")
    view_stats("Titre", "jeux")
    plotly_pie("Titre", "jeux", max=30)

else:
    st.info("Veuillez téléverser un fichier CSV pour commencer.")

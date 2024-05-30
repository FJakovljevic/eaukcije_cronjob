import pandas as pd
import streamlit as st
from datetime import datetime
from steamlit_filterable_df import StreamlitFilterableDF

st.set_page_config(layout="wide", page_title="Bolje E-Aukcije")

# lose the bot padding...
st.markdown("""
<style>
.block-container{
    padding-top: 3rem;
    padding-left: 3rem;
    padding-right: 3rem;
    padding-bottom: 0rem;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("https://raw.githubusercontent.com/FJakovljevic/eaukcije_cronjob/main/data/EAukcija_dump.csv")
    df['Datum'] = pd.to_datetime(df['Datum'])
    return df

def get_auctions_df():
    df = load_data()

    # clearing cache when its passed the day
    if df['Datum'].max().date() < datetime.today().date():
        st.cache_data.clear()
 
    return load_data()

st.header("Bolja E-Aukcija", divider="green")
st.markdown("""
Kako sajt [eaukcija.sud.rs](https://eaukcija.sud.rs/#/) ne nudi mogućnosti filtriranja aukcija i veoma je nepregledan za korišćenje, 
razvijen je ovaj sajt koji upravo nudi mogućnosti filtriranja i pregleda svih budućih aukcija. 
Moguće je filtrirati i sortirati po `Tipu`, `Kategoriji`, `Opstini`, `Početnoj ceni` i `datumu`, 
a za svaku aukciju prisutan je link ka originalu na sajtu ministarstva. 
**Dobrodošli na Bolju E-Aukciju!**

Aukcije:
""")

columns_to_filter = ["Tip", "Kategorija", "Opstina", "Ponovljena", "Pocetna Cena", "Datum"]
columns_formatting = {
    "Link": st.column_config.LinkColumn("Link", display_text="Otvori"),
    "Datum": st.column_config.DatetimeColumn("Datum", format="D MMM YYYY, h:mm a"),
    "Ponovljena": st.column_config.CheckboxColumn("Ponovljena"),
    "Pocetna Cena": st.column_config.NumberColumn("Pocetna Cena"),
    "Procenjena Vrednost": st.column_config.NumberColumn("Procenjena Vrednost"),
}

dynamic_filters = StreamlitFilterableDF(df=get_auctions_df(), columns_to_filter=columns_to_filter)
dynamic_filters.display(use_container_width=True, column_config=columns_formatting, hide_index=True, height=500)

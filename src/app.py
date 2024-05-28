import pandas as pd
from streamlit_patched_ads import st
from steamlit_filterable_df import StreamlitFilterableDF

st.set_page_config(layout="wide", page_title="Bolje E-Aukcije")

st.header("Bolja E-Aukcija", divider="green")
st.markdown(
    """
Kako sajt [eaukcija.sud.rs](https://eaukcija.sud.rs/#/) ne nudi mogućnosti filtriranja aukcija i veoma je nepregledan za korišćenje, 
razvijen je ovaj sajt koji upravo nudi mogućnosti filtriranja i pregleda svih budućih aukcija. 
Moguće je filtrirati i sortirati po `Tipu`, `Kategoriji`, `Opstini`, `Početnoj ceni` i `datumu`, 
a za svaku aukciju prisutan je link ka originalu na sajtu ministarstva. 
**Dobrodošli na Bolju E-Aukciju!**

Aukcije:
"""
)


@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/FJakovljevic/eaukcije_cronjob/main/data/EAukcija_dump.csv"
    return pd.read_csv(url)


columns_to_filter = ["Tip", "Kategorija", "Opstina", "Ponovljena", "Pocetna Cena", "Datum"]
columns_formatting = {
    "Link": st.column_config.LinkColumn("Link", display_text="Otvori"),
    "Datum": st.column_config.DatetimeColumn("Datum", format="D MMM YYYY, h:mm a"),
    "Ponovljena": st.column_config.CheckboxColumn("Ponovljena"),
    "Pocetna Cena": st.column_config.NumberColumn("Pocetna Cena"),
    "Procenjena Vrednost": st.column_config.NumberColumn("Procenjena Vrednost"),
}

dynamic_filters = StreamlitFilterableDF(df=load_data(), columns_to_filter=columns_to_filter)
dynamic_filters.display(use_container_width=True, column_config=columns_formatting, hide_index=True, height=500)


st.html("""<iframe src="adsens.html" width="100%" height="200" frameborder="0" scrolling="no"></iframe>""")
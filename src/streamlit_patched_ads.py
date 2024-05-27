import importlib
import pathlib

from bs4 import BeautifulSoup

print("Patching streamlit for ads")
# loading streamlit index html
streamlit_path = importlib.util.find_spec("streamlit").origin
index_path = pathlib.Path(streamlit_path).parent / "static" / "index.html"
with open(index_path, "r") as file:
    html_content = file.read()
index_html = BeautifulSoup(html_content, "lxml")

# creating ads html
ads_html = """<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1234567890123456" crossorigin="anonymous"></script>"""
ads_tag = BeautifulSoup(ads_html, "html.parser")

# if tag doesn't exist add it to header and save file
if not index_html.find("script", src=ads_tag.script.get("src")):
    index_html.head.append(ads_tag)
    index_html_with_ads = index_html.prettify()
    index_path.write_text(index_html_with_ads)


print("Importing streamlit")
import streamlit as st  # noqa: E402

__all__ = ["st"]

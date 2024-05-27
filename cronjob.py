import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pandas as pd
import requests
from tqdm import tqdm


def api_post_request(url, data=None):
    return requests.post(url, data=data).json()["Data"]


def get_all_auctions():
    data = {"ItemCount": 10_000, "PageCount": "1"}
    auctions = api_post_request("https://eaukcija.sud.rs/WebApi.Proxy/api/EAukcija/GetAuctionsInPrediction", data)
    return pd.DataFrame(auctions["Auctions"])


def get_property_details(property_id, property_type):
    if property_type == "MovableProperties":
        url = "https://eaukcija.sud.rs/WebApi.Proxy/api/EAukcija/GetMovablePropertyDetails"
    elif property_type == "ImmovableProperties":
        url = "https://eaukcija.sud.rs/WebApi.Proxy/api/EAukcija/GetImmovablePropertyDetails"
    elif property_type == "CommonProperties":
        url = "https://eaukcija.sud.rs/WebApi.Proxy/api/EAukcija/GetCommonPropertyDetails"
    else:
        raise ValueError("`property_type` must be one of: MovableProperties, ImmovableProperties, CommonProperties")

    property = api_post_request(url, {"AuctionId": str(property_id)})
    property["Url"] = f"https://eaukcija.sud.rs/#/aukcije/{property['Id']}"

    for key_to_remove in ["AuctionBidResponseModel", "GuaranteeSlip", "OnWishList", "Images", "VideoLink"]:
        del property[key_to_remove]

    return property


def get_all_property_details():
    df = get_all_auctions()
    with ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(get_property_details, df.Id, df.PropertyType), total=len(df), mininterval=30))
    return pd.json_normalize(results)


def create_dump():
    df = get_all_property_details()
    df["StartDate"] = pd.to_datetime(df["StartDate"]).dt.date
    df["Percentage"] = (100 * df["StartingPrice"] / df["EstimatedPrice"]).round()

    type_map = {'MovableProperties': 'Pokretnosti', 'ImmovableProperties': 'Nepokretnosti', 'CommonProperty':'Kombinovano'}
    df["PropertyType"] = df["PropertyType"].map(type_map)

    translation_dict = {
        "StartDate": "Datum",
        "IsFirstSale": "Prva Prodaja",
        "Place.Municipality": "Opstina",
        "StartingPrice": "Pocetna Cena",
        "EstimatedPrice": "Procenjena Vrednost",
        "Percentage": "%",
        "PropertyType": "Tip",
        "Category.Name": "Kategorija",
        "Description": "Opis",
        "Url": "Link",
    }

    df = df.rename(columns=translation_dict)[translation_dict.values()]

    filename = os.path.join(DIRECTORY, DUMP_NAME)
    df.to_csv(filename, index=False)


def update_log():
    filename = os.path.join(DIRECTORY, LOG_NAME)
    df = pd.DataFrame([{"cronjob_run": datetime.now()}])

    if not os.path.isfile(filename):
        df.to_csv(filename, index=False)

    else:
        df.to_csv(filename, mode="a", header=False, index=False)


DIRECTORY = "data"
LOG_NAME = "runs.csv"
DUMP_NAME = "EAukcija_dump.csv"

if __name__ == "__main__":

    # create directory if it doesnt exist
    if not os.path.exists(DIRECTORY):
        os.makedirs(DIRECTORY)

    create_dump()
    update_log()

import json
from lxml import html
from io import StringIO
import requests
import os


WIKIPEDIA_COUNTRY_CODES_URL = "https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes"

TABLE = "/html/body/div[3]/div[3]/div[5]/div[1]/table/tbody"
TABLE_XPATH = '//*[@id="mw-content-text"]/div[1]/table/tbody/tr'
FIRST_ROW_INDEX = 2

COUNTRY_NAME_COLUMN_INDEX = 0
OFFICIAL_STATE_NAME_COLUMN_INDEX = 1
SOVEREIGNTY_COLUMN_INDEX = 2
ISO_3166_1_ALPHA_2_CODE_COLUMN_INDEX = 3
ISO_3166_1_ALPHA_3_CODE_COLUMN_INDEX = 4
ISO_3166_1_NUMERIC_CODE_COLUMN_INDEX = 5
ISO_3166_2_SUBDIVISION_LINK_COLUMN_INDEX = 6
COUNTRY_CODE_TOP_LEVEL_DOMAIN_COLUMN_INDEX = 7

UN_MEMBER_STATE = "UN member state"
UN_OBSERVER = "UN observer"

EN_WIKIPEDIA_BASEURL = "https://en.wikipedia.org"


if __name__ == "__main__":
    filter_sovereignty = [UN_MEMBER_STATE]

    response = requests.get(WIKIPEDIA_COUNTRY_CODES_URL)
    html_content = response.content.decode()
    root = html.fromstring(html_content)
    table = root.xpath(TABLE_XPATH)
    tbody = table[FIRST_ROW_INDEX:]
    
    countries = {}
    for row in tbody:
        columns = row.findall("td")
        if len(columns) > 1:
            sovereignty_html = columns[SOVEREIGNTY_COLUMN_INDEX]
            sovereignty = sovereignty_html.text_content().strip()

            if sovereignty in filter_sovereignty:
                # Country name
                country_name_html = columns[COUNTRY_NAME_COLUMN_INDEX][1]
                country_name = country_name_html.text_content().strip()

                # Official state name and wiki link
                state_name_html = columns[OFFICIAL_STATE_NAME_COLUMN_INDEX][0]
                state_name = state_name_html.text_content()
                country_wiki_link = EN_WIKIPEDIA_BASEURL + state_name_html.get("href")

                # ISO 3166-1 alpha-2 code
                alpha2_html = columns[ISO_3166_1_ALPHA_2_CODE_COLUMN_INDEX][0].find("span")
                alpha2 = alpha2_html.text_content()
                
                # ISO 3166-1 alpha-3 code
                alpha3_html = columns[ISO_3166_1_ALPHA_3_CODE_COLUMN_INDEX][0].find("span")
                alpha3 = alpha3_html.text_content()

                # ISO 3166-1 numeric code
                numeric_code_html = columns[ISO_3166_1_NUMERIC_CODE_COLUMN_INDEX][0].find("span")
                numeric_code = numeric_code_html.text_content()

                # Top level domain
                top_level_domain_html = columns[COUNTRY_CODE_TOP_LEVEL_DOMAIN_COLUMN_INDEX]
                used_domain_html = top_level_domain_html.findall("a")[-1]  # There can be multiple domains in this column - therefore use the last
                top_level_domain = used_domain_html.text_content()[1:]

                country = {
                    "country_name": country_name,
                    "official_state_name": state_name,
                    "wiki_link": country_wiki_link,
                    "alpha2": alpha2,
                    "alpha3": alpha3,
                    "numeric": numeric_code,
                    "top_level_domain": top_level_domain
                }
                countries[alpha2] = country

    with open("data/un_countries.json", "w+") as f:
        f.write(json.dumps(countries, indent=2))

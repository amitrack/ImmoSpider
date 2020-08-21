# -*- coding: utf-8 -*-
import json
import logging
import re

import scrapy

from immospider.items import ImmoscoutItem


def camel_case_split(identifier):
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z]['
                          'a-z])|$)', identifier)
    return [m.group(0) for m in matches]


class ImmoscoutSpider(scrapy.Spider):
    name = "immoscout"
    allowed_domains = ["immobilienscout24.de"]
    # start_urls = ['https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Berlin/Berlin']
    # start_urls = ['https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Berlin/Berlin/Lichterfelde-Steglitz_Nikolassee-Zehlendorf_Dahlem-Zehlendorf_Zehlendorf-Zehlendorf/2,50-/60,00-/EURO--800,00/-/-/']

    # The immoscout search results are stored as json inside their javascript. This makes the parsing very easy.
    # I learned this trick from https://github.com/balzer82/immoscraper/blob/master/immoscraper.ipynb .
    script_xpath = './/script[contains(., "IS24.resultList")]'
    next_xpath = '//div[@id = "pager"]/div/a/@href'
    custom_settings = {"CONNECTION_STRING": "EXAMPLE_CONNECTION_STRING",
                       "CRAWL_ID": "DEFAULT"}

    def start_requests(self):
        yield scrapy.Request(self.url)

    def parse(self, response):
        lines = response.xpath(self.script_xpath).extract_first()
        if lines is None:
            logging.info(
                "Immoscout24 has flagged this crawler as a robot , Stopping crawl")
            return None
        for line in response.xpath(self.script_xpath).extract_first().split(
            '\n'):
            if line.strip().startswith('resultListModel'):
                immo_json = line.strip()
                immo_json = json.loads(immo_json[17:-1])
                if immo_json["searchResponseModel"]["resultlist.resultlist"][
                    "paging"]["numberOfListings"] == 1:
                    results = [r["resultlistEntry"] for r in
                               immo_json["searchResponseModel"][
                                   "resultlist.resultlist"][
                                   "resultlistEntries"]]

                else:
                    results = \
                        immo_json["searchResponseModel"][
                            "resultlist.resultlist"][
                            "resultlistEntries"][0]["resultlistEntry"]

                for result in results:
                    item = ImmoscoutItem()
                    data = result["resultlist.realEstate"]
                    item["creation_date"] = result.get("@creation")
                    item["modification_date"] = result.get("@modification")
                    item["publish_date"] = result.get("@publishDate")
                    self.parse_transaction(data["@xsi.type"], item)
                    item['immo_id'] = data['@id']
                    item['url'] = response.urljoin(
                        "/expose/" + str(data['@id']))
                    item['title'] = data['title']
                    address = data['address']
                    item['city'] = address['city']
                    item['zip_code'] = address.get('postcode', "")
                    item['district'] = address.get('quarter', "")
                    item["address"] = address["description"]["text"]
                    item["price"] = data["price"]["value"]
                    item["sqm"] = data["livingSpace"]
                    item["rooms"] = data["numberOfRooms"]
                    item["real_estate_company"] = data.get("realtorCompanyName")
                    if "calculatedPrice" in data:
                        item["extra_costs"] = (
                            data["calculatedPrice"]["value"] - data["price"][
                            "value"])
                    else:
                        item["extra_costs"] = 0
                    item["kitchen"] = data.get("builtInKitchen", False)
                    item["balcony"] = data.get("balcony", False)
                    item["garden"] = data.get("garden", False)
                    item["private"] = data.get("privateOffer",
                                               "false") is "true"
                    item["area"] = data.get("plotArea", 0)
                    item["cellar"] = data.get("cellar", "false") is "true"

                    try:
                        contact = data['contactDetails']
                        item['contact_name'] = contact['firstname'] + " " + \
                                               contact[
                                                   "lastname"]
                    except:
                        item['contact_name'] = None

                    try:
                        item['media_count'] = len(
                            data['galleryAttachments']['attachment'])
                    except:
                        item['media_count'] = 0

                    try:
                        item['lat'] = address['wgs84Coordinate']['latitude']
                        item['lng'] = address['wgs84Coordinate']['longitude']
                    except Exception as e:
                        # print(e)
                        item['lat'] = None
                        item['lng'] = None

                    yield item

        next_page_list = response.xpath(self.next_xpath).extract()
        if next_page_list:
            next_page = next_page_list[-1]
            print("Scraping next page", next_page)
            if next_page:
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse)

    def parse_transaction(self, type_str: str, item: ImmoscoutItem):
        type_map = {"Apartment": "WOHNUNG", "House": "HAUS"}
        transaction_map = {"Rent": "MIETE", "Buy": "KAUF"}
        type_str = type_str.replace("search:", "")
        if type_str == "FlatShareRoom":
            item["type"] = "ZIMMER"
            item["transaction_type"] = "MIETE"
            return None
        parsed = camel_case_split(type_str)
        item["type"] = type_map[parsed[0]]
        item["transaction_type"] = transaction_map[parsed[1]]

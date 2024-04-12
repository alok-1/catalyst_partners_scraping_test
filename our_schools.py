import argparse
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

class Scraper:
    def __init__(self, url):
        self.url = url
        self.ss = requests.Session()

    def fetch_page(self,url,method,headers=None ,post = None):
        if method == "get":
            page_source = self.ss.get(url)
            if page_source.status_code == 200:
                # Parse the HTML content of the page
                soup = BeautifulSoup(page_source.text, 'html.parser')
            return soup
        if method == "post":
            page_source = self.ss.post(url, headers= headers, data=post)
            if page_source.status_code == 200:
                # Parse the HTML content of the page

                json_data = json.loads(page_source.text)[2]["data"] if page_source.text else None

                soup = BeautifulSoup(json_data, features="html.parser") if json_data else None
                return soup
        return None

    def scrape_website(self):
            data = []
            try:
                open_url = self.fetch_page(self.url,'get')
                school_name = open_url.find("title").text.split("|")[1].strip()
                address_element = open_url.find('p', class_='address')
                address = address_element.text.strip().split('\n')[0] if address_element else None
                state = address_element.text.strip().split('\n')[1].strip().split(",")[0] if address_element else None
                zip = address_element.text.strip().split('\n')[1].strip().split(",")[1].strip().split(" ")[1] if address_element else None
                view_dom_id = open_url.find('script', {'data-drupal-selector': 'drupal-settings-json'}).string.strip().split('"view_dom_id":"')[1].split('"')[0]
                next_page = True if open_url.find('li', {'class': 'next'}) else False
                page = 0
                node = open_url.find('link', {'rel': 'shortlink'}).get("href").split("org")[1]
                while next_page:
                    url = 'https://isd110.org/views/ajax?_wrapper_format=drupal_ajax'

                    headers = {
                        'accept': 'application/json, text/javascript, */*; q=0.01',
                        'accept-language': 'en-US,en;q=0.9,hi;q=0.8',
                        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'cookie': '_gid=GA1.2.426032854.1712829454; _ga_TJHT1BKY5Q=GS1.1.1712916974.3.1.1712917030.0.0.0; _ga=GA1.2.2068163061.1712829454',
                        'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjQwMTI0MTkiLCJhcCI6IjE1ODg4Mzc0MjUiLCJpZCI6IjIyOWViNjljOGYwM2Y4NTUiLCJ0ciI6IjIyMjllM2UwYTU1ZWRlMDU4ZjViOWFkYjI4MDJlNDY2IiwidGkiOjE3MTI5MjAzNjE0MjQsInRrIjoiNjY2ODYifX0=',
                        'origin': 'https://isd110.org',
                        'referer': self.url,
                        'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-fetch-dest': 'empty',
                        'sec-fetch-mode': 'cors',
                        'sec-fetch-site': 'same-origin',
                        'traceparent': '00-2229e3e0a55ede058f5b9adb2802e466-229eb69c8f03f855-01',
                        'tracestate': '66686@nr=0-1-4012419-1588837425-229eb69c8f03f855----1712920361424',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                        'x-newrelic-id': 'UAYGU1JSARABUVRWBgUDV1YI',
                        'x-requested-with': 'XMLHttpRequest'
                    }

                    post_data = {
                        'view_name': 'staff_teaser',
                        'view_display_id': 'default',
                        'view_args': 'all/5',
                        'view_path': node,
                        'view_base_path': '',
                        'view_dom_id': view_dom_id,
                        'pager_element': '0',
                        'page': str(page),
                        '_drupal_ajax': '1',
                        'ajax_page_state[theme]': 'wac',
                        'ajax_page_state[theme_token]': '',
                        'ajax_page_state[libraries]': 'aeon/base,blazy/bio.ajax,core/html5shiv,core/picturefill,google_analytics/google_analytics,gtranslate/jquery-slider,micon/micon,paragraphs/drupal.paragraphs.unpublished,system/base,ux/ux.auto_submit,ux_form/ux_form.input,ux_header/ux_header,ux_offcanvas_menu/ux_offcanvas_menu,views/views.ajax,views/views.module,wac/base'
                    }
                    response = self.fetch_page(url,'post',headers,post_data)
                    # Check if the request was successful
                    if response:
                        next_page = True if response.find('li', {'class': 'next'}) else False
                        all_div = response.find_all("div",{'class':'views-row'})

                        for get_div in all_div:
                            row_data = {
                                "school_name": school_name,
                                "address": address,
                                "state": state,
                                "zip": zip
                            }
                            name = get_div.find('h2',{"class":'title'}).text
                            row_data["first_name"] = name.split(", ")[0] if name else None
                            row_data["last_name"] = name.split(", ")[1] if name else None
                            title = get_div.find('div',{"class":'job-title'}).text
                            row_data["title"] = title.strip() if title else None
                            phone = get_div.find('div',{"class":'phone'}).text
                            row_data["phone"] = phone if phone else None
                            email = get_div.find('div',{"class":'email'}).text
                            row_data["phone"] = email if email else None
                            data.append(row_data)
                    else:
                        next_page = False 
                    
                    page += 1
                
            except Exception as e:
                print(e)
            return data

    def save_to_csv(self, json_data_list):
        df = pd.DataFrame([data for data in json_data_list])

        # Write DataFrame to CSV file
        csv_filename = df["school_name"][0].replace(" ",'_')+'.csv'
        df.to_csv(csv_filename, index=False)

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='nevadaepro scraper')
    parser.add_argument('url', type=str, help='URL of the website to scrape')
    args = parser.parse_args()
    # Create a Scraper object
    scraper = Scraper(args.url)
    
    # Scrape the website
    scraped_data = scraper.scrape_website()
    
    if scraped_data:
        # Save scraped data to CSV file
        scraper.save_to_csv(scraped_data)
        print(f"Scraped data saved")

if __name__ == "__main__":
    main()

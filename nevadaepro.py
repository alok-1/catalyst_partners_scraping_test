import argparse
import requests
from bs4 import BeautifulSoup
import csv
import math
import os
import json

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
            if 'bso/external/bidDetail.sdo' in url:
                return page_source
            if page_source.status_code == 200:
                # Parse the HTML content of the page
                soup = BeautifulSoup(page_source.text, features="xml")
                return soup
        return None
    
    def download_file(self,url, folder_path,file_name,bid_solicitation,csrf_token):
        file_name = os.path.join(folder_path, file_name+'.pdf')
        id  = url.split("File('")[1].split("');")[0]
        url = 'https://nevadaepro.com/bso/external/bidDetail.sdo'
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9,hi;q=0.8',
            'cookie': 'XSRF-TOKEN=' + csrf_token + '; JSESSIONID=825CCBF0C201E24FCD46D1127E115E0A; _ga=GA1.1.1574407783.1712819591; dtCookie=v_4_srv_12_sn_04923BCC1C84B1C2837950127BF2DBAB_perc_100000_ol_0_mul_1_app-3A37bc123ce5d9a8ed_0; AWSALB=Cdq+MnoS3OvnIQvp551QQCpvL2TXBsceQKiBX4+Fiw9Uk6xfmZ9bzSmzDfT216qSxK8e1fPUYBfS4USP1kec7ergOspbODM1j7nrst4GZGszI65tb4RgDccXNdfe; AWSALBCORS=Cdq+MnoS3OvnIQvp551QQCpvL2TXBsceQKiBX4+Fiw9Uk6xfmZ9bzSmzDfT216qSxK8e1fPUYBfS4USP1kec7ergOspbODM1j7nrst4GZGszI65tb4RgDccXNdfe; _ga_JGSX0KVE09=GS1.1.1712837922.4.1.1712841162.0.0.0',
            'origin': 'https://nevadaepro.com',
            'referer': 'https://nevadaepro.com/bso/external/bidDetail.sdo?docId=80DOT-S2801&external=true&parentUrl=close',
            'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        post_data = {
            '_csrf': csrf_token,
            'mode': 'download',
            'bidId': bid_solicitation,
            'docId': bid_solicitation,
            'currentPage': '1',
            'querySql': '',
            'downloadFileNbr': id,
            'itemNbr': 'undefined',
            'parentUrl': 'close',
            'fromQuote': '',
            'destination': ''
        }

        response = self.fetch_page(url,'post',headers,post_data)

        # Check if the request was successful
        if response.status_code==200:
            # Save the file to a local directory
            with open(file_name, 'wb') as f:
                f.write(response.content)
            print("File downloaded successfully.")
        else:
            print(f"Failed to download the file. Status code: {response.status_code}")
        return file_name

    def scrape_website(self):
            data = []
            try:
                open_url = self.fetch_page(self.url,'get')
                pages = open_url.find("span",{"class":"ui-paginator-current"})
                page_count = int(pages.text.split("of ")[-1]) if pages else None
                total_page = math.ceil(page_count/25)
                csrf_token = open_url.find('input', {'name':'_csrf'}).get("value")
                for page in range(1,total_page+1):
                    count = 0
                    url = 'https://nevadaepro.com/bso/view/search/external/advancedSearchBid.xhtml'

                    headers = {
                        'accept': 'application/xml, text/xml, */*; q=0.01',
                        'cookie': 'XSRF-TOKEN='+ csrf_token +'; JSESSIONID=23995E2D42331EB987D7E86D2C832252; _ga=GA1.1.1574407783.1712819591; dtCookie=v_4_srv_12_sn_04923BCC1C84B1C2837950127BF2DBAB_perc_100000_ol_0_mul_1_app-3A37bc123ce5d9a8ed_0; _ga_JGSX0KVE09=GS1.1.1712849662.7.1.1712849736.0.0.0; AWSALB=CkWo2s3inv5lOfOExVdOAoieQZDhNpE32H/r+9FQYcNmcaHTuRTLxygGt7GnEBPcp6UqqRnZSDRQoCtc5HCB97ww2Mso3JeFAT2lBh5jy77E9juTA+FkWgFcPbx4; AWSALBCORS=CkWo2s3inv5lOfOExVdOAoieQZDhNpE32H/r+9FQYcNmcaHTuRTLxygGt7GnEBPcp6UqqRnZSDRQoCtc5HCB97ww2Mso3JeFAT2lBh5jy77E9juTA+FkWgFcPbx4',
                        'faces-request': 'partial/ajax',
                        'origin': 'https://nevadaepro.com',
                        'referer': 'https://nevadaepro.com/bso/view/search/external/advancedSearchBid.xhtml?openBids=true',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-fetch-dest': 'empty',
                        'sec-fetch-mode': 'cors',
                        'sec-fetch-site': 'same-origin',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                        'x-dtpc': '12$449662463_208h14vSFUGSBJPBFBCQEDGKVATBHFCSUCUVPLJ-0e0',
                        'x-requested-with': 'XMLHttpRequest',
                    }

                    post_data = {
                        'javax.faces.partial.ajax': 'true',
                        'javax.faces.source': 'bidSearchResultsForm:bidResultId',
                        'javax.faces.partial.execute': 'bidSearchResultsForm:bidResultId',
                        'javax.faces.partial.render': 'bidSearchResultsForm:bidResultId',
                        'bidSearchResultsForm:bidResultId': 'bidSearchResultsForm:bidResultId',
                        'bidSearchResultsForm:bidResultId_pagination': 'true',
                        'bidSearchResultsForm:bidResultId_first': str(count),
                        'bidSearchResultsForm:bidResultId_rows': '25',
                        'bidSearchResultsForm:bidResultId_encodeFeature': 'true',
                        'bidSearchResultsForm': 'bidSearchResultsForm',
                        '_csrf': csrf_token,
                        'openBids': 'true',
                        'javax.faces.ViewState': '-2839723238214539978:3222054479213065380'
                    }
                    open_url = self.fetch_page(url,'post',headers,post_data)
                    find_all = BeautifulSoup(open_url.text.split('</tr>-')[0]+'</tr>', 'html.parser')
                    count += 25
                    # aa = 1
                    # tbody = open_url.find('tbody', id='bidSearchResultsForm:bidResultId_data')
                    if find_all:
                        rows = find_all.find_all('tr')
                        for row in rows:
                            row_data = {
                                "bid_solicitation": '',
                                "buyer": '',
                                "description": '',
                                "bid_opening_date": '',
                                "bid_detail": ''
                            }
                            # Find all cells within the row
                            cells = row.find_all('td', role='gridcell')
                            bid_detail_url = cells[0].find('a').get('href')
                            row_data["bid_solicitation"] = cells[0].text
                            row_data["buyer"] = cells[5].text
                            row_data["description"] = cells[6].text
                            row_data["bid_opening_date"] = cells[7].text
                            if bid_detail_url:
                                bid_page = self.fetch_page("".join(['https://nevadaepro.com', bid_detail_url]),'get')
                                folder_path = "download_file/"+row_data["bid_solicitation"]
                                if not os.path.exists(folder_path):
                                    os.makedirs(folder_path)

                                bid_number = bid_page.find('td', string='Bid Number:')
                                bid_number = bid_number.find_next_sibling('td').get_text(strip=True) if bid_number else None

                                purchaser = bid_page.find('td', string='Purchaser:')
                                purchaser = purchaser.find_next_sibling('td').get_text(strip=True) if purchaser else None

                                department = bid_page.find('td', string='Department:')
                                department = department.find_next_sibling('td').get_text(strip=True) if department else None

                                fiscal_year = bid_page.find('td', string='Fiscal Year:')
                                fiscal_year = fiscal_year.find_next_sibling('td').get_text(strip=True) if fiscal_year else None

                                alternate_id = bid_page.find('td', string='Alternate Id:')
                                alternate_id = alternate_id.find_next_sibling('td').get_text(strip=True) if alternate_id else None

                                info_contact = bid_page.find('td', string='Info Contac:')
                                info_contact = info_contact.find_next_sibling('td').get_text(strip=True) if info_contact else None

                                purchase_method = bid_page.find('td', string='Purchase Method:')
                                purchase_method = purchase_method.find_next_sibling('td').get_text(strip=True) if purchase_method else None

                                description = bid_page.find('td', string='Description:')
                                description = description.find_next_sibling('td').get_text(strip=True) if description else None

                                organization = bid_page.find('td', string='Organization:')
                                organization = organization.find_next_sibling('td').get_text(strip=True) if organization else None

                                location = bid_page.find('td', string='Location:')
                                location = location.find_next_sibling('td').get_text(strip=True) if location else None

                                type_code = bid_page.find('td', string='Type Code:')
                                type_code = type_code.find_next_sibling('td').get_text(strip=True) if type_code else None

                                required_date = bid_page.find('td', string='Required Date:')
                                required_date = required_date.find_next_sibling('td').get_text(strip=True) if required_date else None

                                bid_type = bid_page.find('td', string='Bid Type:')
                                bid_type = bid_type.find_next_sibling('td').get_text(strip=True) if bid_type else None

                                bid_opening_date = bid_page.find('td', string='Bid Opening Date:')
                                bid_opening_date = bid_opening_date.find_next_sibling('td').get_text(strip=True) if bid_opening_date else None

                                allow_electronic_quote = bid_page.find('td', string='Allow Electronic Quote:')
                                allow_electronic_quote = allow_electronic_quote.find_next_sibling('td').get_text(strip=True) if allow_electronic_quote else None

                                available_date = bid_page.find('td', string='Available Date:')
                                available_date = available_date.find_next_sibling('td').get_text(strip=True) if available_date else None

                                informal_bid_flag = bid_page.find('td', string='Informal Bid Flag:')
                                informal_bid_flag = informal_bid_flag.find_next_sibling('td').get_text(strip=True) if informal_bid_flag else None

                                pre_bid_conference = bid_page.find('td', string='Pre Bid Conference:')
                                pre_bid_conference = pre_bid_conference.find_next_sibling('td').get_text(strip=True) if pre_bid_conference else None

                                bulletin_desc = bid_page.find('td', string='Bulletin Desc:')
                                bulletin_desc = bulletin_desc.find_next_sibling('td').get_text(strip=True) if bulletin_desc else None

                                ship_to_address = bid_page.find('td', string='Ship-to Address:')
                                ship_to_address = ship_to_address.find_next_sibling('td').get_text(strip=True) if ship_to_address else None

                                bill_to_address = bid_page.find('td', string='Bill-to Address:')
                                bill_to_address = bill_to_address.find_next_sibling('td').get_text(strip=True) if bill_to_address else None

                                file_attachment_links = bid_page.find_all('a', href=lambda x: x and 'javascript:downloadFile' in x)

                                downloaded_file_paths = []
                                csrf_token = bid_page.find('input', {'name':'_csrf'}).get("value")


                                # Download each file and store the file paths
                                for link in file_attachment_links:
                                    file_url = link['href']
                                    file_name = link.text+'_'+ row_data["bid_solicitation"]
                                    file_path = self.download_file(file_url, folder_path,file_name,row_data["bid_solicitation"],csrf_token)
                                    downloaded_file_paths.append(file_path)

                                # Store the extracted details in a dictionary
                                extracted_data = {
                                   
                                        "Bid Number": bid_number,
                                        "Purchaser": purchaser,
                                        "Department": department,
                                        "Fiscal Year": fiscal_year,
                                        "Alternate Id": alternate_id,
                                        "Info Contac": info_contact,
                                        "Purchase Method": purchase_method,
                                        "Description": description,
                                        "Organization": organization,
                                        "Location": location,
                                        "Type Code": type_code,
                                        "Required Date": required_date,
                                        "Bid Type": bid_type,
                                        "Bid Opening Date": bid_opening_date,
                                        "Allow Electronic Quote": allow_electronic_quote,
                                        "Available Date": available_date,
                                        "Informal Bid Flag": informal_bid_flag,
                                        "Pre Bid Conference": pre_bid_conference,
                                        "Bulletin Desc": bulletin_desc,
                                        "Ship-to Address": ship_to_address,
                                        "Bill-to Address": bill_to_address,
                                        "file_attachment" : downloaded_file_paths
                                }                          
                            # Append row data to the list
                            row_data['bid_detail'] = extracted_data
                            data.append(row_data)  
            except Exception as e:
                print(e)
            return data

    def save_to_json(self, data):
        with open('nevadaepro_data.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

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
        scraper.save_to_json(scraped_data)
        print(f"Scraped data saved")

if __name__ == "__main__":
    main()

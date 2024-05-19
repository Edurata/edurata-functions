import requests
from bs4 import BeautifulSoup
import os
import urllib.parse

def call_proxy(url):
    print("calling: " + url)
    password = os.environ.get('CRAWL_PASSWORD')

    oxy_url = f'https://api.crawlbase.com/?token={password}&url={urllib.parse.quote_plus(url)}&format=json'
    print(oxy_url)
    response = requests.get(oxy_url)
    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code}")
        print(response.reason)
        return None
    response_json = response.json()
    return response_json["body"]

def extract_text_from_url(url):
    html_content = call_proxy(url)
    if not html_content:
        return None
    
    soup = BeautifulSoup(html_content, 'html.parser')
    text_content = soup.get_text(separator='\n', strip=True)
    return text_content

def handler(inputs):
    url = inputs['url']
    text_content = extract_text_from_url(url)
    return {'text': text_content}

# Call the handler function to scrape and return the text content
if __name__ == "__main__":
    url = "https://www.example.com"
    result = handler({'url': url})
    print(result)

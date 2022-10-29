import requests
import csv
from bs4 import BeautifulSoup
import urllib3


urllib3.disable_warnings()

HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
    }

def get_data():
    input = open('input.csv', 'r')
    reader = csv.reader(input)
    names = []
    geo = []
    for row in reader:
        if row[0] != 'Company Name':
            names.append(row[0])
            geo.append(row[1])
    return names, geo


def parse_google(name, geo):
    url = 'https://www.google.com/search'
    params = {
        'q': name + ' ' + geo,

    }
    response = requests.get(url, params=params, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    results = soup.select('a:has(h3)')
    blacklist_url = ('facebook.com', 'youtube.com', 'twitter.com', 'linkedin.com')

    for result in results:
        for black in blacklist_url:
            if black in result.get('href'):
                break
            if 'http:' in result.get('href'):
                print('Link found: ' + result.get('href'))
                return result.get('href')
    for result in results:
        for black in blacklist_url:
            if black in result.get('href'):
                continue
            if 'https:' in result.get('href'):
                print('Link found: ' + result.get('href'))
                return result.get('href')

    return None


def find_contact_page(url):
    pages = ['contact', 'contact-us/', 'contacts/', 'about/contact/', 'about/contact-us/', 'about/contacts/'
             ]
    for page in pages:
        try:
            response = requests.get(url + page, headers=HEADERS, allow_redirects=False)
        except:
            try:
                response = requests.get(url + page, headers=HEADERS, allow_redirects=False, verify=False)
            except: return None
        if response.status_code == 200:
            print('Contact page found: ' + url + page)
            return url + page
    print('Contact page not found: ' + url)
    return None


def find_email(url):
    try:
        response = requests.get(url, headers=HEADERS)
    except:
        try:
            response = requests.get(url, headers=HEADERS, verify=False)
        except:
            return None
    responce = response.text
    soup = BeautifulSoup(responce, 'html.parser')
    emails = soup.find_all('a', href=True)
    for email in emails:
        if '@' in email.text and '.' in email.text:
            print('Email found: ' + email.text)
            return email.text
    print('Email not found: ' + url)
    return None
    # email_index = responce.find('mailto:')
    # if email_index == -1:
    #     print('Email not found: ' + url)
    #     return None
    # email = responce[email_index + 7:email_index + 7 + 30]
    # email = email[:email.find('"')]
    # print('Email found: ' + email)
    # return email


def get_index_url_from_url(url):
    index_url = url[url.find('://') + 3:]
    index_url = index_url[:index_url.find('/')]
    return 'https://'+ index_url + '/'


def main():
    links = []
    names, geo = get_data()
    for i in range(len(names)):
        link = parse_google(names[i], geo[i])
        if link is not None:
            links.append(link)
        else:
            links.append('Not found')
    contact_page = []
    for link in links:
        if link[-1] != '/':
            link += '/'
        link = get_index_url_from_url(link)
        contact_page.append(find_contact_page(link))
    emails = []
    for key, page in enumerate(links):
        email = find_email(page)
        if email is None:
            if contact_page[key] is not None:
                email = find_email(contact_page[key])
            else:
                email = None
        emails.append(email)

    output = open('output.csv', 'w')
    writer = csv.writer(output)
    writer.writerow(['Company Name', 'Link', 'Contact page', 'Email'])
    for i in range(len(names)):
        writer.writerow([names[i], links[i], contact_page[i], emails[i]])
    output.close()


if __name__ == '__main__':
    main()

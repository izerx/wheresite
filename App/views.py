from django.shortcuts import render
from django.template import loader
from django.template.base import Template
from django.http import HttpResponse
import geoip2.database
from socket import gethostbyname
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def get_links(url):
    html = requests.get(url).text
    return outside_links(BeautifulSoup(html, 'html.parser'))

def outside_links(soup):
    links = []
    for link in soup.find_all('a'):
        link = link.get('href')
        try:
            if 'https://' in link or 'http://' in link:
                links.append(link)
        except Exception:
            continue
    return links

def get_coords(url):
    reader = geoip2.database.Reader('App/GeoLite2-City.mmdb')
    response = reader.city(gethostbyname(url))
    return response.location.latitude, response.location.longitude

def get_host_of_url(url):
    return '{uri.netloc}'.format(uri=urlparse(url))

def parse_page(url):
    response = []
    links = get_links(url)

    for link in links:
        try:
            response.append({'link': link, 'host': get_host_of_url(link), 'latitude': get_coords(get_host_of_url(link))[0], 'longitude': get_coords(get_host_of_url(link))[1]})
        except Exception:
            continue

    return response

def index(request):
    if request.is_ajax():
        url = request.POST.get('url')

        return HttpResponse(loader.get_template('include/main-section.html').render({'links': parse_page(url)}, request))

    return render(request, 'index.html')

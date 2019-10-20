from django.shortcuts import render
from django.template import loader
from django.template.base import Template
from django.http import HttpResponse
import geoip2.database
from socket import gethostbyname
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from .models import Results
from random import choice
from string import ascii_lowercase
from json import loads

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
    coords = []

    for link in links:
        try:
            coord = [get_coords(get_host_of_url(link))[0], get_coords(get_host_of_url(link))[1]]
            if coord not in coords:
                response.append({
                    'link': link,
                    'host': get_host_of_url(link),
                    'latitude': coord[0],
                    'longitude': coord[1]
                })
                coords.append(coord)
        except Exception:
            continue
        
    return response


def generate_save_url():
    save_url = ''.join(choice(ascii_lowercase) for i in range(6))
    return save_url if check_availability_save_url(save_url) else generate_save_url()

def check_availability_save_url(url):
    return False if Results.objects.filter(url = url).count() > 0 else True

def create_results(response, url):
    return Results.objects.create(url = url, save_url = generate_save_url(), points = response)

def show_results(request, save_url):
    result = Results.objects.get(save_url = save_url)
    links = result.points[1:-1].replace('}, ', '}|').split('|')

    return render(request, 'index.html', {'links': [loads(link.replace("'", '"')) for link in links], 'url': result.url, 'save_url': result.save_url})

def index(request):
    if request.is_ajax():
        parse_links = parse_page(request.POST.get('url'))

        results = create_results(parse_links, request.POST.get('url'))

        return HttpResponse(loader.get_template('include/main-section.html').render({'links': parse_links, 'save_url': results.save_url, 'url': request.POST.get('url')}, request))

    return render(request, 'index.html')

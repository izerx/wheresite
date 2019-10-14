from django.shortcuts import render
from django.template import loader
from django.template.base import Template
from django.http import HttpResponse
import geoip2.database
import socket
import requests
from bs4 import BeautifulSoup
from django.template.defaulttags import register

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
    response = reader.city(socket.gethostbyname(url))
    return response.location.latitude, response.location.longitude

def get_host_of_url(url):
    url = url.replace('//', '.')
    url_arr = url.split('.')[1:]
    url_fix = []
    domen = ''
    for el in url_arr:
        if '/' not in el:
            url_fix.append(el)
        else:
            for i in el:
                if i == '/':
                    break
                else:
                    domen += i
    url_fix.append(domen)
    try:
        url_fix.remove('www')
    except Exception:
        pass

    return '.'.join(url_fix)


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

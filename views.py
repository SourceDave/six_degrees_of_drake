from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from django.templatetags.static import static
from django.views.decorators.http import condition
from django.http import StreamingHttpResponse

import urllib2
import json
import re
import os
import six_degrees_of_drake

from six_degrees_of_drake.models import Artist
from six_degrees_of_drake import utils

SIX_DEGREES_OF_DRAKE_GRAPH_DOMAIN = 'graph/'

WIKIPEDIA_DOMAIN = 'http://en.wikipedia.org/wiki/'
WIKIPEDIA_API_QUERY_MODULE_ENDPOINT = \
    'http://en.wikipedia.org/w/api.php?action=query&list=search&format=json&srwhat=text&srlimit=3&continue=&srprop=snippet&srsearch=%22associated%20acts%22+intitle:'

# HOME PAGE
def index(request):
    all_artists_list = Artist.objects.all()
    context = {'artist_list': all_artists_list}
    return render(request, 'six_degrees_of_drake/index.html', context)

# GRAPH PAGE
def graph(request, artist_wiki_name):
    artist_url = WIKIPEDIA_DOMAIN + artist_wiki_name
    artist, just_created = Artist.get_or_create_with_url(artist_url)

    if artist:
        context = {'artist_wiki_name': artist_wiki_name}
        return render(request, 'six_degrees_of_drake/graph.html', context)
    else:
        return HttpResponse("Cannot find name of artist")

# INFO PAGE (Streams artist info)
@condition(etag_func=None)
def info(request, artist_wiki_name):
    artist_url = WIKIPEDIA_DOMAIN + artist_wiki_name
    artist, just_created = Artist.get_or_create_with_url(artist_url)

    if artist:
        return StreamingHttpResponse(artist.create_generator(), content_type="text/json")

# QUERY ENDPOINT
def query(request, query):
    # Make request to Wikipedia API, which has been given parameters to 
    # search for articles containing the string "associated acts"
    query_url = WIKIPEDIA_API_QUERY_MODULE_ENDPOINT + query

    # Transform response into list of artists
    response_object = utils.json_to_response_object(query_url)

    # Add artist + metatdata to result
    result = []
    for artist_entry in response_object[u'query'][u'search']:
        artist_dictionary = {}
        artist_dictionary['name'] = artist_entry[u'title']
        artist_dictionary['url'] = SIX_DEGREES_OF_DRAKE_GRAPH_DOMAIN + urllib2.quote(artist_entry[u'title'].encode('utf-8'))
        artist_dictionary['snippet'] = delete_tags(artist_entry[u'snippet']) + u'...'
        artist_dictionary['image_url'] = utils.get_artist_image_url(artist_entry[u'title'])
        # TODO get the url of the artist's image
        result.append(artist_dictionary)

    return JsonResponse(result, safe=False)

# STATS PAGE
def stats(request, artist_name):
    response = "This is the statistics page for %s <br><br>" % artist_name
    artist_list = Artist.objects.filter(name__iexact=artist_name)

    if artist_list:
        associated_acts_count = artist_list[0].associated_acts.count()
        response += "Number of associated acts: %s" % associated_acts_count
    else:
        response += "Cannot find name of artist"

    return HttpResponse(response)

def example_films(request):
    prefix = six_degrees_of_drake.__path__[0]
    filepath = prefix + static('six_degrees_of_drake/example_films.json')
    example_films = open(filepath, 'r')
    example_films_json = json.loads(example_films.read())
    return JsonResponse(example_films_json, safe=False)

def delete_tags(text):
    return re.sub('<.*?>', '', text)

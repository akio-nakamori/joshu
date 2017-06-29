from django.http import Http404
from django.shortcuts import render

from .models import Anime, AnimeTitle
import re


def index(request):
    list = Anime.objects.all()
    # title_list = AnimeTitle.objects.all()
    # anime_list = Anime.objects.filter(aid__in=AnimeTitle.objects.all()).all()
    anime_list = list
    latest_anime_list = sorted(anime_list, key=lambda m: m.title)
    return render(request, 'dashboard/index.html', {'latest_anime_list': latest_anime_list})


def detail(request, anime_id):
    try:
        anime = Anime.objects.get(aid=anime_id)

        if anime.description:
            # clean up description from pseudo-html
            p = re.compile('http://anidb.net/[a-z]{1,3}[0-9]{1,7}')
            data2 = p.sub('', anime.description)
            p = re.compile('(\[url=\]|\[/url\]|<br />)')
            data3 = p.sub('', data2)
        else:
            data3 = 'missing data'

        anime.description = data3

        anime_episode = anime.episode
        anime_relation = anime.relation
    except Anime.DoesNotExist:
        raise Http404("Anime does not exist")
    return render(request, 'dashboard/detail.html', {
        'anime': anime,
        'anime_episode': anime_episode,
        'anime_relation': anime_relation
    })


def graph(request, anime_id):
    try:
        anime = Anime.objects.get(aid=anime_id)
        anime_relation = anime.relation
        anime_sequel = anime.sequel
        anime_prequel = anime.prequel
        anime_same_setting = anime.same_setting
        anime_alternative_setting = anime.alternative_setting
        anime_alternative_version = anime.alternative_version
        anime_side_story = anime.side_story
        anime_parent_story = anime.parent_story
        anime_summary = anime.summary
        anime_full_story = anime.full_story
        anime_other = anime.other
    except Anime.DoesNotExist:
        raise Http404("Anime does not exist")
    return render(request, 'dashboard/graph.html', {
        'anime': anime,
        'anime_relation': anime_relation,
        'anime_sequel': anime_sequel,
        'anime_prequel': anime_prequel,
        'anime_same_setting': anime_same_setting,
        'anime_alternative_setting': anime_alternative_setting,
        'anime_alternative_version': anime_alternative_version,
        'anime_side_story': anime_side_story,
        'anime_parent_story': anime_parent_story,
        'anime_summary': anime_summary,
        'anime_full_story': anime_full_story,
        'anime_other': anime_other
    })

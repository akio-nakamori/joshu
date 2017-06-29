from django.contrib import admin

# Register your models here.
from .models import AnimeTitle, Anime, AnimeRelation, Episode

admin.site.register(AnimeTitle)
admin.site.register(Anime)
admin.site.register(AnimeRelation)
admin.site.register(Episode)

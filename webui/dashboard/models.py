from __future__ import unicode_literals

from django.db import models
import os
import sys


class AnimeTitle(models.Model):
    # id = models.BigIntegerField(primary_key=True)
    aid = models.BigIntegerField()
    titletype = models.CharField(max_length=512)
    lang = models.CharField(max_length=512)
    title = models.CharField(max_length=512)

    @property
    def picture(self):
        return Anime.objects.get(aid=self.aid).picture

    @property
    def title_short(self):
        if len(self.title) > 25:
            return self.title[0:25]
        else:
            return self.title

    class Meta:
        db_table = 'anime_title'


class Anime(models.Model):
    # id = models.BigIntegerField(primary_key=True)
    aid = models.BigIntegerField()

    year = models.CharField(max_length=16, null=False)
    type = models.CharField(max_length=16, null=False)

    nr_of_episodes = models.IntegerField(null=False)
    highest_episode_number = models.IntegerField(null=False)
    special_ep_count = models.IntegerField(null=False)
    air_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    url = models.CharField(max_length=512, null=True)
    picname = models.CharField(max_length=128, null=True)

    rating = models.FloatField(null=True)
    vote_count = models.IntegerField(null=False)
    temp_rating = models.FloatField(null=True)
    temp_vote_count = models.IntegerField(null=False)
    average_review_rating = models.FloatField(null=True)
    review_count = models.IntegerField(null=False)
    is_18_restricted = models.IntegerField(null=False)

    description = models.CharField(max_length=8192, null=True)

    ann_id = models.BigIntegerField(null=True)
    allcinema_id = models.BigIntegerField(null=True)
    animenfo_id = models.CharField(max_length=64, null=True)
    anidb_updated = models.DateTimeField(null=False)

    special_count = models.IntegerField(null=False)
    credit_count = models.IntegerField(null=False)
    other_count = models.IntegerField(null=False)
    trailer_count = models.IntegerField(null=False)
    parody_count = models.IntegerField(null=False)

    updated = models.DateTimeField(null=False)

    # relations = relationship("AnimeRelationTable", backref='anime')

    @property
    def title(self):
        try:
            return AnimeTitle.objects.filter(aid=self.aid).filter(titletype='main')[0].title
        except:
            try:
                return AnimeTitle.objects.filter(aid=self.aid)[0].title
            except:
                return 'Missing data'

    @property
    def title_short(self):
        if len(self.title) > 25:
            return self.title[0:25]
        else:
            return self.title

    @property
    def picture(self):
        return str(os.path.join("anime" + os.sep, self.picname)).replace('\\', '/')

    @property
    def relation(self):
        return self.get_relation(wanted_type="")

    def get_relation(self, wanted_type=""):
        # print >> sys.stderr, "wanted_type = " + str(wanted_type)
        anime_relation = []
        for x in AnimeRelation.objects.filter(anime_pk=self.id):
            try:
                y = Anime.objects.get(aid=x.related_aid)
                if y is not None:
                    allow_type = []
                    if wanted_type == "":
                        allow_type = {'sequel', 'prequel', 'same setting', 'alternative setting',
                                      'alternative version', 'side story', 'parent story', 'summary', 'full story',
                                      'other'}
                        # not allow_type 'music video','character',
                    else:
                        allow_type.append(wanted_type)

                    if x.relation_type in allow_type:
                        # print >> sys.stderr, "aid = " + str(x.related_aid)
                        print >> sys.stderr, "y.aid = " + str(y.aid)
                        print >> sys.stderr, "y.title = " + str(y.title)
                        # print >> sys.stderr, "y = " + str(y)
                        # print >> sys.stderr, "x = " + str(x.relation_type)

                        if wanted_type != "":
                            anime_relation.append(y)
                        else:
                            anime_relation.append((y, x.relation_type))
            except Exception as e:
                print >> sys.stderr, "E = " + str(e.message)
        return anime_relation

    @property
    def sequel(self):
        return self.get_relation(wanted_type='sequel')

    @property
    def prequel(self):
        return self.get_relation(wanted_type='prequel')

    @property
    def same_setting(self):
        return self.get_relation(wanted_type='same setting')

    @property
    def alternative_setting(self):
        return self.get_relation(wanted_type='alternative setting')

    @property
    def alternative_version(self):
        return self.get_relation(wanted_type='alternative version')

    @property
    def side_story(self):
        return self.get_relation(wanted_type='side story')

    @property
    def parent_story(self):
        return self.get_relation(wanted_type='parent story')

    @property
    def summary(self):
        return self.get_relation(wanted_type='summary')

    @property
    def full_story(self):
        return self.get_relation(wanted_type='full story')

    @property
    def other(self):
        return self.get_relation(wanted_type='other')

    @property
    def episode(self):
        anime_episode = []
        try:
            for x in Episode.objects.filter(aid=self.aid).extra(select={'int_epno': "CAST(REGEXP_SUBSTR(epno, '^[0-9]+') AS INTEGER)"}).order_by('int_epno'):
                anime_episode.append(x)
        except Exception as e:
            print >> sys.stderr, "E = " + str(e.message)
        return anime_episode

    class Meta:
        db_table = 'anime'


class AnimeRelation(models.Model):
    RELATION_TYPE_CHOICES = (
        ('sequel', 'sequel'),
        ('prequel', 'prequel'),
        ('same setting', 'same setting'),
        ('alternative setting', 'alternative setting'),
        ('alternative version', 'alternative version'),
        ('music video', 'music video'),
        ('character', 'character'),
        ('side story', 'side story'),
        ('parent story', 'parent story'),
        ('summary', 'summary'),
        ('full story', 'full story'),
        ('other', 'other')
    )

    # id = models.BigIntegerField(primary_key=True)
    # anime_pk = models.ForeignKey(Anime, on_delete=models.CASCADE)
    anime_pk = models.BigIntegerField()
    related_aid = models.BigIntegerField()
    relation_type = models.CharField(choices=RELATION_TYPE_CHOICES, max_length=20)

    class Meta:
        db_table = 'anime_relation'


class Episode(models.Model):
    TYPE_CHOICES = (
        ('regular', 'regular'),
        ('special', 'special'),
        ('credit', 'credit'),
        ('trailer', 'trailer'),
        ('parody', 'parody'),
        ('other', 'other')
    )
    # id = models.BigIntegerField(primary_key=True)
    aid = models.BigIntegerField()
    eid = models.BigIntegerField()
    length = models.IntegerField(null=False)
    rating = models.FloatField(null=True)
    votes = models.IntegerField(null=False)
    epno = models.CharField(max_length=8, null=False)
    title_eng = models.CharField(max_length=256, null=True)
    title_romaji = models.CharField(max_length=256, null=True)
    title_kanji = models.CharField(max_length=256, null=True)
    aired = models.DateField(null=True)
    type = models.CharField(choices=TYPE_CHOICES, max_length=10)
    updated = models.DateTimeField(null=False)

    class Meta:
        db_table = 'episode'

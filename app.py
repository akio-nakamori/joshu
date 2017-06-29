#!/usr/bin/env python
# -*- coding: utf-8 -*-

import adbb
import json
import logging
import os
import sys
import requests

#import adbb.db as db
import db
from sqlalchemy import *
# import objects


debug = True
config = []
_session = []
joshu_version = 3
joshu_name = "Joshu"
sql = ""
logger = None


# scan -> add files to unknown
# calc -> calculate ed2khash for unknown without hash
# rescan -> recognise files w/ ed2khash from unknown (online)
# reco -> look up all episodes and get all information about anime serie that is missing (episodes w/o series)
# image -> download all needed image for anime table
# missing -> look tru anime_relation and check if all of those anime have record in anime

# TODO: file_unknown flag that this file was checked so skip it with rescan
# TODO: anime_tags
# TODO: anime_cast main/secondary


# region Init()
def init():
    """
    Init all needed things to make joshu up and running
    :return:
    """
    global config
    config = json.load(open('./config.json'))
    global sql
    sql = "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4&use_unicode=0".format(config.get('db_user'),
                                                                                config.get('db_pass'),
                                                                                config.get('db_host'),
                                                                                config.get('db_port'),
                                                                                config.get('db_name'))
    init_logger()
    init_db()
    init_adbb()


def init_logger():
    # custom logger
    if os.name != 'posix':
        global logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        logger.setLevel(logging.DEBUG)
        lh = logging.StreamHandler()
        lh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(filename)s:%(lineno)d - %(message)s'))
        logger.addHandler(lh)

        lh = logging.handlers.SysLogHandler(address=(config.get('syslog_host'), 514))
        lh.setFormatter(logging.Formatter('joshu %(filename)s/%(funcName)s:%(lineno)d - %(message)s'))
        logger.addHandler(lh)


def init_adbb():
    if os.name != 'posix':
        adbb.init(config.get('user'), config.get('pass'), sql, debug=True, logger=logger)
    else:
        adbb.init(config.get('user'), config.get('pass'), sql, debug=True)


def init_db():
    global _session
    _session = db.init_db(sql)

# endregion


def log(message):
    """
    simple debug log function
    :param message: anything
    :return: print str of anything
    """
    if debug:
        print(message)


# region Command's

def command_scan(path):
    """
    Add files from given path to database
    :param path: path to scan
    """
    path = unicode(path)
    if os.path.exists(path):
        file_count = 0
        files_count = sum([len(files) for r, d, files in os.walk(path)])
        for dir_path, dir_names, file_names in os.walk(path):
            for file_name in file_names:
                file_count += 1
                log(str(file_count) + '/' + str(files_count))
                if os.path.splitext(file_name)[1][1:] in config.get('extension'):
                    _unknown = db.UnknownTable(path=os.path.join(dir_path, file_name))
                    _session.add(_unknown)
                    _session.commit()
                else:
                    print("{} contain unsupported file type".format(os.path.join(dir_path.encode('utf-8'), file_name.encode('utf-8'))))
    else:
        print("Path not found.")


def command_recognize_files(path=None, force=False):
    """
    Go tru not recognized files and try to match them to AniDB series
    :param path: path from which files should be rescanned
    :param force: include files with known ed2khash
    """
    if path:
        path = unicode(path)
        path += "%"
        if force:
            unknown_list = _session.query(db.UnknownTable).filter(db.UnknownTable.path.like(path, escape='/')).all()
        else:
            unknown_list = _session.query(db.UnknownTable).filter(and_(db.UnknownTable.path.like(path, escape='/'),
                                                                       db.UnknownTable.ed2khash.is_(None))).all()
    else:
        if force:
            unknown_list = _session.query(db.UnknownTable).all()
        else:
            unknown_list = _session.query(db.UnknownTable).filter(~db.UnknownTable.ed2khash.is_(None)).all()

    counter = 0
    counter_max = len(unknown_list)
    for unknown_file in unknown_list:
        counter += 1
        log(str(counter) + '/' + str(counter_max) + ' rows')
        try:
            _file = adbb.File(path=os.path.join(unknown_file.path), ed2khash=unknown_file.ed2khash)
            if _file.episode and _file.anime:
                print("'{}' contains episode {} of '{}'. Mylist state is '{}'".format(_file.path.encode('utf-8'),
                                                                                      _file.episode.episode_number,
                                                                                      _file.anime.title,
                                                                                      _file.mylist_state))
                _session.delete(unknown_file)
                _session.commit()
                print("db item deleted: '{}'".format(unknown_file.path.encode('utf-8')))
        except adbb.errors.IllegalAnimeObject as e:
            print("Skipping invalid item: '{}'".format(unknown_file.path.encode('utf-8')))
            pass
        except Exception as e:
            print("SKIP")


def command_version():
    """
    Print current version
    :return: int
    """
    print(joshu_version)


def command_help():
    """
    Print this help
    """
    print "scan <path>"
    print command_scan.__doc__
    print "rescan <path:optional>"
    print command_recognize_files.__doc__
    print "calc"
    print command_calc.__doc__
    print "reco"
    print command_recognize_anime.__doc__
    print "image"
    print command_image_scan.__doc__
    print "missing"
    print command_get_missing_data.__doc__
    print "title"
    print command_get_missing_titles.__doc__
    print "desc"
    print command_get_missing_anime_description.__doc__
    print "recalc-desc"
    print command_convert_anime_description.__doc__
    print "version"
    print command_version.__doc__
    print "help"
    print command_help.__doc__


def command_calc(force=False):
    """
    Go tru not recognized files and calculate they ed2khash for all that don't have it already or force for all
    :return:
    """
    if force:
        calc_list = _session.query(db.UnknownTable).all()
    else:
        calc_list = _session.query(db.UnknownTable).filter(db.UnknownTable.ed2khash.is_(None)).all()
    counter = 0
    counter_max = len(calc_list)
    for calc_file in calc_list:
        counter += 1
        log(str(counter) + '/' + str(counter_max) + ' rows')
        try:
            calc_file.ed2khash = unicode(adbb.fileinfo.get_file_hash(calc_file.path))
            calc_file.update()
            _session.commit()
        except Exception as e:
            print("SKIP")
            print(str(e))


def command_recognize_anime():
    """
    Scan tru all episodes to find out all aid (anime_id) and create missing rows in 'anime'
    :return:
    """
    query = _session.query(db.EpisodeTable).group_by(db.EpisodeTable.aid)
    subquery = _session.query(db.AnimeTable.aid)
    query = query.filter(~db.EpisodeTable.aid.in_(subquery))
    anime_list = query.all()

    counter = 0
    counter_max = len(anime_list)

    for anime_file in anime_list:
        counter += 1
        log(str(counter) + '/' + str(counter_max) + ' animes')
        _anime = adbb.Anime(int(anime_file.aid))
        _anime.update()
        _session.commit()


def command_image_scan():
    """
    Rebuild/Re-download image directory
    :return:
    """
    image_dir = config.get('images')
    anime_dir = os.path.join(image_dir + os.sep, "anime")
    if not os.path.exists(anime_dir):
        os.makedirs(anime_dir)
    # episode_dir = os.path.join(image_dir, "episode")
    anime_list = _session.query(db.AnimeTable).all()
    counter = 0
    counter_max = len(anime_list)
    for anime in anime_list:
        counter += 1
        log("{} / {} pics".format(str(counter), str(counter_max)))
        image_path = os.path.join(anime_dir, anime.picname)
        if os.path.exists(image_path):
            if os.stat(image_path).st_size == 0:
                adbb.log.debug("Removing empty file: '{}'".format(image_path))
                os.remove(image_path)
        if not os.path.exists(image_path):
            image_url = "https://img7.anidb.net/pics/anime/" + anime.picname
            adbb.log.debug("Downloading '{}' from '{}'".format(anime.picname, image_url))
            with open(image_path, 'wb') as handle:
                response = requests.get(image_url, stream=True)
                if not response.ok:
                    print response
                for block in response.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)


def command_get_missing_data():
    """
    Scan anime_relation and check if all anime are present in db
    :return:
    """
    query = _session.query(db.AnimeRelationTable).group_by(db.AnimeRelationTable.related_aid)
    sub_query = _session.query(db.AnimeTable.aid)
    query = query.filter(~db.AnimeRelationTable.related_aid.in_(sub_query))
    data_list = query.all()

    counter = 0
    counter_max = len(data_list)

    for anime_file in data_list:
        counter += 1
        log(str(counter) + '/' + str(counter_max) + ' animes')
        _anime = adbb.Anime(int(anime_file.related_aid))
        _anime.update()
        _session.commit()


def command_get_missing_titles():
    """
    Scan anime_title and check if all anime have title information
    :return:
    """
    query = _session.query(db.AnimeTitleTable).group_by(db.AnimeTitleTable.aid)
    sub_query = _session.query(db.AnimeTable.aid)
    query = query.filter(~db.AnimeTitleTable.aid.in_(sub_query))
    title_list = query.all()

    counter = 0
    counter_max = len(title_list)

    for anime_file in title_list:
        counter += 1
        log(str(counter) + '/' + str(counter_max) + ' titles')
        adbb.anames.get_titles(aid=anime_file.aid)


def command_get_missing_anime_description():
    """
    Scan anime_relation and check if all anime are present in db
    :return:
    """
    query = _session.query(db.AnimeTable)
    sub_query = _session.query(db.AnimeDescTable.aid)
    query = query.filter(~db.AnimeTable.aid.in_(sub_query))
    data_list = query.all()

    counter = 0
    counter_max = len(data_list)

    for anime_file in data_list:
        counter += 1
        log(str(counter) + '/' + str(counter_max) + ' animes')
        anime_desc = adbb.AnimeDesc(aid=int(anime_file.aid))
        anime_desc.update()
        # anime_desc = adbb.AnimeDesc(aid=int(anime_file.aid))
        if anime_desc.max_part:
            if int(anime_desc.max_part) > 1:
                adbb.log.debug("Found max_part > 1 for aid: '{}', sending request for more parts.".format(anime_desc.aid))
                x = 1
                c = 0
                while c == 0:
                    adbb.log.debug("Part: {}/{} - getting information for aid: '{}'".format(str(x), str(anime_desc.max_part), str(anime_desc.aid)))
                    next_desc = adbb.AnimeDesc(aid=int(anime_file.aid), part=x)
                    next_desc.update()
                    x += 1
                    if x >= int(anime_desc.max_part):
                        c = 1
            else:
                adbb.log.debug("Description have only 1 part, aid: '{}'".format(str(anime_desc.aid)))


def command_convert_anime_description():
    """
    Scan anime for missing description and try to generate it out of anime_description
    :return:
    """
    query = _session.query(db.AnimeTable).filter(db.AnimeTable.description.is_(None))
    sub_query = _session.query(db.AnimeDescTable.aid)
    query = query.filter(db.AnimeTable.aid.in_(sub_query))
    anime_list = query.all()

    for item in anime_list:
        anime = adbb.Anime(int(item.aid))
        _session.autoflush = False
        query2 = _session.query(db.AnimeDescTable).filter_by(aid=item.aid)
        title_list = query2.all()
        description = dict()
        text_description = ""
        for title in title_list:
            description[int(title.part)] = title.description.encode('utf-8')

        description_count = len(description)
        if description_count > 0:
            # this should be always true
            if description_count == int(title_list[0].max_part):
                # all parts there
                for num in range(description_count):
                    text_description += description[num]

        if text_description != "":
            q = _session.query(db.AnimeTable)
            q = q.filter(db.AnimeTable.aid == item.aid)
            anime_record = q.one()
            anime_record.description = unicode(text_description.decode('utf-8'))
            _session.commit()
            _session.flush()
            adbb.log.debug("Saved description for aid: '{}' in db".format(str(item.aid)))

    _session.autoflush = True

# endregion


if __name__ == '__main__':
    if (len(sys.argv)) < 2:
        print("No command found.")
    else:
        _force = False
        _path = ""
        for arg in sys.argv:
            if "-f" in arg:
                _force = True
                print("Force Mode: Enabled")
            if "path=" in arg:
                _path = arg[5:]  # strip down path=

        command = sys.argv[1]

        if command == "scan":
            path_to_scan = _path
            if path_to_scan != "":
                init()
                command_scan(path_to_scan)
            else:
                print("No path was given.")
        elif command == "rescan":
            init()
            if _path != "":
                command_recognize_files(path=_path, force=_force)
            else:
                command_recognize_files(force=_force)
        elif command == "calc":
            init()
            command_calc(force=_force)
        elif command == "reco":
            init()
            command_recognize_anime()
        elif command == "image":
            init()
            command_image_scan()
        elif command == "missing":
            init()
            command_get_missing_data()
        elif command == "title":
            init()
            command_get_missing_titles()
        elif command == "recalc-desc":
            init()
            command_convert_anime_description()
        elif command == "desc":
            init()
            command_get_missing_anime_description()
        elif command == "version":
            command_version()
        elif command == "help":
            command_help()
    sys.exit()

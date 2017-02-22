import adbb
import json
import logging
import os

config = json.load(open('./config.json'))

sql = "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4".format(config.get('db_user'), config.get('db_pass'), config.get('db_host'), config.get('db_port'), config.get('db_name'))

# custom logger
if os.name != 'posix':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    logger.setLevel(logging.DEBUG)
    lh = logging.StreamHandler()
    lh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(filename)s:%(lineno)d - %(message)s'))
    logger.addHandler(lh)

    lh = logging.handlers.SysLogHandler(address=('{}'.format(config.get('syslog_host')), 514))
    lh.setFormatter(logging.Formatter('joshu %(filename)s/%(funcName)s:%(lineno)d - %(message)s'))
    logger.addHandler(lh)

    # initialize backend
    adbb.init(config.get('user'), config.get('pass'), sql, debug=True, logger=logger)
else:
    adbb.init(config.get('user'), config.get('pass'), sql, debug=True)

anime = adbb.Anime(6187)

# this will print "Kemono no Souja Erin has 50 episodes and is a TV Series"
print("{} has {} episodes and is a {}".format(anime.title, anime.nr_of_episodes, anime.type))

# Episode object can be created either using anime+episode number or the anidb eid
# anime can be either aid, title or Anime object
#episode = adbb.Episode(eid=96461)

# this will print "'Kemono no Souja Erin' episode 5 has title 'Erin and the Egg Thieves'"
#print("'{}' episode {} has title '{}'".format(episode.anime.title, episode.episode_number, episode.title_eng))

# note that most of the time this will work even if we use a file that is not in the anidb database
# will print "'<path>' contains episode 5 of 'Kemono no Souja Erin'. Mylist state is 'on hdd'"
#print("'{}' contains episode {} of '{}'. Mylist state is '{}'".format(file.path, file.episode.episode_number, file.anime.title, file.mylist_state))
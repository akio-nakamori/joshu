#!/usr/bin/env python
# -*- coding: utf-8 -*-

import adbb
import json
import logging
import os
import sys


debug = True


def init():
    """
    Init all needed things to make joshu up and running
    :return:
    """
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

        lh = logging.handlers.SysLogHandler(address=(config.get('syslog_host'), 514))
        lh.setFormatter(logging.Formatter('joshu %(filename)s/%(funcName)s:%(lineno)d - %(message)s'))
        logger.addHandler(lh)

        # initialize backend
        adbb.init(config.get('user'), config.get('pass'), sql, debug=True, logger=logger)
    else:
        adbb.init(config.get('user'), config.get('pass'), sql, debug=True)


def command_scan(path):
    """
    Scan and add files from given path
    :param path: path to scan
    :return:
    """
    root = unicode(path)
    if os.path.exists(path):
        file_count = 0
        for dir_path, dir_names, file_names in os.walk(root):
            for file_name in file_names:
                file_count += 1
                log(str(file_count) + '/' + str(len(file_names)))
                _file = adbb.File(path=os.path.join(dir_path, file_name))
                print("'{}' contains episode {} of '{}'. Mylist state is '{}'".format(_file.path, _file.episode.episode_number, _file.anime.title, _file.mylist_state))
    else:
        print("Path not found.")


def log(message):
    """
    simple debug log function
    :param message: anything
    :return: print str of anything
    """
    if debug:
        print(message)


if __name__ == '__main__':
    if (len(sys.argv)) < 2:
        print("No command found.")
    else:
        if sys.argv[1] == "scan":
            path_to_scan = sys.argv[2]
            if path_to_scan != "":
                init()
                command_scan(path_to_scan)
            else:
                print("No path was given.")
    sys.exit()

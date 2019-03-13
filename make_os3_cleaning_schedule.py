#!/usr/bin/env python3

from argparse import ArgumentParser
import logging
from utils.logger import configure_logging
from os import getenv
from sys import argv

from os3website import OS3Website


def parse_args(args=None):
    parser = ArgumentParser(description='Make OS3 cleaning schedule - For clean coffee')

    parser.add_argument('-y', '--year', default='2018-2019', help='The current year of OS3 (default 2018-2019)')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug messages')

    return parser.parse_args(args)


def main(args=None):
    args = parse_args(args)
    logger = configure_logging(argv[0], logging.DEBUG if args.debug else logging.INFO)

    logger.debug('Validating environment')
    password = getenv('OS3_HTTP_PASS')
    if not password:
        logger.critical('OS3_HTTP_PASS variable not set')
        exit(1)
    username = getenv('OS3_HTTP_USERNAME')
    if not username:
        logger.critical('OS3_HTTP_USERNAME variable not set')
        exit(1)

    logger.info('Getting list of students')
    std = OS3Website(username, password, args.year)
    students = std.get_all_students()
    if args.debug:
        logger.debug('Found {} students:'.format(len(students)))
        print(students)


if __name__ == '__main__':
    main()

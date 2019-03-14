#!/usr/bin/env python3

from argparse import ArgumentParser
import logging
from utils.logger import configure_logging
from os import getenv
from os.path import isfile
from sys import argv

from os3website import OS3Website

MAX_WEBSITE_RETRIES = 3
CLEANING_TASK_LIST_URL = 'https://www.os3.nl/2018-2019/students/playground/cleaning'


def parse_args(args=None):
    parser = ArgumentParser(description='Make OS3 cleaning schedule - For clean coffee')

    parser.add_argument('-y', '--year', default='2018-2019', help='The current year of OS3 (default 2018-2019)')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug messages')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-e', '--excluded-students', nargs='*', help='List of student to exclude (separated by spaces)')
    group.add_argument('-f', '--excluded-students-file', help='A file of students to exclude (seprated by newlines)')

    return parser.parse_args(args)


def main(args=None):
    args = parse_args(args)
    logger = configure_logging(argv[0], logging.DEBUG if args.debug else logging.INFO)

    # Check if HTTP auth creds are present
    logger.debug('Validating environment')
    password = getenv('OS3_HTTP_PASS')
    if not password:
        logger.critical('OS3_HTTP_PASS variable not set')
        exit(1)
    username = getenv('OS3_HTTP_USERNAME')
    if not username:
        logger.critical('OS3_HTTP_USERNAME variable not set')
        exit(1)

    # Get a list of current students
    website = OS3Website(username, password, args.year)
    for i in range(0, MAX_WEBSITE_RETRIES):
        logger.info('Getting list of students')
        students = website.get_all_students()
        if students:
            if args.debug:
                logger.debug('Found {} students:'.format(len(students)))
                print(students)
            break
        else:
            logger.warning('Did not get any students from OS3 site')
            if i == MAX_WEBSITE_RETRIES:
                logger.critical('Max retries reached, giving up')
                exit(10)
            else:
                logger.info('Trying again, attempt {} of {}'.format(i+1, MAX_WEBSITE_RETRIES))


    # Remove students that operator asked to exclude
    if args.excluded_students_file:
        if isfile(args.excluded_students_file):
            logger.info('Excluding students from {}'.format(args.excluded_students_file))
            with open(args.excluded_students_file, 'r') as fh:
                students_to_exclude = fh.read().splitlines()
            logger.debug('Students to exclude: {}'.format(students_to_exclude))
        else:
            logger.error('{} is not a valid exclude file, ignoring...'.format(args.excluded_students_file))
            students_to_exclude = []
    elif args.excluded_students:
        students_to_exclude = args.excluded_students
        logger.info('Students to exclude: {}'.format(students_to_exclude))
    else:
        logger.debug('No students to exclude')
        students_to_exclude = []
    for student in students_to_exclude:
        if student in students:
            students.remove(student)
        else:
            logger.warning(
                'Tried to remove {} from student list, but person was not present in student list'.format(student)
            )

    # TODO Remove debug print
    print(students)

    # Get de items of the cleaning page
    logger.info('Getting list of cleaning tasks')
    for i in range(0, MAX_WEBSITE_RETRIES):
        cleaning_tasks = website.get_elements_from_webpage(CLEANING_TASK_LIST_URL, "li", **{"class": "level1"})
        if cleaning_tasks:
            if args.debug:
                logger.debug('Found the following cleaning tasks: {}'.format(cleaning_tasks))
            break
        else:
            logger.warning('Did not receive a list of cleaning tasks from OS3 site')
            if i == MAX_WEBSITE_RETRIES:
                logger.critical('Max retries reached, giving up')
                exit(11)
            else:
                logger.info('Trying again: attempt {} of {}'.format(i+1, MAX_WEBSITE_RETRIES))



if __name__ == '__main__':
    main()

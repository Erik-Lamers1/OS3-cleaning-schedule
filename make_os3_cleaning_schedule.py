#!/usr/bin/env python3

from argparse import ArgumentParser
import logging
from os import getenv
from os.path import isfile
from sys import argv

from os3website import OS3Website
from utils.logger import configure_logging
from utils.filesystem import get_lines_from_file, write_lines_to_file

MAX_WEBSITE_RETRIES = 3
CLEANING_TASK_LIST_URL = 'https://www.os3.nl/2018-2019/students/playground/cleaning'
logger = configure_logging(__name__)


def parse_args(args=None):
    parser = ArgumentParser(description='Make OS3 cleaning schedule - For clean coffee. '
                                        'Takes a list of students from a file or the OS3 website. '
                                        'And randomly picks students for cleaning tasks gathered from the OS3 site')

    parser.add_argument('students_file', help='A file with student names to pick from, '
                                              'if empty a new list will be generated '
                                              'and written to this location')
    parser.add_argument('-y', '--year', default='2018-2019', help='The current year of OS3 (default 2018-2019)')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug messages')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-e', '--excluded-students', nargs='*', help='List of student to exclude (separated by spaces)')
    group.add_argument('-f', '--excluded-students-file', help='A file of students to exclude (separated by newlines)')

    return parser.parse_args(args)


def get_student_list_from_website(website, debug=False):
    for i in range(0, MAX_WEBSITE_RETRIES):
        logger.info('Trying to get list of student from os3.nl')
        students = website.get_all_students()
        if students:
            break
        else:
            logger.warning('Did not get any students from OS3 site')
            if i == MAX_WEBSITE_RETRIES:
                logger.critical('Max retries reached, giving up')
                break
            else:
                logger.info('Trying again, attempt {} of {}'.format(i + 1, MAX_WEBSITE_RETRIES))
    return students


def main(args=None):
    args = parse_args(args)
    logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

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
    website.set_log_level(logger.level)
    students = []

    # Check if we can get a list of student from file
    if isfile(args.students_file):
        logger.info('Found {}, retrieving student list'.format(args.students_file))
        students = get_lines_from_file(args.students_file)
        create_student_file = True if len(students) == 0 else False
    else:
        create_student_file = True

    # Getting list of student from file not successful, scrape the OS3 site instead
    if not isfile(args.students_file) or len(students) == 0:
        logger.info(
            'Student file {} is empty or non existent, getting list of student from os3.nl'.format(args.students_file)
        )
        students = get_student_list_from_website(website, args.debug)
    if args.debug:
        logger.debug('Found the following student list: {}'.format(students))
    if not students:
        logger.critical('Could not find any students!!!')
        exit(10)

    # Remove students that operator asked to exclude
    if args.excluded_students_file:
        if isfile(args.excluded_students_file):
            logger.info('Excluding students from {}'.format(args.excluded_students_file))
            students_to_exclude = get_lines_from_file(args.excluded_students_file)
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

    # Students_file should be created
    if create_student_file:
        logger.info('Writing list of students to {}'.format(args.students_file))
        try:
            write_lines_to_file(args.students_file, students)
        except IOError as e:
            logger.error('Could not write students to {}, got error: {}'.format(args.students_file, e))

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
                logger.info('Trying again: attempt {} of {}'.format(i + 1, MAX_WEBSITE_RETRIES))


if __name__ == '__main__':
    main()

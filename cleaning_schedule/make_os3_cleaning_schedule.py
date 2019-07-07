#!/usr/bin/env python3

from argparse import ArgumentParser
import logging
from os import getenv
from os.path import isfile
from random import sample
from datetime import datetime

from cleaning_schedule.os3website import OS3Website
from cleaning_schedule.mail import Mail
from cleaning_schedule.utils.development import print_html5
from cleaning_schedule.utils.logger import configure_logging
from cleaning_schedule.utils.filesystem import get_lines_from_file, write_lines_to_file
from cleaning_schedule.settings.base import CLEANING_TASK_LIST_URL, MAX_WEBSITE_RETRIES

"""
This program tries to achieve randomized picking of students,
and assign them to the different cleaning tasks that should be preformed at OS3 each week.

Author: Erik Lamers
"""

logger = configure_logging(__name__)


def parse_args(args=None):
    parser = ArgumentParser(description='Make OS3 cleaning schedule - For clean coffee. '
                                        'Takes a list of students from a file or the OS3 website. '
                                        'And randomly picks students for cleaning tasks gathered from the OS3 site')

    parser.add_argument('students_file', help='A file with student names to pick from, '
                                              'if empty a new list will be generated '
                                              'and written to this location')
    parser.add_argument('-y', '--year', default='2018-2019', help='The current year of OS3 (default 2018-2019)')

    parser.add_argument('-c', '--cc', nargs='*', help='A list of CC address for the email (separated by spaces)')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug messages')
    parser.add_argument('-s', '--students', type=int, default=2, help='Amount of students to pick (default 2)')
    parser.add_argument('-u', '--user', default=getenv('OS3_USER'),
                        help='OS3 username (default $OS3_USER)')
    parser.add_argument('-p', '--password', default=getenv('OS3_PASS'),
                        help='OS3 password (default $OS3_PASS)')
    parser.add_argument('--keep-picked-students', action='store_true',
                        help='Do not remove student from student list after picking')

    student_args_group = parser.add_mutually_exclusive_group()
    student_args_group.add_argument('-x', '--excluded-students', nargs='*',
                                    help='List of student to exclude (separated by spaces)')
    student_args_group.add_argument('-f', '--excluded-students-file',
                                    help='A file of students to exclude (separated by newlines)')

    email_args_group = parser.add_mutually_exclusive_group(required=True)
    email_args_group.add_argument('-e', '--email', help='The email address to send the cleaning schedule to')
    email_args_group.add_argument('--no-email', action='store_true', help='Do not email (use for debugging)')

    args = parser.parse_args(args)
    # Check if HTTP auth creds are present
    if not args.user:
        parser.error('No user given and $OS3_HTTP_USER not set')
    elif not args.password:
        parser.error('No password given and $OS3_HTTP_PASS not set')

    # Check for valid emails
    mail = Mail()
    if not args.no_email and not \
            (mail.verify_email_addresses([args.email]) or (args.cc and not mail.verify_email_addresses(args.cc))):
        parser.error('Email addresses not valid!')

    if args.no_email and args.cc:
        logger.warning('CC email list given with no-email option enabled. Ignoring CC list.')

    return args


def get_student_list_from_website(website):
    """
    Curl the OS3 year info website to get a list of students.
    :param website: OS3 website class object
    :return: list: students
    """
    students = []
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


def get_cleaning_tasks_from_website(website):
    """
    Curl the OS3 CLEANING_TASK_LIST_URL to get a list of cleaning tasks.
    :param website: OS3 website class object
    :return: list: Cleaning tasks
    """
    cleaning_tasks = []
    for i in range(0, MAX_WEBSITE_RETRIES):
        logger.info('Getting list of cleaning tasks')
        cleaning_tasks = website.get_elements_from_webpage(CLEANING_TASK_LIST_URL, "li", **{"class": "level1"})
        if cleaning_tasks:
            break
        else:
            logger.warning('Did not receive a list of cleaning tasks from OS3 site')
            if i == MAX_WEBSITE_RETRIES:
                logger.critical('Max retries reached, giving up')
                break
            else:
                logger.info('Trying again: attempt {} of {}'.format(i + 1, MAX_WEBSITE_RETRIES))
    return cleaning_tasks


def main(args=None):
    students = []
    email_body = ''
    date = datetime.today().strftime('%d-%m-%Y')
    args = parse_args(args)
    logger.setLevel(logging.DEBUG if args.debug else logging.INFO)
    logger.debug('Argument validation successful')

    logger.info('Connecting to OS3 website')
    website = OS3Website(args.user, args.password, args.year)
    website.set_log_level(logging.DEBUG if args.debug else logging.INFO)

    # Check if we can get a list of student from file
    if isfile(args.students_file):
        logger.info('Found {}, retrieving student list'.format(args.students_file))
        students = get_lines_from_file(args.students_file)
        create_student_file = True if len(students) < args.students else False
    else:
        create_student_file = True

    # Getting list of student from file not successful, scrape the OS3 site instead
    if not isfile(args.students_file) or len(students) < args.students:
        logger.info(
            'Student file {} is empty or non existent, getting list of student from os3.nl'.format(args.students_file)
        )
        students = get_student_list_from_website(website)
    if not students:
        logger.critical('Could not find any students!')
        exit(10)
    if args.debug:
        logger.debug('Found the following student list: {}'.format(students))

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

    # Get de items of the cleaning page
    cleaning_tasks = get_cleaning_tasks_from_website(website)
    if not cleaning_tasks:
        logger.error('Could not find any cleaning tasks!')
        logger.warning('Assuming os3.nl playground page is broken, continuing with empty task list')
    if args.debug:
        logger.debug('Found the following cleaning tasks: {}'.format(', '.join(cleaning_tasks)))

    # Matching students to cleaning tasks
    logger.info('Picking {} students from list'.format(args.students))
    picked_students = sample(students, args.students)
    if args.debug:
        logger.debug('Picked the following students: {}'.format(', '.join(picked_students)))

    # Removing picked students from student list
    if not args.keep_picked_students:
        logger.info('Removing picked students from remaining student list')
        for student in picked_students:
            try:
                students.remove(student)
            except ValueError:
                logger.error('Trying to remove {} from student list failed!'.format(student))

    # Students_file should be created or updated
    if create_student_file or not args.keep_picked_students:
        logger.info('Writing list of (remaining) students to {}'.format(args.students_file))
        try:
            write_lines_to_file(args.students_file, students)
        except IOError as e:
            logger.error('Could not write students to {}, got error: {}'.format(args.students_file, e))

    logger.info('Rendering email template')
    mail = Mail()
    mail.set_log_level(logging.DEBUG if args.debug else logging.INFO)
    try:
        email_body = mail.render_template(**{
            'date': date,
            'cleaning_url': CLEANING_TASK_LIST_URL,
            'students': picked_students,
            'cleaning_tasks': cleaning_tasks,
            'list_rotated': create_student_file
        })
    except Exception as e:
        logger.critical('Unable to render email template, got error: {}'.format(e))
        exit(255)
    if args.debug or args.no_email:
        logger.debug('Printing rendered email')
        print_html5(email_body)

    if not args.no_email:
        logger.info('Sending email to {}'.format(args.email))
        message = mail.make_email(
            args.email,
            'OS3 cleaning schedule for the week of {}'.format(date),
            email_body.decode('utf-8'),
            args.cc
        )
        if website.send_email('cleaning-schedule@os3.nl', args.cc.append(args.email) if args.cc else [args.email],
                              message):
            logger.info('Email sent')
        else:
            # Mail sending failed
            logger.critical('Mail sending failed')
            exit(255)


if __name__ == '__main__':
    main()

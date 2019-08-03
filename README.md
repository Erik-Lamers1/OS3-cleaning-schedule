# OS3-cleaning-schedule
[![CircleCI](https://circleci.com/gh/Erik-Lamers1/OS3-cleaning-schedule.svg?style=svg)](https://circleci.com/gh/Erik-Lamers1/OS3-cleaning-schedule)

OS3 Cleaning schedule - For clean coffee  
This repo tries to achieve randomized picking of students,
and assign them to the different cleaning tasks that should be preformed at OS3 each week.  
An email is send to the specified email address with the results  

Python3 only project!

### Entrypoint

`cleaning-schedule/make_os3_cleaning_schedule.py --help`
```
usage: make_os3_cleaning_schedule.py [-h] [-y YEAR] [-d] [-s STUDENTS]
                                     [-u USER] [-p PASSWORD]
                                     [--keep-picked-students]
                                     [-x [EXCLUDED_STUDENTS [EXCLUDED_STUDENTS ...]]
                                     | -f EXCLUDED_STUDENTS_FILE]
                                     [-c [CC [CC ...]]]
                                     (-e EMAIL | --no-email)
                                     students_file

Make OS3 cleaning schedule - For clean coffee. Takes a list of students from a
file or the OS3 website. And randomly picks students for cleaning tasks
gathered from the OS3 site

positional arguments:
  students_file         A file with student names to pick from, if empty a new
                        list will be generated and written to this location

optional arguments:
  -h, --help            show this help message and exit
  -y YEAR, --year YEAR  The current year of OS3 (default 2018-2019)
  -d, --debug           Debug messages
  -s STUDENTS, --students STUDENTS
                        Amount of students to pick (default 2)
  -u USER, --user USER  OS3 username (default $OS3_USER)
  -p PASSWORD, --password PASSWORD
                        OS3 password (default $OS3_PASS)
  --keep-picked-students
                        Do not remove student from student list after picking

Exclusion actions:
  Students to exclude, append either to file or to a list when a student is
  no longer able to preform cleaning tasks

  -x [EXCLUDED_STUDENTS [EXCLUDED_STUDENTS ...]], --excluded-students [EXCLUDED_STUDENTS [EXCLUDED_STUDENTS ...]]
                        List of student to exclude (separated by spaces)
  -f EXCLUDED_STUDENTS_FILE, --excluded-students-file EXCLUDED_STUDENTS_FILE
                        A file of students to exclude (separated by newlines)

Email actions:
  Either choose to send no email or add a emails to send to (required)

  -c [CC [CC ...]], --cc [CC [CC ...]]
                        A list of CC address for the email (separated by
                        spaces)
  -e EMAIL, --email EMAIL
                        The email address to send the cleaning schedule to
  --no-email            Do not email (use for debugging)
```

### Running the tests

```angular2
pip3 install -r requirements/development.txt
tox
```

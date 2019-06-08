import setuptools

setuptools.setup(
    name='os3-cleaning-schedule-Erik-Lamers1',
    version='0.1.1',
    author='Erik Lamers',
    author_email='erik.lamers@os3.nl',
    description='OS3 cleaning schedule for clean coffee',
    url="https://github.com/Erik-Lamers1/OS3-cleaning-schedule",
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'requests',
        'beautifulsoup4',
        'jinja2',
    ]
)

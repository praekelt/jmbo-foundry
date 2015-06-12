import multiprocessing
from setuptools import setup, find_packages

setup(
    name='jmbo-foundry',
    version='2.0.0',
    description='Jmbo Foundry ties together the various Jmbo products enabling you to rapidly build multilingual web and mobi sites with the minimum amount of code and customization.',
    long_description=open('README.rst', 'r').read() + open('AUTHORS.rst', 'r').read() + open('CHANGELOG.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekelt.com',
    license='BSD',
    url='http://github.com/praekelt/jmbo-foundry',
    packages=find_packages(),
    dependency_links=[
    ],
    install_requires=[
        'django>=1.6,<1.7',

        'django_compressor',
        'django-dfp>=0.3.3',
        'django-export',
        'django-googlesearch',
        'django-layers-hr>=0.4',
        'django-object-tools>=0.0.5',
        'django-pagination',
        'django-publisher',             # legacy, required by migrations
        'django-simple-autocomplete>=0.5',
        'django-social-auth==0.7.18',   # 0.7.19 introduces a migration scoping bug
        'django-snippetscream',

        # These Jmbo apps are always part of Foundry
        'jmbo>=2.0.0',
        'jmbo-analytics',
        'jmbo-contact>=2.0.0',
        'jmbo-post>=2.0.0',

        # Python libraries
        'BeautifulSoup',
        'jellyfish',
        'python-memcached',
        'PyJWT',
        'requests',
        'zope.interface'
    ],
    include_package_data=True,
    tests_require=[
        # Foundry provides high-level testing tools for other content types
        'jmbo-banner>=0.6',
        'jmbo-calendar>=2.0.0',
        'jmbo-chart>=2.0.0',
        #'jmbo-competition',
        'jmbo-downloads>=2.0.0',
        #'jmbo-friends==2.0.0a1',   # add back when friends gets a stable release
        'jmbo-gallery>=2.0.0',
        'jmbo-music>=2.0.0',
        'jmbo-poll>=2.0.0',
        #'jmbo-sitemap>=0.1',
        #'jmbo-show>=0.2',
        #'jmbo-twitter',
        'django-setuptest>=0.1.6',
        'psycopg2',
    ],
    test_suite="setuptest.setuptest.SetupTestSuite",
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    zip_safe=False,
)

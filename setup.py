import multiprocessing
from setuptools import setup, find_packages

setup(
    name='jmbo-foundry',
    version='2.1.3',
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

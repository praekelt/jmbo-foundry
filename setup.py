import multiprocessing
from setuptools import setup, find_packages

setup(
    name='jmbo-foundry',
    version='1.3.1',
    description='Jmbo Foundry ties together the various Jmbo products enabling you to rapidly build multilingual web and mobi sites with the minimum amount of code and customization.',
    long_description = open('README.rst', 'r').read() + open('AUTHORS.rst', 'r').read() + open('CHANGELOG.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekelt.com',
    license='BSD',
    url='http://github.com/praekelt/jmbo-foundry',
    packages = find_packages(),
    dependency_links = [
    ],
    install_requires = [
        # todo: attempt to get rid of these five
        'django-section',
        'django-gizmo',
        'django-generate',
        'django-registration',
        'django-snippetscream',

        'django-googlesearch',
        'django-export',
        'django-simple-autocomplete',
        'django-pagination',
        'django-object-tools>=0.0.5',
        'django-debug-toolbar',
        'django_compressor',
        'django-social-auth==0.7.18',   # 0.7.19 introduces a migration scoping bug

        'jmbo>=1.2.0',
        'jmbo-gallery>=0.2.1',
        'jmbo-music',
        'jmbo-calendar',
        'jmbo-chart',
        'jmbo-post>=0.4',
        'jmbo-show>=0.2',
        'jmbo-banner>=0.2.2',
        'jmbo-competition',
        'jmbo-contact>=0.1.2',
        'jmbo-poll',
        'jmbo_analytics',
        'jmbo-friends',
	    'jmbo-downloads',
        'jmbo_twitter',
        'jmbo_sitemap>=0.1',

        'jellyfish',
        'BeautifulSoup',
        'PyJWT',
        'requests',
        'gunicorn',
        'python-memcached',
    ],
    include_package_data=True,
    tests_require=[
        'django-setuptest>=0.1.4',
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

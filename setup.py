from setuptools import setup, find_packages

setup(
    name='jmbo-foundry',
    version='1.1',
    description='Jmbo Foundry ties together the various Jmbo products enabling you to rapidly build multilingual web and mobi sites with the minimum amount of code and customization.',
    long_description = open('README.rst', 'r').read() + open('AUTHORS.rst', 'r').read() + open('CHANGELOG.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekelt.com',
    license='BSD',
    url='http://github.com/praekelt/jmbo-foundry',
    packages = find_packages(),
    install_requires = [
        # todo: eliminate dependencies handled by apps themselves
        'django-section',
        'jmbo-gallery>=0.2.1',
        'django-googlesearch',
        'jmbo-music',
        'django-export',
        'django-snippetscream',
        'django-generate',
        'jmbo-calendar',
        'jmbo>=1.0',
        'jmbo-chart',
        'django-recaptcha',
        'django-secretballot',
        'django-richcomments',
        'django-publisher',
        'django-category',
        'jmbo-post>=0.1.2',
        'django-likes',
        'django-gizmo',
        'django-object-tools>=0.0.5',
        'django-registration',
        'jmbo-show',
        'jmbo-event',
        'django-preferences',
        'jmbo-banner>=0.0.6',
        'jmbo-competition',
        'jmbo-contact',
        'jmbo-poll',
        'django-debug-toolbar',
        'django-simple-autocomplete',
        'django-pagination',
        'south',
        'BeautifulSoup',
        'django_compressor',
        'jmbo_analytics',
        'jmbo-friends',
        'gunicorn',
        'django-sites-groups',
        'jellyfish',
        'python-memcached',
	    'jmbo-downloads',
    ],
    include_package_data=True,
    tests_require=[
        'django-setuptest>=0.1.2',
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

import multiprocessing
from setuptools import setup, find_packages

setup(
    name='jmbo-foundry',
    version='1.2.6.1',
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

        # Django apps
        'django-googlesearch',
        'django-export',
        'django-simple-autocomplete',
        'django-pagination',
        'django-object-tools>=0.0.5',
        'django-debug-toolbar',
        'django_compressor',
        'django-social-auth==0.7.18',   # 0.7.19 introduces a migration scoping bug
        'django-dfp>=0.3.3',            # required because of import in base_inner.html

        # Jmbo apps
        'jmbo>=1.1',
        'jmbo-post>=0.1.2',
        'jmbo-contact>=0.1.2',
        'jmbo_analytics',
        'jmbo_sitemap>=0.1',

        # Optional praekelt-maintained Jmbo apps. Uncomment for development or
        # install with buildout or pip.
        #'jmbo-banner>=0.2.2',
        #'jmbo-calendar',
        #'jmbo-chart',
        #'jmbo-competition',
	    #'jmbo-downloads',
        #'jmbo-friends',
        #'jmbo-gallery>=0.2.1',
        #'jmbo-music',
        #'jmbo-poll',
        #'jmbo-show>=0.2',
        #'jmbo-twitter',

        # Python libraries
        'jellyfish',
        'BeautifulSoup',
        'PyJWT==0.1.6',
        'requests',
        'gunicorn',
        'python-memcached',
    ],
    include_package_data=True,
    tests_require=[
        'django-setuptest>=0.1.4',
        # Below does not work for buildout so automated testing is currently a
        # problem. You have to manually uncomment apps in the section above to
        # test them. When buuildout support is deprecated this will be fixed.
        #'jmbo-banner>=0.2.2',
        ##'jmbo-calendar',
        #'jmbo-chart',
        ##'jmbo-competition',
	    #'jmbo-downloads',
        #'jmbo-friends',
        #'jmbo-gallery>=0.2.1',
        #'jmbo-music',
        #'jmbo-poll',
        ##'jmbo-show>=0.2',
        #'jmbo-twitter',
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

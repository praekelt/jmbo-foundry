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
        # Setuptools weirdness requires this. Basically jmbo_analytics has
        # django<1.7 allowing 1.6.x to be installed, which is not supported.
        'django>=1.4,<1.5',

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

        'jmbo>=1.2.0,<1.99',
        'jmbo-gallery>=0.2.1,<1.99',
        'jmbo-music<1.99',
        'jmbo-calendar<1.99',
        'jmbo-chart<1.99',
        'jmbo-post>=0.4,<1.99',
        'jmbo-show>=0.2,<1.99',
        'jmbo-banner>=0.2.2,<1.99',
        'jmbo-competition<1.99',
        'jmbo-contact>=0.1.2,<1.99',
        'jmbo-poll<1.99',
        'jmbo_analytics',
        'jmbo-friends<1.99',
	    'jmbo-downloads<1.99',
        'jmbo_twitter<1.99',
        'jmbo_sitemap>=0.1,<1.99',

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

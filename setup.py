from setuptools import setup, find_packages

setup(
    name='jmbo-foundry',
    version='0.0.2',
    description='Jmbo foundry behaviour/templates app.',
    long_description = open('README.rst', 'r').read() + open('AUTHORS.rst', 'r').read() + open('CHANGELOG.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekelt.com',
    license='BSD',
    url='http://github.com/praekelt/jmbo-foundry',
    packages = find_packages(),
    install_requires = [
        # todo: eliminate dependencies handled by apps themselves
        'django-section',
        'jmbo-gallery',
        'django-googlesearch',
        'jmbo-music',
        'django-export',
#        'jmbo-foundry',
        'django-snippetscream',
        'django-generate',
        'jmbo-calendar',
        'jmbo',
        'jmbo-chart',
        'django-recaptcha',
        'django-secretballot',
        'django-richcomments',
        'django-publisher',
#        'jmbo-social',	# xxx: can't download tarball currently
        'django-category',
        'jmbo-post',
        'django-likes',
        'django-gizmo',
        'django-object-tools',
        'django-registration',
        'jmbo-show',
        'jmbo-event',
        'django-preferences',
        'jmbo-banner',
        'jmbo-competition',
        'django-ckeditor',
        'jmbo-contact',
        'jmbo-poll',
        'django-debug-toolbar',
        'django-simple-autocomplete',
        'django-pagination',
        'south',
        'BeautifulSoup',
    ],
    include_package_data=True,
    tests_require=[
        'django-setuptest',
    ],
    test_suite="setuptest.SetupTestSuite",
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

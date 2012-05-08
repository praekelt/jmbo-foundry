from setuptools import setup, find_packages

setup(
    name='foundrydemo',
    version='0.0.1',
    description='Demo based on the Jmbo platform.',
    long_description = open('README.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekelt.com',
    license='BSD',
    url='',
    packages = find_packages(),
    dependency_links = [
        'http://github.com/praekelt/jmbo-foundry/tarball/master#egg=jmbo-foundry',
    ],
    install_requires = [
        'jmbo-foundry',
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

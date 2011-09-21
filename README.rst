Jmbo Generic
============

Jmbo generic behaviour/templates app.

.. contents:: Contents
    :depth: 5

Installation
------------

#. Install or add ``jmbo-generic`` to your Python path.

#. Add ``generic`` to your ``INSTALLED_APPS`` setting.

#. Add ``generic`` url include to your project's ``urls.py`` file::

    (r'^$', include('generic.urls')),

#. ``jmbo-generic`` includes a number of template sets allowing you to deliver lightweight(``zero``), mobile(``basic``) or desktop/touch(``full``) specific output. Determing which template set to use is simply a matter of specifying a ``TEMPLATE_TYPE`` setting, and adding  ``generic.loaders.TypeLoader`` to the ``TEMPLATE_LOADERS`` setting. For example to use the ``basic`` template set update your settings as follows::
    
    TEMPLATE_TYPE = "basic"

    TEMPLATE_LOADERS = (
        ...other template loader classes...
        'generic.loaders.TypeLoader',
    )

#. ``jmbo-generic`` includes static media resources which you need to configure as described in `Django`s managing static files doc <https://docs.djangoproject.com/en/dev/howto/static-files/>`_.

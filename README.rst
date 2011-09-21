Jmbo Generic
============

Jmbo generic behaviour/templates app.

.. contents:: Contents
    :depth: 5

Installation
------------

#. Install or add ``jmbo-generic`` to your Python path.

#. Install ``django-preferences`` as described `here <http://pypi.python.org/pypi/django-preferences#installation>`_.

#. Add ``generic`` to your ``INSTALLED_APPS`` setting.

#. Add ``generic`` url include to your project's ``urls.py`` file::

    (r'^$', include('generic.urls')),

#. ``jmbo-generic`` includes a number of template sets allowing you to deliver lightweight(``zero``), mobile(``basic``) or desktop/touch(``full``) specific output. Determing which template set to use is simply a matter of specifying a ``TEMPLATE_TYPE`` setting, and adding  ``generic.loaders.TypeLoader`` to the ``TEMPLATE_LOADERS`` setting. For example to use the ``basic`` template set update your settings as follows::
    
    TEMPLATE_TYPE = "basic"

    TEMPLATE_LOADERS = (
        ...other template loader classes...
        'generic.loaders.TypeLoader',
    )

#. ``jmbo-generic`` includes static media resources which you need to configure as described in `Django`s managing static files documentation <https://docs.djangoproject.com/en/dev/howto/static-files/>`_.

Models
------

.. _generic.models.Link:

generic.models.Link
*******************

Fields
~~~~~~
        
.. _generic.models.Link.title:
    
title
+++++
A short descriptive title for link.

.. _generic.models.Link.view_name:
    
view_name
+++++++++
View name to which this link will redirect. This takes precedence over :ref:`generic.models.Link.url` field.
    

.. _generic.models.Link.url:
    
url
+++
URL to which this menu link will redriect. Only used if :ref:`generic.models.Link.view_name` is not specified.

.. _generic.models.Link.methods:

Methods & Properties
~~~~~~~~~~~~~~~~~~~~

.. _generic.models.Link.get_absolute_url:
    
get_absolute_url(self)
++++++++++++++++++++++
Returns url to which link should redirect based on a reversed view name as specified in :ref:`generic.models.Link.view_name` or otherwise an explicitly provided url as specified in :ref:`generic.models.Link.url`.

.. _generic.models.Link.is_active:

is_active(self, request)
++++++++++++++++++++++++
Determines whether or not the link can be consider active based on the request path. True if the request path can be resolved to the same view name as is contained in :ref:`generic.models.Link.view_name`. Otherwise True if request path starts with url as contained in :ref:`generic.models.Link.url` field.

.. _generic.models.LinkPosition:

generic.models.LinkPosition
***************************

.. _generic.models.LinkPosition.Fields:

Fields
~~~~~~

.. _generic.models.LinkPosition.position:
    
position
++++++++
Used to determine in which position/order elements should render in :ref:`generic_inclusion_tags.menu` and :ref:`generic_inclusion_tags.navbar` inclusion tags.

.. _generic_inclusion_tags:

Inclusion Tags
--------------

generic.templatetags.generic_inclusion_tags
*******************************************

Generic inclusion tags delivering various functionality like :ref:`generic_inclusion_tags.menu` and :ref:`generic_inclusion_tags.navbar`. Load these tags by including ``{% load generic_inclusion_tags %}`` in your templates.

.. _generic_inclusion_tags.menu:

{% menu %}
~~~~~~~~~~

.. _generic_inclusion_tags.navbar:

{% navbar %}
~~~~~~~~~~~~

Renders a navigation bar normally used as part of main navigation element positioned at top of pages. Utilizes :ref:`generic.models.Link` objects configurable via `Navbar Preferences in admin <http://localhost:8000/admin/preferences/navbarpreferences>`_ to provide a flexible navbar system. Elements are ordered using :ref:`generic.models.LinkPosition.position` values as specified via admin. You can customize the resulting HTML by overriding the ``generic/inclusion_tags/navbar.html`` file. The template recieves  ``object_list`` and ``active_link`` context variables. ``object_list`` is a collection of :ref:`generic.models.Link` elements to display and ``active_link`` is an :ref:`generic.models.Link` determined to be active for the requested path.

Jmbo Generic
============

Jmbo generic behavior/templates app.

.. contents:: Contents
    :depth: 5

Installation
------------

#. Install or add ``jmbo-generic`` to your Python path.

#. Install ``django-preferences`` as described `here <http://pypi.python.org/pypi/django-preferences#installation>`_.

#. Add ``generic`` to your ``INSTALLED_APPS`` setting.

#. Add ``generic`` URL include to your project's ``urls.py`` file::

    (r'^', include('generic.urls')),

#. ``jmbo-generic`` includes a number of template sets allowing you to deliver lightweight(``zero``), mobile(``basic``) or desktop/touch(``full``) specific output. Specifying which template set to use is simply a matter of specifying a ``TEMPLATE_TYPE`` setting, and adding  ``generic.loaders.TypeLoader`` to the ``TEMPLATE_LOADERS`` setting. For example to use the ``basic`` template set update your settings as follows::
    
    TEMPLATE_TYPE = "basic"

    TEMPLATE_LOADERS = (
        'generic.loaders.TypeLoader',
        ...other template loader classes...
    )

   This causes templates to be loaded from a path prefixed with whatever value was specified as the ``TEMPLATE_TYPE`` setting. For example in this case a template specified as ``generic/home.html`` would actually be loaded from ``basic/generic/home.html``.

   .. note:: 
   
        You have to add ``TypeLoader`` as the first loader for it to resolve templates correctly.

#. ``jmbo-generic`` includes static media resources which you need to configure as described in `Django`s managing static files documentation <https://docs.djangoproject.com/en/dev/howto/static-files/>`_.

Models
------

.. _generic.models.Link:

generic.models.Link
*******************

Used in conjunction with `{% menu %}`_ and `{% navbar %}`_ to provide an admin configurable navbar and menu.

Fields
~~~~~~
        
.. _generic.models.Link.title:
    
title
+++++
A short descriptive title for link.

.. _generic.models.Link.view_name:
    
view_name
+++++++++
View name to which this link will redirect. This takes precedence over `category`_ and `url`_ fields.
    
    
.. _generic.models.Link.category:
    
category
++++++++
Category to which this link will redirect. This takes precedence over `url`_ field.

.. _generic.models.Link.url:
    
url
+++
URL to which this menu link will redirect. Only used if `view_name`_ is not specified.

.. _generic.models.Link.methods:

Methods & Properties
~~~~~~~~~~~~~~~~~~~~

.. _generic.models.Link.get_absolute_url:
    
get_absolute_url(self)
++++++++++++++++++++++
Returns URL to which link should redirect based on a `reversed <https://docs.djangoproject.com/en/dev/topics/http/urls/#reverse>`_ view name as specified in `view_name`_ field or category view for category specified in `category`_ field or otherwise an explicitly provided URL as specified in `url`_ field.

.. _generic.models.Link.is_active:

is_active(self, request)
++++++++++++++++++++++++
Determines whether or not the link can be consider active based on the request path. ``True`` if the request path can be resolved to the same view name as is contained in `view_name`_ field. Otherwise ``True`` if request path starts with URL as resolved for category contained in `category`_ field. Otherwise ``True`` if request path starts with URL as contained in `url`_ field.

.. _generic.models.LinkPosition:

generic.models.LinkPosition
***************************

Used to determine position/order of elements in `{% menu %}`_ and `{% navbar %}`_ inclusion tags.

.. _generic.models.LinkPosition.Fields:

Fields
~~~~~~

.. _generic.models.LinkPosition.position:
    
position
++++++++
Specifies position/order of link in `{% menu %}`_ and `{% navbar %}`_ inclusion tags.

.. _generic_inclusion_tags:

Inclusion Tags
--------------

generic.templatetags.generic_inclusion_tags
*******************************************

Provides generic inclusion tags like `{% menu %}`_ and `{% navbar %}`_. Load these tags by including ``{% load generic_inclusion_tags %}`` in your templates.

.. _generic_inclusion_tags.menu:

{% menu %}
~~~~~~~~~~

Renders a navigation menu normally used as part of footer navigation element. Utilizes `generic.models.Link`_ objects configurable via `Menu Preferences in admin <http://localhost:8000/admin/preferences/menupreferences>`_ to provide a flexible menu navigation system. Elements are ordered using `position`_ values as specified on `generic.models.LinkPosition`_ objects via admin. You can customize the resulting HTML by overriding the ``generic/inclusion_tags/menu.html`` template file. The template receives  an ``object_list`` context variable, which is a collection of ordered `generic.models.Link`_ elements to display.

.. _generic_inclusion_tags.navbar:

{% navbar %}
~~~~~~~~~~~~

Renders a navigation bar normally used as part of main navigation element positioned at top of pages. Utilizes `generic.models.Link`_ objects configurable via `Navbar Preferences in admin <http://localhost:8000/admin/preferences/navbarpreferences>`_ to provide a flexible navbar system. Elements are ordered using `position`_ values as specified on `generic.models.LinkPosition`_ objects via admin. You can customize the resulting HTML by overriding the ``generic/inclusion_tags/navbar.html`` template file. The template receives  ``object_list`` and ``active_link`` context variables. ``object_list`` is a collection of ordered `generic.models.Link`_ elements to display and ``active_link`` is an `generic.models.Link`_ object determined to be active for the requested path.


Jmbo Foundry
============
**Jmbo Foundry ties together the various Jmbo products enabling you to rapidly build multilingual web and mobi sites with the minimum amount of code and customization.**

.. figure:: https://travis-ci.org/praekelt/jmbo-foundry.svg?branch=develop
   :align: center
   :alt: Travis

.. contents:: Contents
    :depth: 5

Overview
--------

`jmbo-foundry` ties together the various Jmbo products enabling you to rapidly build
multilingual web and mobi sites with the minimum amount of code and customization.

`jmbo-foundry` strives for a high level of through the web configuration. Much
of the site's behaviour is configurable through the admin interface.

Installation
------------

Use `jmbo-skeleton <http://pypi.python.org/pypi/jmbo-skeleton>`_ to set up a
Jmbo environment. It is not recommended to install `jmbo-foundry` by itself.

Supported Jmbo products
-----------------------

`jmbo-foundry` pulls in these Jmbo products.

+-----------------------------------------------------------------------+-------+-------+-----+------------+
| Product                                                               | Basic | Smart | Web | Translated |
+=======================================================================+=======+=======+=====+============+
|`jmbo <http://pypi.python.org/pypi/jmbo>`_                             |       |       |     | 100%       |
+-----------------------------------------------------------------------+-------+-------+-----+------------+
|`jmbo-banner <http://pypi.python.org/pypi/jmbo-banner>`_               | x     |       |     | N/A        |
+-----------------------------------------------------------------------+-------+-------+-----+------------+
|`jmbo-calendar <http://pypi.python.org/pypi/jmbo-calendar>`_           | x     |       |     | 0%         |
+-----------------------------------------------------------------------+-------+-------+-----+------------+
|`jmbo-competition <http://pypi.python.org/pypi/jmbo-competition>`_     | x     | x     |     | 0%         |
+-----------------------------------------------------------------------+-------+-------+-----+------------+
|`jmbo-downloads <http://pypi.python.org/pypi/jmbo-downloads>`_         | x     |       |     | 0%         |
+-----------------------------------------------------------------------+-------+-------+-----+------------+
|`jmbo-gallery <http://pypi.python.org/pypi/jmbo-gallery>`_             | x     | x     | x   | 100%       |
+-----------------------------------------------------------------------+-------+-------+-----+------------+
|`jmbo-poll <http://pypi.python.org/pypi/jmbo-poll>`_                   | x     |       |     | 100%       |
+-----------------------------------------------------------------------+-------+-------+-----+------------+
|`jmbo-post <http://pypi.python.org/pypi/jmbo-post>`_                   | x     |       |     | 100%       |
+-----------------------------------------------------------------------+-------+-------+-----+------------+

Sites
-----

Your web presence typically consists of a normal web site and a mobile site.
There may be many more types of sites in future and `jmbo-foundry` makes it
easy to configure them independently. If your main site is served on
`www.mysite.com` then go to `Sites` in the admin interface and set `Domain
name` and `Display name` accordingly. Then add a site entry for your mobile
site and set the values to `m.mysite.com`.

If you have only one site then you may blindly publish everything that is
publishable to this site.  However, if you have more than one site and in
different languages then understanding sites become significant.

At its most basic level publishing to a site means making content appear on a
site. This is easy to understand when the content is eg. an article, but
content is not always limited to things which are easily translatable into real
world objects.

Preferences
-----------

Preferences can be published to certain sites.

General preferences
*******************

Check `Private site` to make the site accessible only to visitors who are
logged in.

Check `Show age gateway` to enable the age gateway for the site. Visitors must
confirm their age before they are allowed to browse the site.

`Exempted URLs` are URLs which must always be visible regardless of `Private
site` or `Age gateway` settings. Certain URLs like `/login` are visible by
default and do not need to be listed.

The `Analytics tags` field may contain javascript. There is a fallback to
enable analytics on low-end browsers but it is not configurable through the
web. See the `settings.py` section.

Registration preferences
************************

You can select which fields to display on the registration form. Some fields
(eg. `username`) are always visible on the registration form and cannot be
removed.

You can select a subset of the displayed fields to be required. Fields which
are absolutely required (eg. `username`) cannot be set to be optional. For
instance, if the site users my log in using their mobile number then set
`mobile_number` as a required field.

Some fields may need to be unique, especially those that may be used to log in
to the site. Using the mobile number example above you should set
`mobile_number` to be a unique field. It is important to decide beforehand
which fields must be unique since it is difficult to remove duplicates if you
change this setting. An exeption is raised if you attempt to change this
setting and duplicates are detected (friendlier validation still to be added).

Login preferences
*****************

Users typically log in to a normal site with their username or email address,
whereas a mobile number is a natural login field for a mobile site. Choose from
`Username only`, `Email address only`, `Mobile number only` or `Username or
email address`.

Password reset preferences
**************************

When a user loses his password he may request a password reset. Normally this
is accomplished by sending an email to the user, but in the case of a mobile
site it is desirable to send a text. Choose between `Email address` or `Mobile
number`. Note that a password reset request does not automatically generate a
new password for the user since this may lead to malicious people disabling
users' accounts.

Naughty word preferences
************************

You can set a list of weighted words. The `report_naughty_words` management
command identifies potentially offensive comments. An email containing
clickable links for approval or deletion is sent to the `Email recipients`.

Listings
--------
A `listing` is essentially a stored search that can be rendered in a certain
style. A listing can be published to certain sites.

`Content type`, `Category` and `Content` are criteria which define the items
present in the listing. These criteria are mutually exclusive.

`Count` specifies the maximum number of items in the listing.

`Style` is the default way in which the listing is rendered. The styles are
vertical, vertical, vertical thumbnail, horizontal, promo and widget. See
`Listing styles` for detail.

`Items per page` is the number of items to display on a single listing page.

Listing styles
**************

`Vertical` is a vertical listing with no images.

`Vertical thumbnail` is a vertical listing with images.

`Horizontal` is a side-by-side listing with images. Each item looks like a
baseball trading card.

`Promo` collates the items in a slideshow.

`Widget` is the most complex. It is used when each item can be interactive, eg.
a listing of polls. Polls you have already voted on are read-only, and the
others may change content once you vote on them. The content type being
represented as a widget needs to provide code for this functionality.

Links
-----

A `link` is a re-usable pointer to something, be it inside the site or external.

`URL`, `Category`, `View name` and `Target` fields are mutually exclusive.

`View name` warrants further explanation. It is the name of a named Django
view, eg. `contact-us`.  The vocabulary is all the named views in the Django
site excluding those with a variable parameter.

Navbars
-------

A navigation bar typically contains a small amount of items since horizontal
space is limited.  Each item in the navigation bar is represented as a `Link`.
A navbar can be published to certain sites.

A navbar with slug `main` is considered special. It is assumed to be the site
navbar by default.

Menus
-----

A menu is essentially the same as a navigation bar, except it has a vertical
layout by default.

A menu with slug `main` is considered special. It is assumed to be the site
menu by default.

Pages
-----

Page builder documentation tbc.

How to use dumpdata
-------------------

To move your `jmbo-foundry` site between databases you will have to use `dumpdata --natural`.
This will emit natural keys for all relations to external models. Internal
relations use primary keys. To safely migrate `jmbo-foundry` models, use the following:

    migrate.py dumpdata --natural --all foundry preferences --exclude=foundry.Member --exclude=foundry.Notification --exclude=foundry.BlogPost --exclude=foundry.ChatRoom --exclude=foundry.FoundryComment

The excluded models subclass external models. You will need to manually dump them
along with their parent models.

Layers
------

A layer is a rendering target. `jmbo-foundry` defines four type of layers:
basic, smart and web. Templates, styling, javascript, images and even code
can all be different per payer. This enables optimal support for different
devices from the same codebase.

Layers are arranged in this hierarchy.

  basic - smart
  basic - web

If eg. the template my_page.html is not found in the web layer then it falls
back to my_page.html from the basic layer. The basic layer must be complete.


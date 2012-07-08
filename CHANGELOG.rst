Changelog
=========

0.4
---
#. `layered` decorator so you can write different views for different layers without cluttering urls.py.

0.3.10
------
#. Translation for search form.
#. Member profile editing regression fixed.

0.3.9
-----
#. Searching now working.

0.3.8
-----
#. Bug fix for regression introduced into 0.3.7.

0.3.7
-----
#. Listings being used within a tile can now choose whether to display a title.
#. Columns now have an optional title.

0.3.6
-----
#. Demo is now part og jmbo-skeleton.
#. Minimum jmbo version required is now >= 0.3.4.
#. Management command load_photosizes loads photosizes in a sane way.

0.3.5
-----
#. Adjust South migration dependencies.
#. Simplify and extend demo.

0.3.4
-----
#. Batching on tastypie listing API.
#. Remove django-ckeditor dependency. Handled by jmbo-post.
#. Patch CsrfTokenNode.render so the input is not wrapped in a hidden container.

0.3.3
-----
#. Version pins for jmbo and jmbo-post.

0.3.2
-----
#. Use slug for lookups in tastypie API.

0.3.1
-----
#. Chatrooms and normal comments can now have distinct appearances. jmbo>=0.3.1 required.

0.3
----
#. Reduce ajax polling when user is inactive
#. django-tastypie support added. jmbo and jmbo-post have minimum version requirements.

0.2.2
-----
#. Pin django-ckeditor to >= 3.6.2
#. Remember me field now on login and join forms. Checked by default.
#. Any call to get_XXX_url is now layer aware.
#. Comment posting now ajaxified depending on browser capabilities.

0.2.1
-----
#. Remove dependency links.

0.2
---
#. Add a base_inner.html template so it is easier to override base.html.
#. Patch listdir so collectstatic does not fail on custom layers for third party foundry-based products.

0.1
---
#. Use Jaro Winkler for matching naughty words.

0.0.2 (2011-09-27)
------------------
#. Detail view.
#. Element preferences.

0.0.1 (2011-09-21)
------------------
#. Initial release.


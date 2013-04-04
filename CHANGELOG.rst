Changelog
=========

1.1.16.1
--------
#. Hotfix. foundrycache template tag was using wrong class to compute key.

1.1.16
------
#. Ensure that `user_logged_in` signal is dispatched when a user joins.
#. Don't allow the creation of a `BlogPost` where the `content` field contains scripting.
#. Map as many fields as possible to member when doing Facebook Connect.
#. Twitter Oauth is now standard functionality.
#. `base_inner.html` provides now has an extratitle block.
#. A comment posted to eg. basic will now show up in the other layers comprising the same logical site.
#. Flatpages are now part of our standard set of products.
#. Through-the-web configurable caching for rows, columns, tiles, menus and navbars.
#. Identify poorly performing areas and optimize code.

1.1.15
------
#. The Open Graph site description can now be set under General Preferences.
#. Allow dot in username.

1.1.14
------
#. Exclude gallery images from search results.
#. Include URLs from `jmbo-gallery`.

1.1.13
------
#. Use `django-banner>=0.2.2`. DFP banners loaded by ajax will now work.

1.1.12
------
#. Fire `onListingRefresh` event when listing is updated via ajax. Extra `target` parameter is passed to handler.
#. Basic ajax comment loading until jQuery-replacement is added.
#. Add name attribute to logo anchor so it is possible to jump to top of page.
#. Ajaxify view modifier navigation on listings.
#. Use `django-dfp>=0.2` which works across all browsers.

1.1.11
------
#. Add an index on Member.last_seen - useful for fast online user queries.

1.1.10
------
#. The `jmbo-banner` migration dependency was not in the correct migration step. Fixed.

1.1.9
-----
#. Initial migration now depends on `jmbo-banner` migrations.

1.1.8
-----
#. Restore version of `jmbo-banner` to 0.2.

1.1.7
-----
#. Hotfix release. Use safe method to get HTTP_USER_AGENT in middlewares since it might not be present.
#. Deprecated. Use 1.1.8.

1.1.6
-----
#. Hotfix release. An url import went missing.
#. Deprecated. Use 1.1.8.

1.1.5
-----
#. Newer version of `jmbo-banner` implies a DFP header to be added to the base template.
#. Deprecated. Use 1.1.8.

1.1.4
-----
#. Add optional CSS classes to page rows and columns.
#. Add last_seen field to Member and a middleware to update this timestamp at most every 5 minutes.

1.1.3
-----
#. Use `django-social-auth` to authenticate against external providers. You must add `social_auth` to `INSTALLED_APPS` and set `SOCIAL_AUTH_USER_MODEL = 'foundry.Member'` at the very least. See the django-social auth documentation for more settings.
#. Drop the wizard style of registration. This is required for consistent UX when registering via Facebook.
#. Listings no longer include unpublished items that are referenced by the Content or Pinned fields.

1.1.2
-----
#. Fix migration 0045 which would case South to complain about a previous set not being frozen.
#. Page objects can now be styled with extra CSS. This is useful when using a page as a campaign.

1.1.1
-----
#. Filter Foundry comments by content type in admin.
#. Remove redundant chatroom detail template. It caused a comment count bug.
#. Allow social sharing of content even if it is a private site.
#. Remove jquery from basic layer since it causes out of memory errors on some devices. We will in future look for an API compatible replacement.
#. Add `jmbo-twitter` as dependency.
#. Provide three customizable listings to enable developers to easily add more listings.

1.1
---
#. Rename potentially confusing photosizes used in listing item templates. Old photosizes are retained for backward compatibility. If your app redefines a photosize for `listing_*` then you must update those photosize names.
#. Handle favicon.ico requests so they do not 404.
#. Include `jmbo-gallery` admin urls.

1.0.1
-----
#. Make fields in registration form reorderable.
#. Set initial values for location and age in registration form, when possible.
#. Remove hack to django-autopaginate to allow last page as default view. We have our own replacement autopaginate tag now.

1.0
---
#. Patch django.contrib.sites.models.Site.__unicode__ so it returns name and not domain. The UI gets confusing since we have up to three sites comprising one logical mobi site.
#. Listings now have automatic RSS feeds.
#. Comment form now fires up correct virtual keyboard for a smart phone.
#. Logged in members can now flag offensive comments. After three flags a moderator is notified.
#. Some IP addresses can now be allowed to bypass the age gateway / private site.
#. Listing gets an optional RSS feed.
#. Simplified paginator. No more breadcrumbs.
#. Show less metadata in mobi listings.
#. Ditch addthis sharing widget. It is too slow.
#. Simplified commenting and chatroom. Removed some navigation links.
#. Some user agents can now be allowed to bypass the age gateway. This allows bots to crawl the site.
#. Up required jmbo to 1.0.

0.7.2
-----
#. Hotfix. Apps with empty URL patterns cause infinite recursion when adding a page.

0.7.1
-----
#. Hotfix. Remove references deprecated `jmbo-gallery` views.

0.7
---
#. A listing now has an optional view modifier. This makes it possible to filter or order the listing.
#. `compute_settings` function is now redundant thanks to the introduction of `foundry.finders.FileSystemLayerAwareFinder`. Add this finder to STATICFILES_FINDERS as the first item.
#. Gallery specific code ported to `jmbo-gallery`. `base_inner.html` has a new link to gallery CSS and JS. If you have a customized template then update accordingly.
#. Up required `jmbo-gallery` to 0.1.

0.6.4
-----
#. Replace deprecated message_set call.

0.6.3
-----
#. Move FileSystemStorage listdir monkey patch to __init__.py so it is applied for collectstatic.

0.6.2
-----
#. Django 1.4 incompatibilities with login and password reset fixed.
#. More tests.

0.6.1
-----
#. Change admin static file urls to use 'static' filter instead of deprecated 'ADMIN_MEDIA_PREFIX'.

0.6
---
#. Up required jmbo to 0.5. Django 1.4 now implicitly required. You may get errors on template loaders not being found. See the Django 1.4 changelog in that case.

0.5.1
-----
#. Clean up ajax batching of listings for basic and smart layers. 
#. View modifiers and modelbase_list.html style templates are not ajaxified anymore.
#. Country model has new field country code.
#. Up required jmbo to 0.4.

0.5
---
#. "More" style batching for smart layer.
#. Listings now have optional pinned items which are anchored to the top of a listing.
#. Default photosizes for basic, mid, smart and web. Some old settings have changed so existing images may be scaled differently.

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


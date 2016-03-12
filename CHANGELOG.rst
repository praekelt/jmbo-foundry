Changelog
=========

2.1.1
-----
#. Deprecate legacy photosizes named `listing_*`.
#. Fix smart layer Javascript to correctly identify listing on ajax actions.

2.1
---
#. Fix bug where listing did not return content in the correct order. Note that `listing.queryset` is not guaranteed to return a real queryset anymore.
#. Remove view_modifier field from listing change form until we move to Django 1.8.

2.0.5
-----
#. Cosmetic change. Listing image background clashed with alternate row colour in Django admin.

2.0.4
-----
#. Remove CSRF protection from search form since searching is always a readonly operation.
#. Improve listing admin UI.

2.0.3
-----
#. Work around deprecated PickleSerializer when setting session expiry.
#. Defensive code in member detail view.

2.0.2
-----
#. Do not attempt to call photologue getters in template if image is not set.
#. Page editor now uses jQuery 1.10.2 and jQuery UI 1.10.4.

2.0.1
-----
#. Change position of api in urls.py so resource registration works properly.

2.0.0
-----
#. Simplify API to use primary keys.
#. Depend on stable versions of Jmbo products.

2.0.0a5
-------
#. Remove references to atlas in migrations.

2.0.0a4
-------
#. Fix sitemap urls.

2.0.0a3
-------
#. Listing fields content and pinned now use a through manager making ordering possible.

2.0.0a2
-------
#. Fix case where `resolve()` would fail if site is run from a subpath.

2.0.0a1
-------
#. Move to Django 1.6 support. Backwards incompatible.
#. Use `django-layers-hr` to handle layering. The FOUNDRY['layers'] setting is now deprecated.
#. Deprecate legacy handling for substring `_LAYER_` in photosize name.
#. Add a `ViewProxy` model enabling views to appear in listings.

1.3.0
-----
#. Deprecate `compute_settings` function.
#. Ignore result of celery tasks as appropriate.
#. Up `jmbo` requirement to 1.2.0.
#. Up `jmbo-post` requirement to 0.4.
#. SEO improvements in templates.

1.2.6.1
-------
#. Delegate photologue dependency to Jmbo.

1.2.6
-----
#. Fix naughty word task emoji handling.

1.2.5.1
-------
#. Fix typo leading to unassigned variable.

1.2.5
-----
#. RSS2 feed now includes canonical image.

1.2.4
-----
#. Validate member profile image strictly.
#. Allow = in username.
#. Friendly error message when attempting to use the same slug for overlapping sites.

1.2.3.1
-------
#. Use new version of `django-ckeditor` with prettier toolbars.
#. Make ajax pagination more robust. It now always targets the correct listing.
#. Fix password setting on member change form.

1.2.2.3
-------
#. Hotfix - fix missing import.

1.2.2.2
-------
#. Hotfix - image layer fallback functionality restored.

1.2.2.1
-------
#. Hotfix - added dependency link to photologue.

1.2.2
-----
#. Fix forms.css rule for required fields.
#. Adapt monkey patch because of `django-photologue` version 2.8.praekelt.
#. Make it possible to define custom listings.

1.2.1
-----
#. Use `next` parameter when redirecting to age gateway. On successfully passing the age gateway, the user is redirected to `next`.
#. Allow a partner site to automatically pass the age gateway for a user by providing age gateway data in a JWT token.

1.2
---
#. Move to jQuery 1.10.2 as recommended version. If you have customized and static Javascript resources you will have to update them manually.
#. Use a newer version of AnythingSlider.
#. Allow form class to be passed to join view.
#. Cache individual comments on comment list.
#. Minor performance improvements.

1.1.23
------
#. Fix template error in `modelbase_list_item_ipod.html`.

1.1.22
------
#. Fix bug where it was possible for an event handler to change the default avatar during user registration.
#. Cache individual listing item templates.

1.1.21
------
#. Content type, categories and tags fields on listings are now ANDed when evaluating the listing.
#. Do not allow comments containing only spaces.

1.1.20
------
#. Provide two more custom listing styles.
#. Listings can now be filtered by tag.

1.1.19.3
--------
#. Use `django-setuptest` 0.1.4. It handles South migrations correctly.
#. Use workaround so `jmbo-sitemap` works correctly again.

1.1.19.2
--------
#. Really do what is stated in 1.1.19.1.

1.1.19.1
--------
#. Found a critical error in legacy Jmbo code that is triggered by `jmbo-sitemap` URL pattern. Remove `jmbo-sitemap` URL patterns.

1.1.19
------
#. Remove potential `get_preference` cache key collision.
#. Port XML sitemap over to `jmbo-sitemap`.

1.1.18.2
--------
#. Protect comment creation against manually crafted POSTs.

1.1.18.1
--------
#. Hotfix. Fix bug where page change form did not display rows.

1.1.18
------
#. Change listing to accept multiple categories. A South data migration is involved and should work without issue, but it is recommended to backup your database.
#. Generate intentionally simple XML sitemap from the main navigation elements.
#. Offer Google Oauth2 login.

1.1.17
------
#. Web promo listing now displays pinned items.
#. Make ajax pagination more robust.
#. Allow @ in username.
#. Friendlier admin form when setting required fields in Registration Preferences.

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


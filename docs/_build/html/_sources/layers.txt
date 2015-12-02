Layers
------

Jmbo Foundry makes use of https://pypi.python.org/pypi/django-layers-hr.
It makes it possible to serve a set of templates and static resources as defined in `settings.py`.
This means you can serve different HTML, Javascript and CSS to eg. basic mobile devices,
smart phones and desktop browsers. These template sets (aka layers) also stack, so if
you create foo.html for basic devices it is automatically available for desktop
browsers as well. You can override foo.html for desktop browsers.


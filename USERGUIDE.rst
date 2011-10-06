Jmbo Generic User Guide
=======================

Initial configuration
---------------------

`jmbo-generic` requires initial configuration before it is ready to serve your
site.

Sites
*****

Your web presence typically consists of a normal web site and a mobile site.
There may be many more types of sites in future and `jmbo-generic` makes it
easy to configure them independently. If your main site is served on
`www.mysite.com` then go to `Sites` in the admin interface and set `Domain
name` and `Display name` accordingly. Then add a site entry for your mobile
site and set the values to `m.mysite.com`.

Preferences
-----------

`jmbo-generic` strives for a high level of through the web configuration. Much
of the site's behaviour is customizable through the admin interface.

General preferences
*******************

Check `show_age_gateway` to enable the age gateway for the site. Visitors must
confirm their age before they are allowed to browse the site.

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
change this setting.

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

Navbar preferences
******************

The navigation bar typically contains a small amount of items since horizontal
space is limited.  Each item in the navigation bar is represented as a `link`.
Links are not just normal links, although they can be. A link has a title and
may point either to a dynamic page already available in the site, a category or
a normal URL.

Menu preferences
****************

The site menu is exactly the same as the navigation bar, except it is rendered at 
then bottom of the home page and has a vertical layout by default.

Element preferences
*******************

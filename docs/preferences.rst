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


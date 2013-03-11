from urllib import urlretrieve
import dateutil.parser

from django.core.files import File

from social_auth.signals import pre_update
from social_auth.backends.facebook import FacebookBackend
from social_auth.backends.twitter import TwitterBackend


def facebook_extra_values(sender, user, response, details, **kwargs):
    mapping = {
        'email': 'email',
        'first_name': 'first_name',
        'last_name': 'last_name', 
        'bio': 'about_me',
        'gender': 'gender',
        'birthday': 'dob'
    }

    for key, fieldname in mapping.items():
        value = details.get(key, None)

        # Sanitize some fields
        if key == 'gender':
            if value:
                value = value[0]
        elif key == 'birthday':
            if value:
                try:
                    value = dateutil.parser.parse(value)
                except ValueError:
                    pass

        if value:
            setattr(user, fieldname, value)

    # Image
    username = details['username']
    url = 'http://graph.facebook.com/%s/picture' % username
    tempfile = urlretrieve(url)
    user.image.save('%s.jpg' % username, File(open(tempfile[0])))

    return True

pre_update.connect(facebook_extra_values, sender=FacebookBackend)


def twitter_extra_values(sender, user, response, details, **kwargs):
    
    # Image
    username = details['username']
    url = 'https://api.twitter.com/1/users/profile_image/%s?size=bigger' % username
    tempfile = urlretrieve(url)
    user.image.save('%s.jpg' % username, File(open(tempfile[0])))

    return True

pre_update.connect(twitter_extra_values, sender=TwitterBackend)

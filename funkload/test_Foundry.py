# -*- coding: iso-8859-15 -*-
"""foundry FunkLoad test

$Id: $
"""
import unittest
from random import randint
from funkload.FunkLoadTestCase import FunkLoadTestCase
from webunit.utility import Upload
from funkload.utils import Data
from funkload.utils import xmlrpc_get_credential, extract_token

class Foundry(FunkLoadTestCase):
    """XXX

    This test use a configuration file Foundry.conf.
    """

    def setUp(self):
        """Setting up test."""
        self.logd("setUp")
        self.server_url = self.conf_get('main', 'url')
        credential_host = self.conf_get('credential', 'host')
        credential_port = self.conf_getInt('credential', 'port')
        self.login, self.password = xmlrpc_get_credential(credential_host,
                                                          credential_port,
                                                         'Member_Group')

    def test_foundry(self):
        # The description should be set in the configuration file
        server_url = self.server_url
        # begin of test ---------------------------------------------
        self.get(server_url + "/blogposts/",
            description="Get /blogposts/")
        #self.get(server_url + "/listing/listing-large-set/",
        #    description="Get /listing/listing-large-set/")

        '''
        # Login
        self.get(server_url + "/login/",
            description="Get /login/")

        token = extract_token(self.getBody(), "name='csrfmiddlewaretoken' value='", "' />")
        self.post(server_url + "/login/", params=[
            ['username', 'alice'],
            ['csrfmiddlewaretoken', token],
            ['password', 'local'],
            ['next', '']],
            description="Post /login/")

        self.get(server_url + "/",
            description="Get /")

        # Navigate over blogposts
        self.get(server_url + "/blogposts/?by=most-liked",
            description="Get /blogposts/")

        #self.get(server_url + "/blogposts/?by=most-liked&for=this-month",
        #    description="Get /blogposts/")

        self.get(server_url + "/blogposts/?page=2",
            description="Get /blogposts/")

        self.get(server_url + "/blogposts/?page=3",
            description="Get /blogposts/")

        self.get(server_url + "/blogposts/?page=1000",
            description="Get /blogposts/")

        # Navigate over main page (tiled layout, paging affects all listings on
        # page so potentially expensive).
        self.get(server_url + "/?page=2",
            description="Get /")

        self.get(server_url + "/?page=3",
            description="Get /")

        # Navigate to an item and comment on it item 5 times
        self.get(server_url + "/blogpost/blog-post-10149",
            description="Get /blogpost/blog-post-10149")
        for i in range(0, 5):
            token = extract_token(self.getBody(), "name='csrfmiddlewaretoken' value='", "' />")
            security_hash = extract_token(self.getBody(), 'name="security_hash" value="', '" id="id_security_hash" />')
            timestamp = extract_token(self.getBody(), 'name="timestamp" value="', '" id="id_timestamp" />')
            self.post(server_url + "/comments/post/", params=[
                ['comment', 'A lovely comment %s %s' % (i, randint(1, 1000000))],
                ['name', 'Anonymous'],
                ['url', ''],
                ['timestamp', timestamp],
                ['object_pk', '10149'],
                ['next', '/blogpost/blog-post-10149/?paginate_by=&my_messages='],
                ['post', 'Post'],
                ['security_hash', security_hash],
                ['content_type', 'foundry.blogpost'],
                ['honeypot', ''],
                ['csrfmiddlewaretoken', token],
                ['in_reply_to', ''],
                ['email', 'anonymous@jmbo.org']],
                description="Post /comments/post/")
            self.get(server_url + "/blogpost/blog-post-10149",
                description="Get /blogpost/blog-post-10149")

        # Create blogpost start
        self.get(server_url + "/create-blogpost/",
            description="Get /create-blogpost/")

        token = extract_token(self.getBody(), "name='csrfmiddlewaretoken' value='", "' />")
        self.post(server_url + "/create-blogpost/", params=[
            ['content', ''],
            ['csrfmiddlewaretoken', token],
            ['title', '']],
            description="Post /create-blogpost/")

        token = extract_token(self.getBody(), "name='csrfmiddlewaretoken' value='", "' />")
        self.post(server_url + "/create-blogpost/", params=[
            ['content', 'Made by funkload'],
            ['csrfmiddlewaretoken', token],
            ['title', 'A new blogpost']],
            description="Post /create-blogpost/")

        # Logout
        self.get(server_url + "/logout/",
            description="Get /logout/")       
        '''

        # end of test -----------------------------------------------

    def tearDown(self):
        """Setting up test."""
        self.logd("tearDown.\n")



if __name__ in ('main', '__main__'):
    unittest.main()

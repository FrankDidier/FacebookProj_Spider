# -*- coding: utf-8 -*-
"""
Instagram User Item
"""
from autoads.item import Item
from autoads.config import config


class InstagramUserItem(Item):
    __table_name__ = './ins/user/'
    __update_key__ = ('status', 'update_time')

    def __init__(self):
        self.username = None
        self.user_link = None
        self.user_id = None
        self.full_name = None
        self.bio = None
        self.followers_count = 0
        self.following_count = 0
        self.posts_count = 0
        self.is_verified = False
        self.is_private = False
        self.profile_pic_url = None
        self.ads_id = None
        self.create_time = None
        self.update_time = None
        self.status = 'init'  # init, collected, failed
        self.unique_key = ('user_link',)


class InstagramFollowerItem(Item):
    __table_name__ = './ins/follower/'
    __update_key__ = ('status',)

    def __init__(self):
        self.target_user = None  # The user whose followers we're collecting
        self.target_user_link = None
        self.follower_username = None
        self.follower_link = None
        self.follower_full_name = None
        self.ads_id = None
        self.create_time = None
        self.status = 'init'
        self.unique_key = ('target_user', 'follower_link')


class InstagramFollowingItem(Item):
    __table_name__ = './ins/following/'
    __update_key__ = ('status',)

    def __init__(self):
        self.target_user = None  # The user whose following we're collecting
        self.target_user_link = None
        self.following_username = None
        self.following_link = None
        self.following_full_name = None
        self.ads_id = None
        self.create_time = None
        self.status = 'init'
        self.unique_key = ('target_user', 'following_link')


class InstagramReelsCommentItem(Item):
    __table_name__ = './ins/reels_comment/'
    __update_key__ = ('status',)

    def __init__(self):
        self.reels_url = None
        self.reels_id = None
        self.comment_id = None
        self.comment_text = None
        self.comment_author = None
        self.comment_author_link = None
        self.comment_time = None
        self.likes_count = 0
        self.ads_id = None
        self.create_time = None
        self.status = 'init'
        self.unique_key = ('reels_url', 'comment_id')


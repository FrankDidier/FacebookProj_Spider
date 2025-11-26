# -*- coding: utf-8 -*-
"""
Spider Manager - Centralized management for all spiders
"""
from spider.fb_group import GroupSpider
from spider.fb_group_specified import GroupSpecifiedSpider
from spider.fb_members import MembersSpider
from spider.fb_members_rapid import MembersRapidSpider
from spider.fb_posts import PostsSpider
from spider.fb_pages import PagesSpider
from spider.fb_greets import GreetsSpider
from spider.ins_followers import InstagramFollowersSpider
from spider.ins_following import InstagramFollowingSpider
from spider.ins_profile import InstagramProfileSpider
from spider.ins_reels_comments import InstagramReelsCommentsSpider
from autoads.config import config
from autoads import tools
import threading


class SpiderManager:
    """Manages all spider instances"""
    
    SPIDER_CLASSES = {
        'fb_group': GroupSpider,
        'fb_group_specified': GroupSpecifiedSpider,
        'fb_members': MembersSpider,
        'fb_members_rapid': MembersRapidSpider,
        'fb_posts': PostsSpider,
        'fb_pages': PagesSpider,
        'fb_greets': GreetsSpider,
        'ins_followers': InstagramFollowersSpider,
        'ins_following': InstagramFollowingSpider,
        'ins_profile': InstagramProfileSpider,
        'ins_reels_comments': InstagramReelsCommentsSpider,
    }
    
    @staticmethod
    def get_spider_class(spider_name):
        """Get spider class by name"""
        return SpiderManager.SPIDER_CLASSES.get(spider_name)
    
    @staticmethod
    def start_spider(spider_name, thread_count=None, ui=None, ms=None, tab_index=0, stop_event=None, grid_layout=None):
        """Start a spider by name"""
        spider_class = SpiderManager.get_spider_class(spider_name)
        if not spider_class:
            raise ValueError(f"Unknown spider: {spider_name}")
        
        if thread_count is None:
            thread_count = tools.get_greet_threading_count(config_from_newest=config)
        
        if stop_event is None:
            stop_event = threading.Event()
        
        # Get ads_ids
        ads_ids = tools.get_ads_id(config.account_nums)
        
        # Create and start spider
        spider = spider_class(
            thread_count=thread_count,
            ads_ids=ads_ids,
            config=config,
            ui=ui,
            ms=ms,
            tab_index=tab_index,
            stop_event=stop_event,
            grid_layout=grid_layout
        )
        
        spider.start()
        return spider, stop_event


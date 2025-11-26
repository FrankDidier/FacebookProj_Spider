# -*- coding: utf-8 -*-
"""
Created on 2022-06-10 23:56:14
---------
@summary:
---------
@author: Administrator
"""

from autoads.item import Item
from autoads.config import config


class UploadItem(Item):
    __table_name__ = config.get_option('table', 'tk_upload')
    __update_key__ = ('status', 'title_path', 'lang', 'upload_num', 'mp4_dir', 'mp4', 'title')

    def __init__(self):
        self.ads_id = None  # 使用的浏览器id，会对应tiktok账号，在获取成员的时候就直接使用此id
        self.name = None  # 每个浏览器对应的设置的账号名称
        self.mp4_dir = None  # 待发布的视频物理文件夹地址
        self.mp4 = None  # 记录已经发布了多少个视频，防止重复发送
        self.upload_num = 1  # 每次发送的视频个数
        self.title_path = None  # 待发布的视频标题物理文件夹地址
        self.title = None  # 已经发送过的文案 不超过150个
        self.lang = None  # tiktok账号需要使用的语言
        self.status = 'init'  # 默认就是已经发送的状态
        self.timeout = 10  # 默认10秒之后上传下一条视频
        self.create_time = None  # 记录一下此视频的发送时间
        self.unique_key = ('ads_id', 'mp4_dir')


class ViewItem(Item):
    __table_name__ = config.get_option('table', 'tk_view')
    __update_key__ = (
        'view_times', 'timeout', 'is_focus', 'is_like', 'is_comment', 'comment', 'is_comment_like',
        'comment_like_page_num','comment_like_num_in_page', 'like_num', 'comment_num', 'lang','target')

    def __init__(self):
        self.ads_id = None  # 使用的浏览器id，会对应tiktok账号，在获取成员的时候就直接使用此id
        self.name = None  # 每个浏览器对应的设置的账号名称
        self.lang = None
        self.is_focus = True  # 是否自动回关
        self.is_like = False  # 是否自动点赞
        self.like_num = 0  # 自动点赞的视频个数，默认1个
        self.follow_num=0 # 点赞之后是否需要关注，从已经点赞的视频中找到几个需要关注的账号
        self.is_comment = False  # 是否自动评论
        self.comment_num = 0  # 自动评论的视频个数，默认1个
        self.comment = None  # 评论内容，设置多条评论，发送的时候随机取一个
        self.is_comment_like = False  # 评论区的评论是否点赞
        self.comment_like_num_in_page = 0  # 评论区每页默认点赞3个
        self.comment_like_page_num = 0  # 评论区默认只点赞2页
        self.timeout = 15  # 默认让视频播放15秒之后再进行点赞、评论操作
        self.view_times = 20  # 默认自动看20个视频
        self.target='all' # 默认是同时对推荐页和已关注页操作
        self.unique_key = ('ads_id',)


class StreamItem(Item):
    __table_name__ = config.get_option('table', 'tk_stream')
    __update_key__ = ('status',)

    def __init__(self):
        self.ads_id = None  # 使用的浏览器id，会对应tiktok账号，在获取成员的时候就直接使用此id
        self.name = None  # 每个浏览器对应的设置的账号名称
        self.is_focus = False  # 是否关注
        self.to_tk_account = None  # 需要关注的目标账号，如果输入的是账号就不能输入视频地址了

        self.is_like = False  # 是否自动点赞
        self.is_forward = False  # 是否自动转发
        self.to_video = None  # 如果输入的是视频地址，就不能输入账号，目标视频 https://www.tiktok.com/@wasildaoud/video/7135970863962148138?is_from_webapp=v1&item_id=7135970863962148138 使用这个地址

        self.status = 'init'  # 默认就是初始化的状态 init,like,focus,forward
        self.timeout = 10  # 默认10秒之后上传下一条视频
        self.create_time = None  # 记录一下创建时间
        self.unique_key = ('ads_id', 'to_tk_account', 'to_video')

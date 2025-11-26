# -*- coding: utf-8 -*-
"""
Created on 2018-07-25 11:49:08
---------
@summary: 请求结构体
---------
@author: Boris
@email:  boris_liu@foxmail.com
"""
import threading
import autoads.tools as tools
from autoads.response import Response
from autoads.log import log
from autoads.webdriver import WebDriverPool
from autoads.config import config


class Request(object):
    session = None
    webdriver_pool: WebDriverPool = None

    local_filepath = None
    oss_handler = None

    __REQUEST_ATTRS__ = {
        # 'method', 'url', 必须传递 不加入**kwargs中
        "params",
        "data",
        "headers",
        "cookies",
        "files",
        "auth",
        "timeout",
        "allow_redirects",
        "proxies",
        "hooks",
        "stream",
        "verify",
        "cert",
        "json",
    }

    DEFAULT_KEY_VALUE = dict(
        url="",
        retry_times=0,
        priority=300,
        parser_name=None,
        callback=None,
        filter_repeat=True,
        auto_request=True,
        request_sync=False,
        use_session=None,
        random_user_agent=True,
        download_midware=None,
        is_abandoned=False,
        render=False,
        render_time=0,
    )

    def __init__(
            self,
            url="",
            retry_times=0,
            priority=300,
            parser_name=None,
            auto_request=True,
            request_sync=False,
            render=True,
            render_time=8,
            ads_id=None,
            response: Response = None,
            driver_count=1,
            is_drop=False,
            callback=None,
            finished_nums=0,
            stop_event=None,
            **kwargs,
    ):
        """

        :param url:
        :param retry_times:
        :param priority:
        :param parser_name:
        :param auto_request:
        :param request_sync:
        :param render:
        :param render_time:
        :param ads_id:
        :param response:
        :param driver_count:
        :param is_drop: 是否要丢弃这个请求
        :param callback:
        :param put_back:  被放回的次数和被放回的浏览器
        :param kwargs:
        """

        self.url = url
        self.retry_times = retry_times
        self.auto_request = auto_request
        self.render = render
        self.render_time = render_time
        self.ads_id = ads_id
        self.response = response
        self.parser_name = parser_name
        self.request_sync = request_sync
        self.callback = callback
        self.priority = priority
        self.finished_nums = finished_nums
        self.member_timeout = config.member_timeout
        self.driver_count = driver_count
        self.is_drop = is_drop
        self.put_back = {}
        self.stop_event=stop_event

        self.requests_kwargs = {}
        for key, value in kwargs.items():
            if key in self.__class__.__REQUEST_ATTRS__:  # 取requests参数
                self.requests_kwargs[key] = value

            self.__dict__[key] = value

    def __repr__(self):
        try:
            return f'<Request url={self.url},ads_id={self.ads_id},finished_nums={self.finished_nums},priority={self.priority}>'
        except:
            return "<Request {}>".format(str(self.to_dict)[:40])

    def __setattr__(self, key, value):
        """
        针对 request.xxx = xxx 的形式，更新reqeust及内部参数值
        @param key:
        @param value:
        @return:
        """
        self.__dict__[key] = value

        if key in self.__class__.__REQUEST_ATTRS__:
            self.requests_kwargs[key] = value

    def __lt__(self, other):
        return self.priority < other.priority

    @property
    def _webdriver_pool(self):
        if not self.__class__.webdriver_pool:
            self.__class__.webdriver_pool = WebDriverPool(**dict(
                timeout=30,  # 请求超时时间
                driver_count=self.driver_count,
                render_time=5  # 渲染时长，即打开网页等待指定时间后再获取源码
            ))

        # print(f'webdriver_pool:{id(self.__class__.webdriver_pool)}')

        return self.__class__.webdriver_pool

    @property
    def to_dict(self):
        request_dict = {}

        for key, value in self.__dict__.items():
            if (
                    key in self.__class__.DEFAULT_KEY_VALUE
                    and self.__class__.DEFAULT_KEY_VALUE.get(key) == value
                    or key == "requests_kwargs"
            ):
                continue

            if key in self.__class__.__REQUEST_ATTRS__:
                if not isinstance(
                        value, (bytes, bool, float, int, str, tuple, list, dict)
                ):
                    value = tools.dumps_obj(value)
            else:
                if not isinstance(value, (bytes, bool, float, int, str)):
                    value = tools.dumps_obj(value)

            request_dict[key] = value

        return request_dict

    def get_response(self,ms=None, ui=None):
        """
        获取带有selector功能的response
        @param save_cached: 保存缓存 方便调试时不用每次都重新下载
        @return:
        """
        # 设置超时默认时间
        self.requests_kwargs.setdefault(
            "timeout", 22
        )  # connect=22 read=22

        # 设置stream
        # 默认情况下，当你进行网络请求后，响应体会立即被下载。你可以通过 stream 参数覆盖这个行为，推迟下载响应体直到访问 Response.content 属性。此时仅有响应头被下载下来了。缺点： stream 设为 True，Requests 无法将连接释放回连接池，除非你 消耗了所有的数据，或者调用了 Response.close。 这样会带来连接效率低下的问题。
        self.requests_kwargs.setdefault("stream", True)

        # 关闭证书验证
        self.requests_kwargs.setdefault("verify", False)

        if self.render:
            browser = self._webdriver_pool.get(self.ads_id,ms=ms, ui=ui,stop_event=self.stop_event)
            if browser.get_driver():

                url = self.url
                if self.requests_kwargs.get("params"):
                    url = tools.joint_url(self.url, self.requests_kwargs.get("params"))

                try:
                    log.info(f'4、线程{threading.current_thread().name}下浏览器{self.ads_id}正在请求浏览器地址{url}')
                    tools.send_message_to_ui(ms=ms, ui=ui, message=f'浏览器{self.ads_id}正在打开地址中... | {url}')
                    if not (self.stop_event and self.stop_event.isSet()): # 当点击了停止按钮，浏览器已经开启，但是还没有请求的时候就可以不用请求也页面了
                        # 网络差的时候，等待第一个页面加载完成
                        if self.render_time:
                            tools.delay_time(self.render_time)

                        browser.get(url)

                        if self.render_time:
                            tools.send_message_to_ui(ms=ms, ui=ui, message=f'浏览器{self.ads_id}暂停{self.render_time}秒，等待页面加载完成，')
                            tools.delay_time(self.render_time)

                        html = browser.page_source
                        response = Response.from_dict(
                            {
                                "url": browser.current_url,
                                "cookies": browser.cookies,
                                "_content": html.encode(),
                                "status_code": 200,
                                "elapsed": 666,
                                "headers": {
                                    "User-Agent": browser.execute_script(
                                        "return navigator.userAgent"
                                    ),
                                    "Cookie": tools.cookies2str(browser.cookies),
                                },
                            }
                        )

                        response.browser = browser
                        tools.send_message_to_ui(ms=ms, ui=ui, message=f'浏览器{self.ads_id}请求地址{url} | 成功')
                    else:
                        response=None
                except Exception as e:
                    log.error(e)
                    tools.send_message_to_ui(ms=ms, ui=ui, message=f'浏览器{self.ads_id}请求地址{url} | 失败 | {str(e)}')
                    self._webdriver_pool.remove(self.ads_id)
                    raise e
            else:
                response = None

        self.response = response
        return response

    @classmethod
    def from_dict(cls, request_dict):
        for key, value in request_dict.items():
            if isinstance(value, bytes):  # 反序列化 如item
                request_dict[key] = tools.loads_obj(value)

        return cls(**request_dict)

    def copy(self):
        return self.__class__.from_dict(self.to_dict)

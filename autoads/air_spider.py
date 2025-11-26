# -*- coding: utf-8 -*-

from threading import Thread
import autoads.tools as tools
from autoads.item_buffer import ItemBuffer
from autoads.parser_control import AirSpiderParserControl
from autoads.request import Request
from autoads.log import log
from autoads.memory_db import MemoryDB
# import tracemalloc


class AirSpider(Thread):
    __custom_setting__ = {}

    def __init__(self, thread_count=1, **kwargs):
        """
        基于内存队列的爬虫，不支持分布式
        :param thread_count: 线程数
        """
        # tracemalloc.start()

        super(AirSpider, self).__init__()

        self._thread_count = thread_count

        self._memory_db = MemoryDB()
        self._parser_controls = []

        self._processing_requests = MemoryDB()

        for key, value in kwargs.items():
            self.__dict__[key] = value

        if not hasattr(self, 'ms'):
            self.ms = None

        if not hasattr(self, 'ui'):
            self.ui = None

        if not hasattr(self, 'stop_event'):
            self.stop_event = None

        if not hasattr(self, 'grid_layout'):
            self.grid_layout = None

        self._item_buffer = ItemBuffer(stop_event=self.stop_event)

    def distribute_task(self):
        log.info(f'开始调用start_requests中的请求')
        # tools.send_message_to_ui(self.ms, self.ui, "开始调用start_requests中的请求")
        i = 0
        for request in self.start_requests():
            if not isinstance(request, Request):
                raise ValueError("仅支持 yield Request")

            request.parser_name = request.parser_name or self.name
            self._memory_db.add(request)
            i += 1

        log.info(f'调用start_requests结束，共加入了{i}个请求')
        tools.send_message_to_ui(self.ms, self.ui, f'采集器共加入了{i}个请求')
        # tools.send_message_to_ui(self.ms, self.ui, f'调用start_requests结束，共加入了{i}个请求')

    def all_thread_is_done(self):
        # if hasattr(self, 'stop_event') and self.stop_event.isSet():
        #     return True

        for i in range(3):  # 降低偶然性, 因为各个环节不是并发的，很有可能当时状态为假，但检测下一条时该状态为真。一次检测很有可能遇到这种偶然性
            # 检测 parser_control 状态
            for parser_control in self._parser_controls:
                if not parser_control.is_not_task():
                    if hasattr(self, 'stop_event') and self.stop_event and self.stop_event.isSet():
                        tools.send_message_to_ui(self.ms, self.ui, '正在终止多个采集器...')
                    return False

            # 检测 任务队列 状态
            if not self._memory_db.empty():
                if hasattr(self, 'stop_event') and self.stop_event and self.stop_event.isSet():
                    tools.send_message_to_ui(self.ms, self.ui, f'正在清空请求库...')
                return False

            # 检测 item_buffer 状态
            if (
                    self._item_buffer.get_items_count() > 0
                    or self._item_buffer.is_adding_to_db()
            ):
                if hasattr(self, 'stop_event') and self.stop_event.isSet():
                    tools.send_message_to_ui(self.ms, self.ui, f'还有{self._item_buffer.get_items_count()}条数据没有保存')
                return False

            tools.delay_time(1)
        # 跟踪内存分配情况
        # snap_shot=tracemalloc.take_snapshot()
        # top_stats=snap_shot.statistics('lineno')
        # for stat in top_stats:
        #     log.info(stat)
        return True

    def run(self):
        # print(f'threading.current_thread()={threading.current_thread().__class__.__name__}')
        log.info(f'主线程开始启动，准备开启{self._thread_count}个ParserControl线程')

        tools.send_message_to_ui(self.ms, self.ui, '采集器启动中...')

        if hasattr(self, 'is_use_interval_timeout'):
            is_use_interval_timeout = self.is_use_interval_timeout
        else:
            is_use_interval_timeout = False

        # 请求推入queue中
        tools.send_message_to_ui(self.ms, self.ui, '采集器加载任务中...')
        self.distribute_task()

        for i in range(self._thread_count):
            parser_control = AirSpiderParserControl(self._memory_db, self._item_buffer, self._processing_requests,
                                                    ui=self.ui, ms=self.ms,
                                                    grid_layout=self.grid_layout, stop_event=self.stop_event,
                                                    is_use_interval_timeout=is_use_interval_timeout)
            parser_control.add_parser(self)
            parser_control.start()
            self._parser_controls.append(parser_control)

        self._item_buffer.start()

        tools.send_message_to_ui(self.ms, self.ui, "采集中...")

        stop_message_send = False

        precessed_req = 0

        while True:
            try:
                if hasattr(self, 'stop_event') and self.stop_event and self.stop_event.isSet() and not stop_message_send:
                    tools.send_message_to_ui(self.ms, self.ui, "停止采集中...")
                    stop_message_send = True

                # 获取历史请求库，实时显示到界面中
                requests = self._processing_requests.get()
                if requests:
                    precessed_req += 1
                    if hasattr(self,'request_to_str') and callable(self.request_to_str):
                        tools.send_message_to_ui(self.ms, self.ui,
                                                 f'{precessed_req}.{self.request_to_str(requests)}')
                    else:
                        tools.send_message_to_ui(self.ms, self.ui,
                                                 f'{precessed_req}.<font color="#3900FF">{requests.url}\n</font>')

                is_done = self.all_thread_is_done()
                # print(f'is_done={is_done}')
                if is_done:
                    # 停止 parser_controls
                    for parser_control in self._parser_controls:
                        parser_control.stop()

                    # 关闭item_buffer
                    self._item_buffer.stop()

                    # 关闭webdirver
                    if Request.webdriver_pool:
                        Request.webdriver_pool.close()

                    log.info("无任务，爬虫结束")

                    tools.send_message_to_ui(self.ms, self.ui, f"无任务，采集结束")
                    if self.ms:
                        self.ms.update_control_status.emit([True,self.tab_index])  # 通知界面更新按钮的状态
                    break

            except Exception as e:
                log.exception(e)

            tools.delay_time(1)  # 1秒钟检查一次爬虫状态

        # 为了线程可重复start
        self._started.clear()

    def join(self, timeout=None):
        """
        重写线程的join
        """
        if not self._started.is_set():
            return

        super().join()

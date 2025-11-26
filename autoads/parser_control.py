# -*- coding: utf-8 -*-

import threading
import time
from queue import Empty
from collections.abc import Iterable

import autoads.tools as tools
from autoads.item_buffer import ItemBuffer
from autoads.memory_db import MemoryDB
from autoads.item import Item
from autoads.log import log
from autoads import ads_api
from urllib.parse import urlparse
from autoads.request import Request


class AirSpiderParserControl(threading.Thread):
    is_show_tip = False

    # 实时统计已做任务数及失败任务数，若失败任务数/已做任务数>0.5 则报警
    _success_task_count = 0
    _failed_task_count = 0

    def __init__(self, memory_db: MemoryDB, item_buffer: ItemBuffer,processing_request: MemoryDB, ui=None, ms=None, grid_layout=None,
                 stop_event=None,is_use_interval_timeout=False):
        super(AirSpiderParserControl, self).__init__()
        self._parsers = []
        self._memory_db = memory_db
        self._processing_request=processing_request
        self._thread_stop = False
        self._wait_task_time = 0
        self._item_buffer = item_buffer
        self.ads_id = None  # 当前线程正在操作的浏览器id
        self.new_ads_id = None  # 当发现浏览器对应的账号有异常，就会更新此参数，来开启新的浏览器，处理请求
        self._finished_nums = 0  # 当前线程已经处理了多少个请求，当超过配置文件中的请求数，就会重新更新需要操作的浏览器，并清空此参数
        self.is_running = False  # 当前线程是不是有请求正在处理，有可能是还没有返回结果出来，网络出现了卡的情况，这个时候就需要先不要拿请求出来了
        self.ui = ui  # 此参数
        self.ms = ms
        self.grid_layout = grid_layout
        self.stop_event = stop_event
        self.is_use_interval_timeout=is_use_interval_timeout

    def init_thread_custom_param(self):
        self.ads_id = None  # 清空当前线程只处理指定的ads_id请求的限制，重新去处理还没有在处理的ads_id
        self._wait_task_time = 0
        self._finished_nums = 0
        self.new_ads_id = None

    def request_put_back(self, request=None):
        # 将请求的put_back参数添加每个线程正在处理这个请求的次数，防止一个请求被一个线程同时出来多次，造成死循环
        if self.ads_id and request:
            key = self.ads_id + '_' + urlparse(request.url).path
            if key not in request.put_back:
                request.put_back[key] = 1
            else:
                request.put_back[key] += 1

            if request.put_back[key] > 2:
                return False
            else:
                return True

        else:
            return False

    def run(self):
        # print(f'self._started={self._started.is_set()}')
        log.info(f'1、处理请求线程{threading.current_thread().name}开始启动，等待请求任务的到来')
        tools.setTextBrowserObjectName(ui=self.ui, grid_layout=self.grid_layout)

        while not self._thread_stop:
            try:
                # 如果这个线程有正在处理的请求，就先不拿新的请求出来了
                if self.is_running:
                    tools.delay_time(2)
                    continue

                # 先去缓存里面看是不是有属于当前ads_id被丢弃的请求，如果有就取出来，如果没有就从请求库中取
                if self.ads_id and Request.webdriver_pool:
                    drop_request = Request.webdriver_pool.get_drop_res(self.ads_id)
                    if drop_request:
                        log.info(f'线程{threading.current_thread().name}浏览器（{self.ads_id}获取丢弃的请求{drop_request}')
                        requests = drop_request
                    else:
                        requests = self._memory_db.get()  # 取出请求
                else:
                    requests = self._memory_db.get()  # 取出请求

                self.is_running = True  # 只要取出来请求，就说明当前线程正在处理这个请求了

                # 多个浏览器同时启动处理，需要让每个浏览器处理同一个类型的请求，不然就会打断别的浏览器的处理过程
                # 每个浏览器都是有一个ads_id对应，每个请求也有一个ads_id属性
                # 当一个线程已经处理完一个请求，就需要重新获取下一个同ads_id的请求
                if not requests:
                    if not self.is_show_tip:
                        log.debug("parser 等待任务...")
                        self.is_show_tip = True

                    time.sleep(1)
                    self._wait_task_time += 1
                    self.is_running = False
                    continue

                # 判断是不是同一个账号下的请求，如果不是就把这个请求放回去，等其他线程去拿到这个请求去处理
                is_put_back = self.request_put_back(requests)
                if self.ads_id and self.ads_id != requests.ads_id:
                    log.info(
                        f'2、线程{threading.current_thread().name}浏览器{self.ads_id}获取到不是同一个账号下的请求:{requests},is_put_back={is_put_back}')
                    if is_put_back:  # 判断是不是可以放回，如果同一个线程放回的次数超过5次，就不再放回，就认定丢弃了，这种情况有可能是卡死或者死循环
                        requests.priority += 11
                        log.info(
                            f'2、线程{threading.current_thread().name}下浏览器{self.ads_id}针对请求{requests}正在放回第{requests.put_back[self.ads_id+"_"+urlparse(requests.url).path]}次')
                        self._memory_db.add(requests)
                        # tools.delay_time(5)
                    else:
                        log.info(f'2、线程{threading.current_thread().name}下浏览器{self.ads_id}针对请求{requests}丢弃')
                        Request.webdriver_pool.add_drop_res(requests)  # 保存被丢弃的请求，这样别的线程就会知道
                        # pass
                        # self._finished_nums+=1
                else:
                    # 判断ads_id是不是正在处理，通过webdriver_pool中去查找是否存在，如果存在就不处理当前请求
                    # 此判断是因为总请求个数小于线程开启数，如果没有这个判断，就会产生不同的线程同时操作同一个浏览器的情况发生
                    # 只要在开启线程个数的时候，不要超过请求的个数，就不会发生上面的情况
                    # 还有一种情况是，线程在循环下一个浏览器的时候，有可能这个浏览器被别的线程已经打开了，正在处理，也有可能是已经过期的
                    if not self.ads_id and Request.webdriver_pool and Request.webdriver_pool.exists(requests.ads_id):
                        log.info(
                            f'2. 线程{threading.current_thread().name}准备处理{requests.ads_id},发现有别的线程正在处理！重新放回,is_put_back={is_put_back}')
                        # 考虑到线程刚刚被初始化self.ads_id=None，同时拿到的ads_id是其他线程正在处理的
                        # 这个时候请求就直接丢弃了，因为并不能设置参数来表示这个请求被当前线程下的浏览器放回的次数
                        # 所以干脆丢弃掉
                        log.info(f'2、线程{threading.current_thread().name}下浏览器{self.ads_id}针对请求{requests}丢弃')
                        Request.webdriver_pool.add_drop_res(requests)  # 保存被丢弃的请求，这样别的线程就会知道
                    else:
                        self.is_show_tip = False
                        if ads_api.expired_ads(requests.ads_id):  # 判断此浏览器是不是已经过期了
                            log.info(f'2. 线程{threading.current_thread().name}准备处理{requests},发现浏览器过期了！请求丢弃不处理')
                            self.is_running = False
                            continue

                        log.info(f'2、线程{threading.current_thread().name}开始处理请求任务：-->{requests}')
                        # tools.send_message_to_ui(ms=self.ms,ui=self.ui,message='程序开始采集中...')
                        tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'采集<font color="#3900FF">{requests.url}</font>开始')

                        self._processing_request.add(requests)

                        self.ads_id = requests.ads_id

                        requests.finished_nums = self._finished_nums
                        log.info(
                            f'线程{threading.current_thread().name}状态1【ads_id={self.ads_id},_finished_nums={self._finished_nums},new_ads_id={self.new_ads_id}】')
                        self.deal_requests([requests])
                        # 只有在确定是处理一个浏览器的请求的时候才需要增加
                        # 当deal_requests在给线程初始化状态的时候，说明是上一个浏览器处理结束，
                        # 下一个浏览器等待进来的状态，这个时候就不要更新了，处理清零状态就可以了
                        if self.ads_id:
                            self._finished_nums += 1  # 给request添加已经处理了多少个请求的标志
                        log.info(
                            f'线程{threading.current_thread().name}状态3【ads_id={self.ads_id},_finished_nums={self._finished_nums},new_ads_id={self.new_ads_id}】')
                        tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'结束采集\r\n\r\n')
                        if self.is_use_interval_timeout:
                            tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'程序等待{requests.member_timeout}秒发送下一个成员')
                            tools.delay_time(requests.member_timeout)

                self.is_running = False

                # 当界面中点击了停止，当前线程让自己停止掉，不再取新的请求出来
                if self.stop_event and self.stop_event.isSet():
                    log.info(f'线程{threading.current_thread().name}  is_running={self.is_running}  正在清理请求库，并设置thread_stop=True，')
                    tools.clear_queue(self._memory_db.priority_queue)

                    if Request.webdriver_pool:
                        tools.send_message_to_ui(self.ms, self.ui, '浏览器关闭中...')
                        log.info(f'线程{threading.current_thread().name}打开的浏览器{self.ads_id}关闭中...')
                        Request.webdriver_pool.remove(self.ads_id)  # 浏览器关闭

                    self._thread_stop = True
                    self.is_running = False
                    self.is_show_tip = True  # 告诉主线程，自己已经完成自身的关闭了
                    self.init_thread_custom_param()  # 线程初始化
                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'结束采集\r\n\r\n')

            except Exception as e:
                log.exception(e)
                self.is_running = False
                if self.stop_event and self.stop_event.isSet():
                    self._thread_stop = True
                tools.delay_time(1)
                # raise e

    def deal_requests(self, requests):
        for request in requests:
            # 界面中点击了停止，就需要马上告诉线程执行清理程序了
            if self.stop_event and self.stop_event.isSet():
                break

            if Request.webdriver_pool and Request.webdriver_pool.expried(request.ads_id):
                log.info(
                    f'线程{threading.current_thread().name}状态2【expried=True,ads_id={self.ads_id},_finished_nums={self._finished_nums},new_ads_id={self.new_ads_id}】')
                if self.new_ads_id and self.ads_id != self.new_ads_id:  # 当发现原来浏览器失效了，就需要更换成新的可用浏览器
                    log.info(f'线程{threading.current_thread().name}更换浏览器（{request.ads_id}-->{self.new_ads_id}）')
                    request.ads_id = self.new_ads_id  # 在采集群组和采集成员的时候，会有其他账号替代，那么同ads_id的请求可以继续处理
                else:
                    log.info(f'线程{threading.current_thread().name}丢弃请求{request}')
                    return  # 需要丢弃同ads_id的请求，不做处理了，这个是发消息的时候发现了账号异常的话，是不会有账号来替代的，所以这么处理

            is_close_browser = False
            response = request.response

            for parser in self._parsers:
                if parser.name == request.parser_name:
                    try:

                        if request.index == -1:
                            log.info(f'线程{threading.current_thread().name}被初始化index=-1，处理请求{request}')
                            self.init_thread_custom_param()

                        # 解析request
                        if request.auto_request and not response:
                            log.info(f'线程{threading.current_thread().name}，开启浏览器获取请求{request}')
                            tools.send_message_to_ui(ms=self.ms, ui=self.ui, message='远程浏览器开启中...')
                            response = request.get_response(ms=self.ms, ui=self.ui)

                        if response:
                            if request.callback:  # 如果有parser的回调函数，则用回调处理
                                callback_parser = (
                                    request.callback
                                    if callable(request.callback)
                                    else tools.get_method(parser, request.callback)
                                )
                                results = callback_parser(request, response)
                            else:  # 否则默认用parser处理
                                log.info(f'线程{threading.current_thread().name}，开始处理结果页面数据，请求{request}')
                                # tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'开始采集页面数据...')
                                results = parser.parse(request, response)

                            if results and not isinstance(results, Iterable):
                                raise Exception(
                                    "%s.%s返回值必须可迭代"
                                    % (parser.name, request.callback or "parse")
                                )
                        else:
                            log.error(Exception(
                                "%s开启浏览器%s异常"
                                % (parser.name, request.ads_id)
                            ))
                            results=[]

                        # 此处判断是request 还是 item
                        for result in results or []:
                            log.info(f'线程{threading.current_thread().name}，开始解析页面数据')

                            # 界面中点击了停止，就需要马上告诉线程执行清理程序了
                            if self.stop_event and self.stop_event.isSet():
                                requests.clear()  # 清理请求库
                                break

                            if isinstance(result, Request):
                                # 给request的 parser_name 赋值
                                result.parser_name = result.parser_name or parser.name
                                log.info(f'线程{threading.current_thread().name}，开始处理返回的请求{result}')
                                # 判断是不是更新了ads_id,如果更新了，说明当前的ads_id是失效的
                                if self.ads_id != result.ads_id:
                                    log.info(f'线程{threading.current_thread().name}，返回的请求{result}更新了浏览器')
                                    self.new_ads_id = result.ads_id
                                    if result.is_drop:
                                        log.info(f'线程{threading.current_thread().name}，重新更新线程状态，丢弃返回的请求{result}')
                                        self.init_thread_custom_param()
                                        continue

                                # 判断是同步的callback还是异步的
                                if result.request_sync:  # 同步
                                    requests.append(result)
                                    log.info(f'线程{threading.current_thread().name}，返回的请求被同步到requests中及时处理，{result}')
                                else:  # 异步
                                    # 将next_request 入库
                                    log.info(f'线程{threading.current_thread().name}，返回的请求加入异步处理库，{result}')
                                    self._memory_db.add(result)

                            elif isinstance(result, Item):
                                self._item_buffer.put_item(result)
                                log.info(f'线程{threading.current_thread().name}，返回的数据加入异步数据保存库中，{result}')

                            # elif isinstance(result, Action):
                            #     self._action_buffer.put_action(result)

                            elif result is not None:
                                function_name = "{}.{}".format(
                                    parser.name, "parse",
                                )
                                raise TypeError(
                                    f"{function_name} result expect Request or Item, bug get type: {type(result)}"
                                )

                    except Exception as e:
                        is_close_browser = True
                        # 当请求发生异常了，让线程的参数进行初始化，防止请求死循环
                        self.init_thread_custom_param()
                        self.is_running = False
                        requests.clear()
                        tools.send_message_to_ui(self.ms, self.ui, '已停止')
                        log.info(f'线程{threading.current_thread().name}请求{request}发生了异常')
                        log.error(e)
                        # raise e
                    else:
                        # 记录成功任务数
                        self.__class__._success_task_count += 1
                    finally:
                        # 释放浏览器
                        if is_close_browser:
                            request.webdriver_pool.remove(request.ads_id)

                    break

        # 界面中点击了停止，就需要马上告诉线程执行清理程序了
        if self.stop_event and self.stop_event.isSet():
            if Request.webdriver_pool:
                tools.send_message_to_ui(self.ms, self.ui, '浏览器关闭中...')
                log.info(f'线程{threading.current_thread().name}打开的浏览器{self.ads_id}关闭中...')
                Request.webdriver_pool.remove(self.ads_id)  # 浏览器关闭

            self.is_show_tip = True  # 告诉主线程，自己已经完成自身的关闭了
            self.init_thread_custom_param()  # 线程初始化

    def stop(self):
        self._thread_stop = True
        self._started.clear()

    def add_parser(self, parser):
        self._parsers.append(parser)

    def is_not_task(self):
        return self.is_show_tip

    @classmethod
    def get_task_status_count(cls):
        return cls._failed_task_count, cls._success_task_count

# -*- coding: utf-8 -*-
"""
Created on 2022-06-10 16:06:44
---------
@summary:
---------
@author: Administrator
"""

import autoads
from autoads.log import log
from autoads.action_control import Action
from datetime import datetime
from autoads.items.group_item import GroupItem
from autoads.config import config
from autoads import tools
import codecs
import json
from autoads import ads_api
from urllib.parse import urlparse
import os
import threading


class GroupSpider(autoads.AirSpider):

    def start_requests(self):

        # pipeline = self._item_buffer._pipelines[0]

        if not self.ads_ids:
            self.ads_ids = tools.get_ads_id(self.config.account_nums)

        key_words = self.config.groups_words
        tools.send_message_to_ui(self.ms, self.ui, f"正在采集群组关键词{key_words}")

        # 根据我们配置的words的数量，来开启线程来处理
        # 根据可用的浏览器个数来开启动浏览器
        i = 0
        priority=10
        for word in key_words:
            # 判断是不是之前处理过，如果处理过就不处理了
            file_name = self.config.groups_table + tools.make_safe_filename(word) + '.txt'
            if os.path.exists(file_name):
                continue

            if i == len(self.ads_ids):  # 当浏览器可用个数小于关键词个数
                i = 0
                priority+=10

            ads_id = self.ads_ids[i]
            i += 1
            url = f"{self.config.groups_url}{word}"
            log.info(f'查询组：{url}')

            yield autoads.Request(url=url, ads_id=ads_id, index=0, priority=priority, word=word,
                                  driver_count=len(self.ads_ids),stop_event=self.stop_event)

    def parse(self, request, response):
        browser = response.browser

        log.info(
            f'线程{threading.current_thread().name}中浏览器{request.ads_id}请求地址比对:{urlparse(browser.current_url).path},{urlparse(request.url).path}')

        if urlparse(browser.current_url).path == urlparse(request.url).path:
            index = request.index
            if int(index) == -1:  # 判断是不是要关闭浏览器了，标志为-1，就是要关闭浏览器
                log.info(f'线程{threading.current_thread().name}中浏览器{request.ads_id}已经完成滚动，准备关闭了！')
                # 已经全部处理完了，那么这个ads_id就必须要关掉了，但是线程不关闭，此线程就要去处理别的ads_id的请求
                tools.delay_time(2)  # 暂停2秒
                # 关闭当前浏览器,线程重新初始化
                if request.webdriver_pool:
                    tools.send_message_to_ui(self.ms, self.ui, '没有更多的群组数据，外部浏览器关闭中...')
                    request.webdriver_pool.remove(request.ads_id)
            else:

                group_link_page = tools.get_page_data_mutilxpath(browser,self.config.groups_xpath_query)

                items_count = len(group_link_page)

                log.info(f'页面中获取到的元素个数：{items_count}-->上一次获取个数：{request.index}')

                group_link_page = group_link_page[request.index:]

                group_table = self.config.groups_table + tools.make_safe_filename(
                    request.word) + '.txt'  # 搜集的群组按照关键词保存到指定的文件夹中
                # Clean links file (just URLs)
                clean_links_file = group_table.replace('.txt', '_links.txt')
                log.info(f'保存的地址-->{group_table}')
                for i in range(len(group_link_page)):
                    # for item in group_link_page:
                    item = group_link_page[i]
                    insert_item = GroupItem()
                    insert_item.__table_name__ = group_table  # 重新设置保存的文件地址
                    insert_item.group_name = item.get_attribute('aria-label')
                    temp_link = item.get_attribute('href')
                    group_link = temp_link[:temp_link.rfind('?')]
                    insert_item.group_link = group_link
                    insert_item.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    insert_item.ads_id = request.ads_id
                    insert_item.word = request.word
                    # print(insert_item.group_link)
                    yield insert_item
                    # Also save clean link to separate file
                    tools.save_clean_link(clean_links_file, group_link)

                if items_count-request.index>0:
                    tools.send_message_to_ui(self.ms, self.ui, f'采集到[新{items_count-request.index}/总{items_count}]个群组')
                request.index = items_count
                # tools.send_message_to_ui(self.ms, self.ui, '页面滚动中...')
                is_finished = Action(browser).scroll_until_loaded()
                request.request_sync = True  # 把请求同步送入处理，不放到请求库
                if is_finished:
                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, message='群组采集结束，页面停止滚动')
                    # 当页面滚动已经结束了，那么就可以关闭掉浏览器
                    request.index = -1  # 发送可以关掉浏览器的标志，在下一次请求处理的时候，直接关闭掉
                    yield request
                else:
                    yield request
        else:
            # 通过判断是不是地址有跳转，如果是，说明这个账号有问题，就在列表中移除
            ads_api.remove_expired_ads(request.ads_id)
            request.webdriver_pool.remove(request.ads_id)
            request.webdriver_pool.queue_expried_ads.append(request.ads_id)
            new_ads_id = tools.get_single_ads(ignore=self.ads_ids)
            if new_ads_id:  # 当还有可以被分配的浏览器资源的时候，才会分配这个请求，如果没有，就不再分配了，这一类型的请求就只能放弃了
                log.info(f'线程{threading.current_thread().name}正关闭异常浏览器{request.ads_id}，使用新的浏览器{new_ads_id}重新处理请求')
                request.ads_id = new_ads_id  # 需要在线程中更新当前线程需要处理的ads_id,防止当前线程执行了一个就不执行了
                request.request_sync = True
                request.response = None
                tools.send_message_to_ui(self.ms, self.ui, '检测到Facebook账号异常，正在更换新的账号...')
            else:
                request.ads_id = '######'  # 需要在线程中更新当前线程需要处理的ads_id,防止当前线程执行了一个就不执行了
                request.response = None
                request.is_drop = True  # 让程序丢弃掉这个请求，之所以还返回这个请求，是因为要告诉线程，让线程清空自己的状态，重新去获取新的
                log.info(f'线程{threading.current_thread().name}正关闭异常浏览器{request.ads_id}，并丢弃此请求')
                tools.send_message_to_ui(self.ms, self.ui, '检测到Facebook账号异常，可用账号不足，请检查账号配置')

            yield request

    def pre_close(self):
        # 在程序要结束之前，把抓取到的群组信息，保存到用户自定义的文件中
        table = tools.abspath(self.config.groups_table)
        # bak = tools.abspath(self.config.groups_bak)
        user = tools.abspath(self.config.groups_user)

        unique_key = GroupItem().unique_key[0]
        print(unique_key)

        with codecs.open(table, 'r', encoding='utf-8') as fi, \
                codecs.open(user, 'w', encoding='utf-8') as fo:
            for line in fi:
                dictobj = json.loads(line)
                fo.write(dictobj[unique_key] + '\n')


if __name__ == "__main__":
    ads_ids = tools.get_ads_id(config.account_nums)  # 根据配置的浏览器开启数量来开启多少个线程
    GroupSpider(
        thread_count=len(ads_ids) if len(ads_ids) < len(config.groups_words) else len(config.groups_words),
        ads_ids=ads_ids, config=config).start()

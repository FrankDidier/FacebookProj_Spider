# -*- coding: utf-8 -*-
"""
Created on 2022-06-10 16:06:44
---------
@summary:
---------
@author: Administrator
"""

import autoads
from autoads.items.member_item import MemberItem
from autoads.items.group_item import GroupItem
from autoads.log import log
from autoads.action_control import Action
from datetime import datetime
from autoads import tools
from autoads.config import config
import random
import codecs
import json
import os
from urllib.parse import urlparse
from autoads import ads_api
import threading
from autoads.request import Request


class MembersSpider(autoads.AirSpider):
    pipeline = None
    begin = 0

    def start_requests(self):

        self.pipeline = self._item_buffer._pipelines[0]

        # 使用了yield加载组数据
        group_template = GroupItem()
        groups = self.pipeline.load_items(group_template)

        # self.ads_ids = tools.get_ads_id(config.account_nums)  # 总共有多少个账户同时搜集

        request_dict = {}
        if not (hasattr(self,'ads_id') and self.ads_ids):
            self.ads_ids = tools.get_ads_id()

        for ads_id in self.ads_ids:
            try:
                if ads_id not in request_dict:
                    request_dict[ads_id] = []

                i = len(request_dict[ads_id])  # 计数用
                while i < int(self.config.groups_nums):
                    # 加载单条群组，加入到请求列表中
                    item = next(groups)  # 消费了一条就计数+1
                    self.begin += 1
                    dictobj = json.loads(item)
                    group: GroupItem = self.pipeline.dictToObj(dictobj, group_template)

                    # 如果当前group已经存在搜集好的成员文件，就不再搜集了
                    if os.path.exists(self.config.members_table + tools.make_safe_filename(group.group_name) + '.txt'):
                        continue

                    # 当群组第一次被搜集到，状态是未知，此时就可以随便分配一个ads_id去处理
                    # 当群组中状态是public，也是可以随便哪个去处理
                    # 当群组中状态是apply-join,说明是申请通过的群组，只能由这条记录的ads_id来处理
                    if group.status == 'apply-join':
                        if group.ads_id not in request_dict:
                            request_dict[group.ads_id] = []
                        group.priority = len(request_dict[group.ads_id]) * 10
                        request_dict[group.ads_id].append(group)
                    else:
                        group.priority = (i + 1) * 10
                        request_dict[ads_id].append(group)

                    i += 1
            except StopIteration:  # yield 触发了异常，说明已经没有内容了，就不再放到容器中了
                break

        count = 0
        while request_dict:
            ads_id, groups = request_dict.popitem()
            for group in groups:
                # log.info(group)
                count += 1

                if group.group_link.endswith('/'):
                    url = group.group_link + 'members'
                else:
                    url = group.group_link + '/members'

                log.info(f'{count}-->{url}-->{ads_id}')

                yield autoads.Request(url=url, ads_id=ads_id, index=0, priority=group.priority, group=group,
                                      driver_count=len(self.ads_ids),stop_event=self.stop_event)

    def parse(self, request, response):
        browser = response.browser
        log.info(
            f'线程{threading.current_thread().name}中浏览器{request.ads_id}请求地址比对:{urlparse(browser.current_url).path},{urlparse(request.url).path}')
        if urlparse(browser.current_url).path == urlparse(request.url).path:
            group: GroupItem = request.group
            # 当前群组记录保持的位置，在更新群的时候就需要指定更新的文件物理地址
            group_table = self.config.groups_table + tools.make_safe_filename(group.word) + '.txt'
            group.__table_name__ = group_table

            group_status = group.status
            index = request.index
            member_table = self.config.members_table + tools.make_safe_filename(group.group_name) + '.txt'

            if group_status == 'unknown':
                admins = tools.get_page_data_mutilxpath(browser,self.config.members_xpath_public_admin)
                log.info(
                    f'线程{threading.current_thread().name}中浏览器{request.ads_id}请求={request},group_status={group_status},len(admins)={len(admins)}')
                if len(admins) > 0:
                    group_status = 'public'
                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f"当前群组为公开群组，开始采集群成员")
                    # Clean links file path
                    clean_links_file = member_table.replace('.txt', '_links.txt')
                    # 保存获取到的管理员和版主信息
                    for i in range(len(admins)):
                        item = admins[i]
                        member_link = item.get_attribute('href')
                        insert_item = MemberItem()
                        insert_item.__table_name__ = member_table  # 每个群组里面的成员保存成一个文件，防止后续请求的时候一次加载的太多了数据
                        insert_item.member_name = item.text
                        insert_item.member_link = member_link
                        insert_item.role_type = 'admin'
                        insert_item.ads_id = request.ads_id
                        insert_item.group_link = group.group_link
                        insert_item.group_name = group.group_name
                        yield insert_item
                        # Also save clean link
                        tools.save_clean_link(clean_links_file, member_link)
                    group.status = group_status  # 更新group状态为join
                    request.index = len(admins)
                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f"此群组共{len(admins)}位管理员")
                    log.info(
                        f'线程{threading.current_thread().name}中浏览器{request.ads_id}请求={request},更新后group_status={group_status}')

                    yield group.to_UpdateItem()
                else:
                    group_status = 'apply'
                    # 第一次做申请加入群组
                    # self.apply(browser, group)
                    group.last_apply_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    group.apply_nums = int(group.apply_nums) + 1
                    group.status = group_status
                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f"当前群组为非公开群组,正在验证是否已加入？")
                    log.info(
                        f'线程{threading.current_thread().name}中浏览器{request.ads_id}请求={request},更新后group_status={group_status}')
                    yield group.to_UpdateItem()  # 传递给线程去更新

                    # 立即去处理请求，有可能是上次就已经申请通过了
                    request.request_sync = True
                    yield request

            elif group_status == 'public' or group_status == 'apply-join':
                member_link_page = tools.get_page_data_mutilxpath(browser,
                                                         self.config.members_xpath_public_user)

                items_count = len(member_link_page)

                log.debug(
                    f'线程{threading.current_thread().name}中浏览器{request.ads_id}请求={request},group_status={group_status},元素个数={items_count}，上一次个数={request.index}')

                member_link_page = member_link_page[index:]

                # Clean links file path (alongside JSON file)
                clean_links_file = member_table.replace('.txt', '_links.txt')
                
                for i in range(len(member_link_page)):
                    try:
                        item = member_link_page[i]
                        member_link = item.get_attribute('href')
                        
                        insert_item = MemberItem()
                        insert_item.__table_name__ = member_table
                        insert_item.member_name = item.text
                        insert_item.member_link = member_link
                        insert_item.role_type = 'user'
                        insert_item.ads_id = request.ads_id
                        insert_item.group_link = group.group_link
                        insert_item.group_name = group.group_name
                        yield insert_item
                        
                        # Also save clean link to separate file
                        tools.save_clean_link(clean_links_file, member_link)
                    except Exception as e:
                        log.exception(e)

                if items_count-index>0:
                    tools.send_message_to_ui(self.ms, self.ui, f'采集到[新{items_count-request.index}/总{items_count}]个成员')

                request.index = items_count
            else:
                # 检查是否通过，如果通过了，就直接抓成员数据
                member_link_page = tools.get_page_data_mutilxpath(browser,
                                                         self.config.members_xpath_apply_join_user)
                log.info(
                    f'线程{threading.current_thread().name}中浏览器{request.ads_id}请求={request},len(member_link_page)={len(member_link_page)}')
                if len(member_link_page):
                    admins = tools.get_page_data_mutilxpath(browser,
                                                   self.config.members_xpath_apply_join_admin)

                    log.info(
                        f'线程{threading.current_thread().name}中浏览器{request.ads_id}请求={request},group_status={group_status},len(admins)={len(admins)}')
                    if len(admins) > 0:
                        group_status = 'apply-join'
                        # Clean links file path
                        clean_links_file = member_table.replace('.txt', '_links.txt')
                        # 保存获取到的管理员和版主信息
                        for i in range(len(admins)):
                            item = admins[i]
                            member_link = item.get_attribute('href')
                            insert_item = MemberItem()
                            insert_item.__table_name__ = member_table
                            insert_item.member_name = item.text
                            insert_item.member_link = member_link
                            insert_item.role_type = 'admin'
                            insert_item.ads_id = request.ads_id
                            insert_item.group_link = group.group_link
                            insert_item.group_name = group.group_name
                            yield insert_item
                            # Also save clean link
                            tools.save_clean_link(clean_links_file, member_link)
                        group.status = group_status  # 更新group状态为apply-join
                        request.index = len(admins)
                        tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f"此非公开群组已加入，共采集到{len(admins)}位管理员")
                        log.info(
                            f'线程{threading.current_thread().name}中浏览器{request.ads_id}请求={request},更新后group_status={group_status}')
                        yield group.to_UpdateItem()
                else:
                    # 间隔3天申请一次群组，先判断最后一次申请时间距离当前时间是不是有超过3天
                    # 超过了就再申请一次，每个群组只申请3次，不通过就不再申请
                    log.info(
                        f'线程{threading.current_thread().name}中浏览器{request.ads_id}请求={request},group_status={group_status},group.apply_nums={group.apply_nums},group.last_apply_time={group.last_apply_time}')
                    if group.apply_nums < 3:
                        if group.last_apply_time:
                            last_apply_time = datetime.strptime(group.last_apply_time, "%Y-%m-%d %H:%M:%S")
                            now_time = datetime.now()
                            diff_seconds = (now_time - last_apply_time).total_seconds()
                        else:
                            diff_seconds = 3 * 24 * 60 * 60 + 10
                        if diff_seconds > 3 * 24 * 60 * 60:
                            # self.apply(browser, group)
                            group.last_apply_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            group.apply_nums = int(group.apply_nums) + 1
                            group.status = group_status
                            yield group.to_UpdateItem()  # 传递给线程去更新

                    # 这个分支说明当前请求群组是非公开群，就需要重新去获取一条群数据来处理
                    try:
                        is_get_group = False
                        group_template = GroupItem()
                        groups = self.pipeline.load_items(group_template, begin=self.begin)
                        while not is_get_group:
                            # 加载单条群组，加入到请求列表中
                            item = next(groups)
                            self.begin += 1
                            dictobj = json.loads(item)
                            group: GroupItem = self.pipeline.dictToObj(dictobj, group_template)

                            # 如果当前group已经存在搜集好的成员文件，就不再搜集了
                            if os.path.exists(
                                    self.config.members_table + tools.make_safe_filename(group.group_name) + '.txt'):
                                continue

                            # 当群组第一次被搜集到，状态是未知，此时就可以随便分配一个ads_id去处理
                            # 当群组中状态是public，也是可以随便哪个去处理
                            # 当群组中状态是apply-join,说明是申请通过的群组，只能由这条记录的ads_id来处理
                            if group.status == 'apply-join':
                                continue

                            if group.group_link.endswith('/'):
                                url = group.group_link + 'members'
                            else:
                                url = group.group_link + '/members'

                            is_get_group = True

                            tools.send_message_to_ui(ms=self.ms, ui=self.ui, message="非公开群组暂时放弃，获取下一个群组中...")

                            new_request = autoads.Request(url=url, ads_id=request.ads_id, index=0,
                                                          priority=request.priority,
                                                          group=group, finished_nums=request.finished_nums,
                                                          request_sync=True)

                            log.info(
                                f'线程{threading.current_thread().name}中浏览器{request.ads_id}请求={new_request}，重新获取立即处理的请求={new_request}')

                            yield new_request
                    except StopIteration:  # yield 触发了异常，说明已经没有内容了，就不再放到容器中了
                        pass

            if group_status == 'public' or group_status == 'apply-join':
                log.info(
                    f'线程{threading.current_thread().name}中浏览器{request.ads_id}请求={request},group_status={group_status}-->页面开始滚动')
                is_finished = Action(browser).scroll_until_loaded()
                # 先检查是不是有上一次或者之前没有正常关闭的消息对话框，如果有就先关闭掉
                closespan_pre = tools.get_page_data_mutilxpath(browser, self.config.greets_xpath_close_btn_row)
                if len(closespan_pre) > 0:
                    try:
                        # Use JavaScript click to avoid "element not interactable" error
                        browser.execute_script("arguments[0].click();", closespan_pre[-1])
                    except Exception as click_err:
                        log.warning(f'Failed to close dialog: {click_err}')
                    tools.delay_time(2)

                if not is_finished:
                    # 这个请求要马上去处理，不要放到请求队列中
                    request.request_sync = True

                    tools.delay_time(2)
                    yield request

                else:
                    # 考虑到页面中只有几个成员，一加载就不会滚动的情况，所以在这里重新获取一下保存
                    member_link_page = tools.get_page_data_mutilxpath(browser,self.config.members_xpath_public_user)

                    items_count = len(member_link_page)

                    log.debug(
                        f'线程{threading.current_thread().name}中浏览器{request.ads_id}请求={request},group_status={group_status},元素个数={items_count}，上一次个数={request.index}')

                    member_link_page = member_link_page[index:]

                    # Clean links file path
                    clean_links_file = member_table.replace('.txt', '_links.txt')
                    
                    for i in range(len(member_link_page)):
                        try:
                            item = member_link_page[i]
                            member_link = item.get_attribute('href')
                            insert_item = MemberItem()
                            insert_item.__table_name__ = member_table
                            insert_item.member_name = item.text
                            insert_item.member_link = member_link
                            insert_item.role_type = 'user'
                            insert_item.ads_id = request.ads_id
                            insert_item.group_link = group.group_link
                            insert_item.group_name = group.group_name
                            yield insert_item
                            # Also save clean link
                            tools.save_clean_link(clean_links_file, member_link)
                        except Exception as e:
                            log.exception(e)

                    if items_count - index > 0:
                        tools.send_message_to_ui(self.ms, self.ui,
                                                 f'采集到[新{items_count-request.index}/总{items_count}]个成员')

                    request.index = items_count

                    log.info(f'线程{threading.current_thread().name}中浏览器{request.ads_id}已经完成滚动！')
                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, message='群成员采集结束，页面停止滚动')
                    
                    # 自动删除已采集完成的群组 - Auto-delete the collected group
                    try:
                        group_files = os.listdir(tools.abspath(self.config.groups_table))
                        for gf in group_files:
                            if gf.endswith('.txt') and not gf.endswith('_links.txt'):
                                group_file_path = os.path.join(tools.abspath(self.config.groups_table), gf)
                                deleted = tools.delete_entry_from_file(group_file_path, 'group_link', group.group_link)
                                if deleted:
                                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, 
                                        message=f'群组 {group.group_name} 采集完成，已从列表中删除')
                                    log.info(f'Deleted group {group.group_link} from {group_file_path}')
                                    break
                    except Exception as e:
                        log.error(f'Error deleting group after collection: {e}')
                    
                    if request.finished_nums == self.config.groups_nums - 1:
                        log.info(f'线程{threading.current_thread().name}中浏览器{request.ads_id}已经全部处理完请求，准备关闭浏览器！')
                        # 已经全部处理完了，那么这个ads_id就必须要关掉了，但是线程不关闭，此线程就要去处理别的ads_id的请求
                        tools.delay_time(2)  # 暂停2秒
                        # 关闭当前浏览器,线程重新初始化
                        tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'共采集{self.config.groups_nums}个群，采集结束，关闭浏览器')
                        if Request.webdriver_pool:
                            Request.webdriver_pool.remove(request.ads_id)

                        new_ads_id = '######'  # 这里是随便给的一个id，作为标志而已
                        log.info(f'线程{threading.current_thread().name}正关闭已经完成的浏览器{request.ads_id}')
                        request.ads_id = new_ads_id  # 需要在线程中更新当前线程需要处理的ads_id,防止当前线程执行了一个就不执行了
                        request.response = None
                        request.is_drop = True  # 让程序丢弃掉这个请求，之所以还返回这个请求，是因为要告诉线程，让线程清空自己的状态，重新去获取新的
                        yield request

        else:
            # 通过判断是不是地址有跳转，如果是，说明这个账号有问题，就在列表中移除
            if urlparse(browser.current_url).path.find('checkpoint') > -1:
                ads_api.remove_expired_ads(request.ads_id)
                request.webdriver_pool.remove(request.ads_id)
                request.webdriver_pool.queue_expried_ads.append(request.ads_id)
                tools.send_message_to_ui(ms=self.ms, ui=self.ui, message='浏览器账号异常，尝试获取新的账号中...')
                new_ads_id = tools.get_single_ads(ignore=self.ads_ids)
                if new_ads_id:  # 当还有可以被分配的浏览器资源的时候，才会分配这个请求，如果没有，就不再分配了，这一类型的请求就只能放弃了
                    log.info(f'线程{threading.current_thread().name}正关闭异常浏览器{request.ads_id}，使用新的浏览器{new_ads_id}重新处理请求')
                    request.ads_id = new_ads_id  # 需要在线程中更新当前线程需要处理的ads_id,防止当前线程执行了一个就不执行了
                    request.request_sync = True
                    request.response = None
                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, message='尝试获取新的账号成功，正在切换新的账号')
                else:
                    request.ads_id = '######'  # 需要在线程中更新当前线程需要处理的ads_id,防止当前线程执行了一个就不执行了
                    request.response = None
                    request.is_drop = True  # 让程序丢弃掉这个请求，之所以还返回这个请求，是因为要告诉线程，让线程清空自己的状态，重新去获取新的
                    request.index = -1
                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, message='尝试获取新的账号失败，此群组不采集')
                    log.info(f'线程{threading.current_thread().name}正关闭异常浏览器{request.ads_id}，并丢弃此请求')

                yield request

    def apply(self, browser, group):
        # 申请加入小组，有以下几种情况
        # 1. 不会弹出回答问题对话框，直接就变成了取消申请

        # 有可能是因为这个群组是要加入的
        join_group_button = browser.find_elements('xpath',
                                                  '//div[@class="k4urcfbm"]//div[@role="button" and @tabindex="0" and .//span]')  # 加入小组按钮
        if len(join_group_button) > 0:
            join_group_button[0].click()
            print('点击了申请按钮')
            tools.delay_time(2)

            # 检查是不是有回答问题按钮存在，如果有，请点击
            # //div[contains(@class,"h676nmdw")]/div[@role="button"]

            answerbtns = browser.find_elements('xpath', '//div[contains(@class,"h676nmdw")]/div[@role="button"]')
            if len(answerbtns) > 0:
                answerbtns[0].click()
                print('点击了回答问题')
                tools.delay_time(2)

            # 检查是不是有弹出回答问题对话框
            dialogs = browser.find_elements('xpath', '//div[@role="dialog"]//label')
            if len(dialogs) > 0:
                print('弹出框了')
                for dialog in dialogs:
                    # 弹出申请dialog
                    apply_text = dialog.find_elements('xpath', './/textarea')
                    for item in apply_text:
                        item.location_once_scrolled_into_view
                        tools.delay_time(0.5)
                        apply_words = self.config.groups_apply_words
                        item.send_keys(random.choice(apply_words))  # 此处内容可以定制

                    radio_btns = dialog.find_elements('xpath', './/input[@type="radio"]')
                    if len(radio_btns) > 0:
                        radio = random.choice(radio_btns)
                        radio.location_once_scrolled_into_view
                        tools.delay_time(0.5)
                        radio.click()
                        tools.delay_time(0.5)

                    accept_checkbox = dialog.find_elements('xpath', './/input[@type="checkbox"]')  # 我同意小组规则
                    if len(accept_checkbox) > 0:
                        accept_checkbox[0].location_once_scrolled_into_view
                        accept_checkbox[0].click()  # is_displayed
                        tools.delay_time(0.5)

                submit_button = browser.find_elements('xpath',
                                                      '//div[@role="dialog"]//div[@class="h676nmdw"]/div[@role="button"]')

                if len(submit_button) > 0:
                    submit_button[0].click()
                    tools.delay_time(2)

            # 更新group的状态
            group.last_apply_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            group.apply_nums = int(group.apply_nums) + 1

    def pre_close(self):
        # 在程序要结束之前，把抓取到的群组信息，保存到用户自定义的文件中
        table = tools.abspath(self.config.members_table)
        # bak = tools.abspath(self.config.groups_bak)
        user = tools.abspath(self.config.members_user)

        unique_key = MemberItem().unique_key[0]
        print(unique_key)

        with codecs.open(table, 'r', encoding='utf-8') as fi, \
                codecs.open(user, 'w', encoding='utf-8') as fo:
            for line in fi:
                dictobj = json.loads(line)
                fo.write(dictobj[unique_key] + '\n')
        
        # 自动生成合并的成员文件 - Auto-create consolidated member file
        try:
            member_dir = tools.abspath(self.config.members_table)
            if os.path.isdir(member_dir):
                output_file = os.path.join(member_dir, 'all_members.txt')
                count = tools.create_consolidated_member_file(member_dir, output_file)
                if count > 0:
                    log.info(f'已自动生成合并成员文件: {output_file} (共 {count} 个成员)')
                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, 
                        message=f'已生成合并成员文件: all_members.txt (共 {count} 个成员)')
        except Exception as e:
            log.error(f'生成合并成员文件失败: {e}')


if __name__ == "__main__":
    ads_ids = tools.get_ads_id(config.account_nums)
    MembersSpider(thread_count=len(ads_ids), ads_ids=ads_ids, config=config).start()

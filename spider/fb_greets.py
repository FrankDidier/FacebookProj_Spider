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
from autoads.log import log
from autoads.action_control import Action
from datetime import datetime
from autoads import tools
from autoads.config import config
import codecs
import json
import os
import random
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from autoads.request import Request
from urllib.parse import urlparse
from autoads import ads_api
import threading


class GreetsSpider(autoads.AirSpider):
    pipeline = None

    def start_requests(self):

        self.pipeline = self._item_buffer._pipelines[0]
        member_template = MemberItem()
        members = self.pipeline.load_items(member_template)

        ads_ids = tools.get_ads_id()

        tools.send_message_to_ui(ms=self.ms, ui=self.ui,
                                 message=f'共{len(ads_ids)}个账户/同时开启{self._thread_count}个账号发私信/每账号发{self.config.members_nums}条私信')

        # 获取所有今天待处理的账号，作为缓存进行缓存起来，最好是保存起来，这样就算程序意外终止了，也可以防止重复发送
        request_dict = {}
        for ads_id in ads_ids:
            try:
                # 获取目录中，今天已经处理过的ads_id进行剔除
                # ads_id_path = self.config.members_finished + datetime.now().strftime(
                #     "%Y-%m-%d") + '/' + ads_id + '.txt'
                # if os.path.exists(ads_id_path):
                #     continue

                # 初始化当前ads_id容器
                if ads_id not in request_dict:
                    request_dict[ads_id] = []

                # 加载每天每个浏览器可以发送多少个私信请求,就循环多少次，并添加成员请求
                for i in range(int(self.config.members_nums)):
                    item = next(members)
                    dictobj = json.loads(item)
                    member: MemberItem = self.pipeline.dictToObj(dictobj, member_template)

                    while member.status!='init':
                        item = next(members)
                        dictobj = json.loads(item)
                        member: MemberItem = self.pipeline.dictToObj(dictobj, member_template)

                    member.priority = (i + 1) * 5
                    request_dict[ads_id].append(member)
            except StopIteration:
                break

        count = 0

        log.info(request_dict)

        while request_dict:
            ads_id, members = request_dict.popitem()
            for member in members:
                # log.info(group)
                count += 1
                url = member.member_link
                log.info(f'{count}-->{url}-->{ads_id}')

                yield autoads.Request(url=url, ads_id=ads_id, index=0, priority=member.priority, member=member,
                                      driver_count=tools.get_greet_threading_count(config_from_newest=self.config),
                                      stop_event=self.stop_event)

    def parse(self, request, response):
        browser = response.browser

        log.info(
            f'线程{threading.current_thread().name}中浏览器{request.ads_id}请求地址比对:{urlparse(browser.current_url).path},{urlparse(request.url).path}')

        if urlparse(browser.current_url).path == urlparse(request.url).path:
            index = request.index
            # 点击发消息按钮
            sendbtn = tools.get_page_data_mutilxpath(browser, self.config.greets_xpath_send_btn)

            if len(sendbtn) > 0:
                log.info(f'线程{threading.current_thread().name}中浏览器{request.ads_id}点击发消息按钮')

                # 先检查是不是有上一次或者之前没有正常关闭的消息对话框，如果有就先关闭掉
                try:
                    closespan_pre = tools.get_page_data_mutilxpath(browser, self.config.greets_xpath_close_btn_row)
                    if len(closespan_pre) > 0:
                        log.info(f'线程{threading.current_thread().name}中浏览器{request.ads_id}检查到有消息没有正常结束，准备关闭')
                        tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'检查到有消息没有正常结束，准备关闭...')
                        closespan_pre[-1].click()
                        tools.delay_time(2)
                except Exception as e:
                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'检查到有消息没有正常结束，准备关闭 | 关闭异常')
                    log.error(e)

                # sendbtn[0].click()
                try:
                    # 重新获取一次，防止异常的页面刷新而找不到元素
                    sendbtn = tools.get_page_data_mutilxpath(browser, self.config.greets_xpath_send_btn)
                    log.info(f'线程{threading.current_thread().name}中浏览器{request.ads_id}点击发送消息按钮，等待页面加载消息对话框...')
                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'点击发送消息按钮，等待页面加载消息对话框...')
                    browser.execute_script("arguments[0].click();", sendbtn[0])
                    tools.delay_time(2)
                except Exception as e:
                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'点击发送消息按钮等待页面加载消息对话框 | 打开异常')
                    log.error(e)

                # 等待输入框的出现，不然就有可能是卡死了，我们等待8秒,每0.5秒会去看一下是不是已经出现了
                try:
                    xpath_content=self.config.greets_xpath_mwchat_textbox[0]
                    WebDriverWait(browser, 8).until(EC.visibility_of_element_located(
                        ('xpath', xpath_content)))
                except Exception as e:
                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'[{xpath_content}] | 访问异常')
                    log.error(e)

                # 判断是否有图片需要上传，如果有，先上传图片
                pics, text = (self.config.members_images, random.choice(self.config.members_texts))
                log.info(f'线程{threading.current_thread().name}中浏览器{request.ads_id}图片-->{pics}|文本-->{text}')

                tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'正在发私信，内容[{text}],图片{pics}')

                if len(pics) > 0 or text:
                    if len(pics) > 0:
                        try:
                            # 尝试多种方式上传图片
                            # Try multiple ways to upload images
                            filebtns = tools.get_page_data_mutilxpath(browser, self.config.greets_xpath_mwchat_file)
                            
                            if len(filebtns) == 0:
                                # 尝试点击添加图片按钮来触发文件选择
                                add_photo_btn = browser.find_elements('xpath', 
                                    "//div[@aria-label='Attach a photo or video' or @aria-label='添加照片或视频' or @aria-label='附加照片或影片']")
                                if add_photo_btn:
                                    add_photo_btn[0].click()
                                    tools.delay_time(1)
                                    filebtns = tools.get_page_data_mutilxpath(browser, self.config.greets_xpath_mwchat_file)
                            
                            if len(filebtns) > 0:
                                for pic in pics:
                                    # 确保图片路径是绝对路径
                                    pic_path = os.path.abspath(pic) if not os.path.isabs(pic) else pic
                                    if os.path.exists(pic_path):
                                        log.info(f'线程{threading.current_thread().name}中浏览器{request.ads_id}上传图片-->{pic_path}')
                                        filebtns[0].send_keys(pic_path)
                                        tools.delay_time(3)  # 等待图片上传完成
                                        tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'图片上传成功: {pic}')
                                    else:
                                        log.warning(f'图片文件不存在: {pic_path}')
                                        tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'图片文件不存在: {pic}')
                            else:
                                log.warning(f'未找到文件上传控件')
                                tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'未找到图片上传按钮')
                        except Exception as e:
                            tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'上传图片 | 异常: {str(e)}')
                            log.error(e)
                    try:
                        textbox = tools.get_page_data_mutilxpath(browser, self.config.greets_xpath_mwchat_textbox)
                        tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'获取到页面中的文本输入框个数={len(textbox)}')
                        if len(textbox) > 0:
                            if text:
                                # 随机选择一条文案，进行输入
                                textbox[0].click()
                                tools.delay_time(0.5)
                                log.info(f'线程{threading.current_thread().name}中浏览器{request.ads_id}输入文本：{text}')
                                tools.send_message_to_ui(ms=self.ms, ui=self.ui,
                                                         message=f'输入文本={text}')
                                textbox[0].send_keys(text)
                                tools.delay_time(1)
                            log.info(f'线程{threading.current_thread().name}中浏览器{request.ads_id}回车提交')
                            textbox[0].send_keys(Keys.ENTER)
                            tools.delay_time(2)

                            # 直接更新这条记录status=send
                            member: MemberItem = request.member
                            member_file = self.config.members_table + tools.make_safe_filename(
                                member.group_name) + '.txt'
                            member.__table_name__ = member_file
                            member.status = 'send'
                            yield member.to_UpdateItem()
                            
                            # 自动删除已发送的条目，避免重复发送
                            # Auto-delete the sent entry to prevent duplicate sending
                            tools.delete_entry_from_file(member_file, 'member_link', member.member_link)

                            tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'私信发送成功！已从列表中删除')
                            tools.delay_time(3)

                            # //div[@data-testid="mwchat-tab"]/div[contains(@class,"pfnyh3mw")]/div/span  关闭
                            closespan = tools.get_page_data_mutilxpath(browser, self.config.greets_xpath_close_btn_row)
                            if len(closespan) > 0:
                                closespan[-1].click()
                                tools.delay_time(2)

                            if request.finished_nums == self.config.members_nums - 1 and int(index) == 0:
                                # 回到主页，慢慢滚动
                                tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'当前账号私信发送完成，正在回到主页，活跃账号！')
                                yield autoads.Request(url=self.config.main_first_page, index=-1, ads_id=request.ads_id,
                                                      request_sync=True)
                                tools.delay_time(2)
                    except Exception as e:
                        tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'输入文字私信 | 异常')
                        log.error(e)
            else:
                log.info(
                    f'线程{threading.current_thread().name}中浏览器{request.ads_id}处理的请求{request.url}页面中没有发消息按钮，不发送消息，保存已处理记录')
                # self.abandom_request(request)
                if hasattr(request, 'member') and request.member:
                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'此成员不能发消息，放弃发送！')
                    member: MemberItem = request.member
                    member_file = self.config.members_table + tools.make_safe_filename(
                        member.group_name) + '.txt'
                    member.__table_name__ = member_file
                    member.status = 'send'
                    yield member.to_UpdateItem()
                    
                    # 自动删除不能发消息的成员，避免重复处理
                    # Auto-delete members who can't receive messages
                    tools.delete_entry_from_file(member_file, 'member_link', member.member_link)

                    # member.table_name = self.config.members_finished + datetime.now().strftime(
                    #     "%Y-%m-%d") + '/' + request.ads_id + '.txt'
                    # member.unique_key.append('group_link')
                    # yield member

                if request.finished_nums == self.config.members_nums - 1 and int(request.index) == 0:
                    # 回到主页，慢慢滚动
                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'当前账号私信发送完成，正在回到主页，活跃账号！')
                    yield autoads.Request(url=self.config.main_first_page, index=-1, ads_id=request.ads_id,
                                          request_sync=True)
                    tools.delay_time(2)

            if int(index) == -1:
                log.info(f'线程{threading.current_thread().name}中浏览器{request.ads_id}已经完成滚动，准备关闭了！')
                # 已经全部处理完了，那么这个ads_id就必须要关掉了，但是线程不关闭，此线程就要去处理别的ads_id的请求
                Action(browser).scroll()
                tools.delay_time(2)  # 暂停2秒
                # 关闭当前浏览器,线程重新初始化
                if Request.webdriver_pool:
                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'当前账号活跃完成，账号关闭！')
                    Request.webdriver_pool.remove(request.ads_id)

                log.info(f'线程{threading.current_thread().name}中浏览器{request.ads_id}已经处理完了，正在删除已经发送过的请求')
                # self.pre_close(request.ads_id)  # 删除已经发送过的请求

        else:
            # 说明页面发生了跳转，如果是跳转到了checkpoint页面，说明异常了，如果是跳转到其他页面，有可能这个页面只是服务商而已
            # 通过判断是不是地址有跳转，如果是，说明这个账号有问题，就在列表中移除
            if urlparse(browser.current_url).path.find('checkpoint') > -1:
                tools.send_message_to_ui(ms=self.ms, ui=self.ui, message='浏览器账号异常，关闭账号')
                ads_api.remove_expired_ads(request.ads_id)
                request.webdriver_pool.remove(request.ads_id)
                request.webdriver_pool.queue_expried_ads.append(request.ads_id)
                new_ads_id = '######'  # 这里是随便给的一个id，作为标志而已
                log.info(f'线程{threading.current_thread().name}正关闭异常浏览器{request.ads_id}，并丢弃此请求')
                request.ads_id = new_ads_id  # 需要在线程中更新当前线程需要处理的ads_id,防止当前线程执行了一个就不执行了
                request.response = None
                request.is_drop = True  # 让程序丢弃掉这个请求，之所以还返回这个请求，是因为要告诉线程，让线程清空自己的状态，重新去获取新的
                yield request
            else:
                log.info(
                    f'线程{threading.current_thread().name}中浏览器{request.ads_id}处理的请求{request.url}发生了跳转，有可能是服务商，不发送消息，保存已处理记录')
                if hasattr(request, 'member') and request.member:
                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'此成员有可能是服务商，不能发消息，放弃发送！')
                    member: MemberItem = request.member
                    member_file = self.config.members_table + tools.make_safe_filename(
                        member.group_name) + '.txt'
                    member.__table_name__ = member_file
                    member.status = 'send'
                    yield member.to_UpdateItem()
                    
                    # 自动删除无效成员
                    tools.delete_entry_from_file(member_file, 'member_link', member.member_link)

                if request.finished_nums == self.config.members_nums - 1 and int(request.index) == 0:
                    # 回到主页，慢慢滚动
                    tools.send_message_to_ui(ms=self.ms, ui=self.ui, message=f'当前账号私信发送完成，正在回到主页，活跃账号！')
                    yield autoads.Request(url=self.config.main_first_page, index=-1, ads_id=request.ads_id,
                                          request_sync=True)
                    tools.delay_time(2)

    def abandom_request(self, request):
        # 这条请求不发私信
        # 更新前端状态和保存处理记录，文件名按照天保存，方便结束的时候更新members文件
        log.info(f'线程{threading.current_thread().name}中浏览器{request.ads_id}处理的请求{request.url}保存处理记录{request.member}')
        if request.member:
            member: MemberItem = request.member
            member.__table_name__ = self.config.members_table + tools.make_safe_filename(member.group_name) + '.txt'
            member.status = 'send'
            yield member.to_UpdateItem()

            # member.table_name = self.config.members_finished + datetime.now().strftime(
            #     "%Y-%m-%d") + '/' + request.ads_id + '.txt'
            # yield member

        if request.finished_nums == self.config.members_nums - 1 and int(request.index) == 0:
            # 回到主页，慢慢滚动
            yield autoads.Request(url=self.config.main_first_page, index=-1, ads_id=request.ads_id,
                                  request_sync=True)
            tools.delay_time(2)

    def pre_close(self, ads_id):
        # 在所有页面全部要关闭之前，把今天处理好了的记录在主要文件中删掉
        finished_table = tools.abspath(self.config.members_finished + datetime.now().strftime(
            "%Y-%m-%d") + '/' + ads_id + '.txt')
        if os.path.exists(finished_table):

            member_template = MemberItem()
            unique_key = member_template.unique_key[0]
            member_dict = {}
            with codecs.open(finished_table, 'r', encoding='utf-8') as fq:
                # 根据每一行的group_name,组织成{group_name:[unique_key,]}
                for line in fq:
                    dictobj = json.loads(line)
                    member: MemberItem = self.pipeline.dictToObj(dictobj, member_template)

                    if member.group_name in member_dict:
                        member_dict[member.group_name].append(member.member_link)
                    else:
                        member_dict[member.group_name] = [member.member_link]

            # 根据已经处理好的当天的当个浏览器的member数据来删除之前的文件中的内容 考虑到当前文件中的记录有可能分配到不同的文件中，所以按照文件来分组来删除
            while member_dict:
                # 加载今天的多行数据中的unique_key字段，这个字段是在item中设置的，作为唯一的查询条件
                group_name, keys = member_dict.popitem()

                table = self.config.members_table + tools.make_safe_filename(group_name) + '.txt'

                split_index = table.rfind('.')
                new_table = tools.abspath(table[:split_index] + '_temp' + table[split_index:])
                table = tools.abspath(table)

                with codecs.open(table, 'r', encoding='utf-8') as fi, \
                        codecs.open(new_table, 'w', encoding='utf-8') as fo:
                    # 把原来表中的数据，一行一行写入新的临时文件中，碰到今天已经处理过的数据，就直接不写入，这样达到删除的效果
                    for line in fi:
                        dictobj = json.loads(line)
                        if dictobj[unique_key] in keys:
                            continue
                        else:
                            fo.write(line)

                # 通过删除原来的文件，再把新的临时表更改名称为原来的文件名
                os.remove(table)  # remove original
                os.rename(new_table, table)  # rename temp to original name
            # 删除掉已经更新过的记录
            # os.remove(finished_table)


if __name__ == "__main__":
    GreetsSpider(thread_count=tools.get_greet_threading_count(), config=config).start()

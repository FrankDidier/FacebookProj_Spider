# -*- coding: utf-8 -*-

import importlib
import threading
from queue import Queue

import autoads.tools as tools
from autoads.dedup import Dedup
from autoads.item import Item, UpdateItem
from autoads.log import log
from autoads.pipelines import BasePipeline

MAX_ITEM_COUNT = 5000  # 缓存中最大item数
UPLOAD_BATCH_MAX_SIZE = 1000


class ItemBuffer(threading.Thread):
    dedup = None

    ITEM_PIPELINES = [
        # "autoads.pipelines.mysql_pipeline.MysqlPipeline",
        "autoads.pipelines.file_pipeline.FilePipeline",
    ]

    def __init__(self, stop_event=None):
        if not hasattr(self, "_table_item"):
            super(ItemBuffer, self).__init__()

            self._thread_stop = False
            self._is_adding_to_db = False
            self.stop_event = stop_event

            self._items_queue = Queue(maxsize=MAX_ITEM_COUNT)

            self._item_tables = {
                # 'item_name': 'table_name' # 缓存item名与表名对应关系
            }

            self._item_update_keys = {
                # 'table_name': ['id', 'name'...] # 缓存table_name与__update_key__的关系
            }

            self._item_unique_keys = {

            }

            self._pipelines = self.load_pipelines()

            self._mysql_pipeline = None

            # self._have_mysql_pipeline = MYSQL_PIPELINE_PATH in self.ITEM_PIPELINES

            if not self.__class__.dedup:
                self.__class__.dedup = Dedup(to_md5=False)

            # 导出重试的次数
            self.export_retry_times = 0
            # 导出失败的次数 TODO 非air爬虫使用redis统计
            self.export_falied_times = 0

    # @property
    # def mysql_pipeline(self):
    #     if not self._mysql_pipeline:
    #         module, class_name = MYSQL_PIPELINE_PATH.rsplit(".", 1)
    #         pipeline_cls = importlib.import_module(module).__getattribute__(class_name)
    #         self._mysql_pipeline = pipeline_cls()
    #
    #     return self._mysql_pipeline

    def load_pipelines(self):
        pipelines = []
        for pipeline_path in self.ITEM_PIPELINES:
            module, class_name = pipeline_path.rsplit(".", 1)
            pipeline_cls = importlib.import_module(module).__getattribute__(class_name)
            pipeline = pipeline_cls()
            if not isinstance(pipeline, BasePipeline):
                raise ValueError(f"{pipeline_path} 需继承 feapder.pipelines.BasePipeline")
            pipelines.append(pipeline)

        return pipelines

    def run(self):
        # print(f'self._started={self._started.is_set()}')
        self._thread_stop = False
        while not self._thread_stop:
            if self.stop_event and self.stop_event.isSet():
                log.info(f'界面中点击了停止按钮，正在清理临时数据库，并设置thread_stop=True')
                tools.clear_queue(self._items_queue)
                self._thread_stop=True
                break

            self.flush()
            tools.delay_time(1)


        self.close()

    def stop(self):
        self._thread_stop = True
        self._started.clear()

    def put_item(self, item):
        if isinstance(item, Item) and not (self.stop_event and self.stop_event.isSet()):
            self._items_queue.put(item)

    def flush(self):
        try:
            items = []
            update_items = []
            requests = []
            callbacks = []
            items_fingerprints = []
            data_count = 0

            while not self._items_queue.empty():
                data = self._items_queue.get_nowait()

                data_count += 1

                # data 分类
                if callable(data):
                    # log.info(f'callable true {data}')
                    callbacks.append(data)

                elif isinstance(data, UpdateItem):
                    update_items.append(data)

                elif isinstance(data, Item):
                    items.append(data)
                    items_fingerprints.append(data.fingerprint)

                else:  # request-redis
                    requests.append(data)

                # print(f'fingerprints-1:{len(items_fingerprints)}')

                if data_count >= UPLOAD_BATCH_MAX_SIZE:
                    self.__add_item_to_db(
                        items, update_items, requests, callbacks, items_fingerprints
                    )

                    items = []
                    update_items = []
                    requests = []
                    callbacks = []
                    items_fingerprints = []
                    data_count = 0

            if self.stop_event and self.stop_event.isSet():
                tools.clear_queue(self._items_queue)
                return

            if data_count:
                self.__add_item_to_db(
                    items, update_items, requests, callbacks, items_fingerprints
                )

        except Exception as e:
            log.exception(e)

    def get_items_count(self):
        return self._items_queue.qsize()

    def is_adding_to_db(self):
        return self._is_adding_to_db

    def __dedup_items(self, items, items_fingerprints):
        """
        去重
        @param items:
        @param items_fingerprints:
        @return: 返回去重后的items, items_fingerprints
        """
        # print(f'__dedup_items-->items_fingerprints:{len(items_fingerprints)}-->items:{len(items)}')

        if not items:
            return items, items_fingerprints

        _is_exists = self.__class__.dedup.get(items_fingerprints)
        # print(f'is_exists-->{len(_is_exists)}')
        _is_exists = _is_exists if isinstance(_is_exists, list) else [_is_exists]

        dedup_items = []
        dedup_items_fingerprints = []
        items_count = dedup_items_count = dup_items_count = 0
        # print(f'is_exists--># _is_exists}')
        while _is_exists:
            item = items.pop(0)
            items_fingerprint = items_fingerprints.pop(0)
            # print(f'is_exists-->{_is_exists}')
            is_exist = _is_exists.pop(0)

            items_count += 1

            if not is_exist:
                dedup_items.append(item)
                dedup_items_fingerprints.append(items_fingerprint)
                dedup_items_count += 1
            else:
                # print(f"重复的链接：{items_fingerprint}")
                dup_items_count += 1

        log.info(
            "待入库数据 {} 条， 重复 {} 条，实际待入库数据 {} 条".format(
                items_count, dup_items_count, dedup_items_count
            )
        )

        return dedup_items, dedup_items_fingerprints

    def __pick_items(self, items, is_update_item=False):
        """
        将每个表之间的数据分开 拆分后 原items为空
        @param items:
        @param is_update_item:
        @return:
        """
        datas_dict = {
            # 'table_name': [{}, {}]
        }

        while items:
            item = items.pop(0)
            # 取item下划线格式的名
            # 下划线类的名先从dict中取，没有则现取，然后存入dict。加快下次取的速度
            # item_name = item.item_name
            # table_name = self._item_tables.get(item_name)
            # 考虑到每个item都会有一个保存地址，所以就按照__table_name来做
            table_name=item.table_name
            log.info(f'待保存数据信息：table_name={table_name}')
            # if not table_name:
            #     table_name = item.table_name
            #     self._item_tables[item_name] = table_name

            if table_name not in datas_dict:
                datas_dict[table_name] = []

            datas_dict[table_name].append(item.to_dict)

            if is_update_item and table_name not in self._item_update_keys:
                self._item_update_keys[table_name] = item.update_key
                self._item_unique_keys[table_name] = item.unique_key
                # print(f'item.update_key-->{item.update_key}')

            log.info(f'此次共有{len(datas_dict.keys())}个文件待保存')

        return datas_dict

    def __export_to_db(self, table, datas, is_update=False, update_keys=(), unique_keys=()):

        for pipeline in self._pipelines:
            if is_update:
                # if table == self._task_table and not isinstance(
                #         pipeline, MysqlPipeline
                # ):
                #     continue

                if not pipeline.update_items(table, datas, update_keys=update_keys, unique_keys=unique_keys):
                    log.error(
                        f"{pipeline.__class__.__name__} 更新数据失败. table: {table}  items: {datas}"
                    )
                    return False

            else:
                if not pipeline.save_items(table, datas):
                    log.error(
                        f"{pipeline.__class__.__name__} 保存数据失败. table: {table}  items: {datas}"
                    )
                    return False

        # 若是任务表, 且上面的pipeline里没mysql，则需调用mysql更新任务
        # if not self._have_mysql_pipeline and is_update and table == self._task_table:
        #     if not self.mysql_pipeline.update_items(
        #             table, datas, update_keys=update_keys
        #     ):
        #         log.error(
        #             f"{self.mysql_pipeline.__class__.__name__} 更新数据失败. table: {table}  items: {datas}"
        #         )
        #         return False

        return True

    def __add_item_to_db(
            self, items, update_items, requests, callbacks, items_fingerprints
    ):
        export_success = True
        self._is_adding_to_db = True

        items, items_fingerprints = self.__dedup_items(items, items_fingerprints)

        # 分捡
        items_dict = self.__pick_items(items)
        update_items_dict = self.__pick_items(update_items, is_update_item=True)

        # item批量入库
        failed_items = {"add": [], "update": [], "requests": []}
        while items_dict:
            table, datas = items_dict.popitem()

            log.debug(
                """
                -------------- item 批量入库 --------------
                表名: %s
                datas: %s
                    """
                % (table, tools.dumps_json(datas, indent=16))
            )

            if not self.__export_to_db(table, datas):
                export_success = False
                failed_items["add"].append({"table": table, "datas": datas})

        # 执行批量update
        while update_items_dict:
            table, datas = update_items_dict.popitem()

            log.debug(
                """
                -------------- item 批量更新 --------------
                表名: %s
                datas: %s
                    """
                % (table, tools.dumps_json(datas, indent=16))
            )

            update_keys = self._item_update_keys.get(table)
            unique_keys = self._item_unique_keys.get(table)
            # print(f'unique_keys-->{unique_keys}')
            if not self.__export_to_db(
                    table, datas, is_update=True, update_keys=update_keys,unique_keys=unique_keys
            ):
                export_success = False
                failed_items["update"].append({"table": table, "datas": datas})

        if export_success:
            # 执行回调
            while callbacks:
                try:
                    callback = callbacks.pop(0)
                    callback()
                except Exception as e:
                    log.exception(e)

            # 去重入库
            if items_fingerprints:
                self.__class__.dedup.add(items_fingerprints, skip_check=True)

        self._is_adding_to_db = False

    def close(self):
        # 调用pipeline的close方法
        for pipeline in self._pipelines:
            try:
                pipeline.close()
            except Exception as e:
                raise e
                # pass

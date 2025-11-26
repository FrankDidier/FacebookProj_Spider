# -*- coding: utf-8 -*-
"""
Created on 2021/3/18 12:39 上午
---------
@summary:
---------
@author: Boris
@email: boris_liu@foxmail.com
"""

from autoads.pipelines import BasePipeline
from typing import Dict, List, Tuple
import json
from autoads.item import Item
import copy
import codecs
import os
import glob
from autoads import tools


class FilePipeline(BasePipeline):
    """
    pipeline 是单线程的，批量保存数据的操作，不建议在这里写网络请求代码，如下载图片等
    """

    def save_items(self, table, items: List[Dict]) -> bool:
        """
        保存数据
        Args:
            table: 表名
            items: 数据，[{},{},...]

        Returns: 是否保存成功 True / False
                 若False，不会将本批数据入到去重库，以便再次入库

        """

        file_dir = os.path.split(table)[0]

        # 判断文件路径是否存在，如果不存在，则创建，此处是创建多级目录
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)

        with open(table, 'a+', encoding='utf8', newline='\n') as f:
            f.writelines([json.dumps(x, ensure_ascii=False) + '\n' for x in items])
            # byte_len = f.write(json.dumps(items, ensure_ascii=False, indent=1))
            return True

    def update_items(self, table, items: List[Dict], update_keys=Tuple, unique_keys=Tuple) -> bool:
        """
        更新数据
        Args:
            table: 表名
            items: 数据，[{},{},...]
            update_keys: 更新的字段, 如 ("title", "publish_time")
            unique_keys: 查找行数据的匹配条件

        Returns: 是否更新成功 True / False
                 若False，不会将本批数据入到去重库，以便再次入库

        """

        # print(items)
        # print(update_keys)

        split_index = table.rfind('.')
        new_table = tools.abspath(table[:split_index] + '_temp' + table[split_index:])
        table = tools.abspath(table)

        # print(new_table)

        unique_key = unique_keys[0]

        # print(unique_key)

        keys = [item[unique_key] for item in items]

        with codecs.open(table, 'r', encoding='utf-8') as fi, \
                codecs.open(new_table, 'w', encoding='utf-8') as fo:

            for line in fi:
                dictobj = json.loads(line)
                if dictobj[unique_key] in keys:
                    item = items[keys.index(dictobj[unique_key])]
                    # print(item)
                    for uk in update_keys:
                        dictobj[uk] = item[uk]

                    # print(dictobj)
                    fo.write(json.dumps(dictobj, ensure_ascii=False) + '\n')
                else:
                    fo.write(line)

        os.remove(table)  # remove original
        os.rename(new_table, table)  # rename temp to original name

        return True

    def dictToObj(self, dictObj, item: Item):
        if not isinstance(dictObj, dict):
            return dictObj
        item = copy.copy(item)
        for k, v in dictObj.items():
            item[k] = self.dictToObj(v, item)
        return item

    def load_items(self, item: Item, begin=0):
        """
        加载数据，按照一行一行的规则给到浏览器去发请求
        :return:
        """
        table = tools.abspath(item.table_name)  # 这里只是一个目录，我们需要把目录中的文件都要过滤一遍来获取到请求
        files = glob.glob(table + '\*.txt')
        index = 1
        for table in files:
            with open(table, encoding="utf-8") as f:
                while True:
                    content = f.readline()
                    if not content:
                        break
                    if index > begin:
                        yield content  # 消费一条

                    index += 1

    def close(self):
        if callable(self.__pre_close__):
            self.__pre_close__()

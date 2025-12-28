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
from autoads.log import log


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
        from autoads.config import config
        
        # Check if we should only save links (not JSON) for member files
        is_member_file = 'member' in table.lower()
        is_group_file = 'group' in table.lower() and 'member' not in table.lower()
        
        members_save_links_only = getattr(config, 'members_save_links_only', False)
        groups_save_links_only = getattr(config, 'groups_save_links_only', False)
        
        if is_member_file and members_save_links_only:
            # Skip saving JSON format - links are saved separately by spider
            log.debug(f"Skipping JSON save for {table} (members_save_links_only=true)")
            return True
        
        if is_group_file and groups_save_links_only:
            # Skip saving JSON format for groups - links are saved separately
            log.debug(f"Skipping JSON save for {table} (groups_save_links_only=true)")
            return True

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
        try:
            split_index = table.rfind('.')
            new_table = tools.abspath(table[:split_index] + '_temp' + table[split_index:])
            table = tools.abspath(table)

            if not os.path.exists(table):
                log.warning(f"Table file not found: {table}")
                return True  # Return True to not block pipeline

            unique_key = unique_keys[0] if unique_keys else 'member_link'
            keys = [item.get(unique_key, '') for item in items]
            
            # Also collect member_link URLs for plain URL file handling
            member_links = [item.get('member_link', '') for item in items]

            is_links_file = '_links.txt' in table or table.endswith('_links.txt')

            # Retry logic for file locking issues
            import time
            import threading
            max_retries = 3
            retry_delay = 0.5
            thread_id = threading.current_thread().ident or 0
            new_table = table + f'.temp_{thread_id}'
            
            for attempt in range(max_retries):
                try:
                    with codecs.open(table, 'r', encoding='utf-8') as fi, \
                            codecs.open(new_table, 'w', encoding='utf-8') as fo:

                        for line in fi:
                            line_stripped = line.strip()
                            if not line_stripped:
                                continue
                            
                            # Try JSON parsing first
                            try:
                                dictobj = json.loads(line_stripped)
                                if dictobj.get(unique_key) in keys:
                                    item = items[keys.index(dictobj[unique_key])]
                                    for uk in update_keys:
                                        dictobj[uk] = item.get(uk, dictobj.get(uk))
                                    fo.write(json.dumps(dictobj, ensure_ascii=False) + '\n')
                                else:
                                    fo.write(line)
                            except json.JSONDecodeError:
                                # Plain URL file - check if this URL should be deleted
                                if is_links_file:
                                    # For _links.txt files, delete processed entries
                                    if line_stripped in member_links:
                                        log.debug(f"Removing processed URL from links file: {line_stripped}")
                                        continue  # Skip writing this line (delete it)
                                fo.write(line)

                    # Atomic file replacement
                    try:
                        os.replace(new_table, table)
                    except PermissionError:
                        os.remove(table)
                        os.rename(new_table, table)
                    break  # Success, exit retry loop
                except PermissionError:
                    if attempt < max_retries - 1:
                        log.warning(f"File locked, retry {attempt + 1}/{max_retries}: {table}")
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                    raise  # Re-raise after all retries

            return True
        except Exception as e:
            log.error(f"Error in update_items for {table}: {e}")
            # Clean up temp file if it exists
            if 'new_table' in locals() and os.path.exists(new_table):
                try:
                    os.remove(new_table)
                except:
                    pass
            return True  # Return True to not block pipeline

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
        all_files = glob.glob(table + '/*.txt') + glob.glob(table + '\\*.txt')
        
        # Separate JSON files and links files
        json_files = [f for f in all_files if not f.endswith('_links.txt')]
        links_files = [f for f in all_files if f.endswith('_links.txt')]
        
        # Prefer JSON files, fallback to links files if no JSON exists
        files = json_files if json_files else links_files
        
        if not files:
            log.warning(f"No files found in {table}")
            return
        
        if not json_files and links_files:
            log.warning(f"⚠️ 只找到 _links.txt 文件，没有JSON文件。建议将 groups_save_links_only 设为 false")
            log.warning(f"⚠️ Only found _links.txt files, no JSON files. Set groups_save_links_only=false")
        
        index = 1
        for file_path in files:
            is_links_file = file_path.endswith('_links.txt')
            with open(file_path, encoding="utf-8") as f:
                while True:
                    content = f.readline()
                    if not content:
                        break
                    if index > begin:
                        # For links files, convert plain URL to minimal JSON format
                        if is_links_file:
                            url = content.strip()
                            if url:
                                # Create minimal group item JSON from URL
                                import json as json_mod
                                content = json_mod.dumps({
                                    "group_link": url,
                                    "group_name": url.split('/')[-2] if '/groups/' in url else url,
                                    "word": "",
                                    "status": "unknown"
                                }) + "\n"
                        yield content  # 消费一条
                    index += 1

    def load_items_from_file(self, item: Item, file_path, begin=0):
        """
        从指定的文件加载数据
        Load items from a specific file
        :param item: Item template
        :param file_path: Path to the file to load
        :param begin: Starting index
        :return: Generator of file lines
        """
        file_path = tools.abspath(file_path)
        if not os.path.exists(file_path):
            log.warning(f'File not found: {file_path}')
            return
        
        index = 1
        with open(file_path, encoding="utf-8") as f:
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

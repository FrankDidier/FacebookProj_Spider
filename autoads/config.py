import configparser
import os.path
import json


class Config(object):
    def __init__(self):
        # self.config_path = os.path.dirname(os.path.abspath('.')) + '\config.ini'  # 返回上级目录再访问某文件（路径根据实际情况自定义）
        # Open a configuration file
        self.__name = None
        self.__config = None
        self.lang = {'请选择': '', '英语': 'en', '阿拉伯语': 'ar', '孟加拉语': 'bn-IN', '米沙鄢语': 'ceb-PH', '捷克语 ': 'cs-CZ',
                     '德语 ': 'de-DE', '希腊语': 'el-GR', '西班牙文': 'es', '芬兰语': 'fi-FI', '菲律宾语': 'fil-PH', '法语': 'fr',
                     '希伯来文e': 'he-IL', '印地语': 'hi-IN', '匈牙利文': 'hu-HU', '印度尼西亚语': 'id-ID', '意大利文': 'it-IT',
                     '日文': 'ja-JP', '爪哇语': 'jv-ID', '柬埔寨语': 'km-KH', '韩语': 'ko-KR', '马来语': 'ms-MY', '缅甸语': 'my-MM',
                     '荷兰语': 'nl-NL', '波兰语': 'pl-PL', '印欧语': 'pt-BR', '罗马尼亚语': 'ro-RO', '俄语': 'ru-RU', '瑞典语': 'sv-SE',
                     '泰语': 'th-TH', '土耳其语': 'tr-TR', '乌克兰语': 'uk-UA', '乌尔都语': 'ur', '越南语': 'vi-VN', '简体中文': 'zh-Hans',
                     '繁体中文': 'zh-Hant-TW'}
        self.target = {'全部': 'all', '推荐页': 'recommendation', '已关注页': 'following'}

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def config_path(self):
        return os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), self.name)

    @property
    def config(self):
        # log.info(self._name)
        if self.__config:
            return self.__config
        else:
            _config = configparser.ConfigParser()
            _config.read(self.config_path, encoding='utf-8')
            self.__config = _config
            return _config

    def add_section(self, section):
        if not self.config.has_section(section):
            self.config.add_section(section)
            self.config.write(open(self.config_path, mode='w', encoding='utf-8'))

    def set_option(self, section, option, value):
        self.add_section(section)
        self.config.set(section, option, value)

        self.config.write(open(self.config_path, mode='w', encoding='utf-8'))

    def remove_section(self, section):
        self.config.remove_section(section)
        self.config.write(open(self.config_path, mode='w', encoding='utf-8'))

    def remove_option(self, section, option):
        if self.config.has_section(section):
            self.config.remove_option(section, option)

        self.config.write(open(self.config_path, mode='w', encoding='utf-8'))

    def get_options(self, section):
        return self.config.options(section)

    def get_option(self, section, option):
        return self.config.get(section, option)

    def get_xpath(self, section, option):
        return json.loads(self.config.get(section, option))

    @property
    def members_user(self):
        return self.get_option('members', 'user')

    @property
    def members_finished(self):
        return self.get_option('members', 'finished')

    @property
    def members_table(self):
        return self.get_option('members', 'table')

    @property
    def members_bak(self):
        return self.get_option('members', 'bak')

    @property
    def members_texts(self):
        return json.loads(self.get_option('members', 'texts'))

    @property
    def members_images(self):
        return json.loads(self.get_option('members', 'images'))

    @property
    def members_xpath_public_admin(self):
        return json.loads(self.get_option('members', 'xpath_public_admin'))

    @property
    def members_xpath_public_user(self):
        return json.loads(self.get_option('members', 'xpath_public_user'))

    @property
    def members_xpath_apply_join_admin(self):
        return json.loads(self.get_option('members', 'xpath_apply_join_admin'))

    @property
    def members_xpath_apply_join_user(self):
        return json.loads(self.get_option('members', 'xpath_apply_join_user'))

    @property
    def groups_user(self):
        return self.get_option('groups', 'user')

    @property
    def groups_table(self):
        return self.get_option('groups', 'table')

    @property
    def groups_bak(self):
        return self.get_option('groups', 'bak')

    @property
    def groups_url(self):
        return self.get_option('groups', 'url')

    @property
    def groups_xpath_query(self):
        return json.loads(self.get_option('groups', 'xpath_query'))

    @property
    def groups_words(self):
        return json.loads(self.get_option('groups', 'words'))

    @property
    def groups_apply_words(self):
        return json.loads(self.get_option('groups', 'apply'))

    @property
    def groups_nums(self):
        return json.loads(self.get_option('main', 'group_nums'))

    @property
    def members_nums(self):
        return json.loads(self.get_option('main', 'members_nums'))

    @property
    def account_nums(self):
        return json.loads(self.get_option('main', 'account_nums'))

    @property
    def member_timeout(self):
        return json.loads(self.get_option('main', 'member_timeout'))

    @property
    def app_code(self):
        return self.get_option('main', 'app_code')

    @property
    def activator_service(self):
        return self.get_option('main', 'activator_service')

    @property
    def main_first_page(self):
        return self.get_option('main', 'first_page')

    @property
    def version(self):
        return self.get_option('main', 'version')

    @property
    def app_name(self):
        return self.get_option('main', 'app_name')

    @property
    def ads_service_url(self):
        return self.get_option('ads', 'ads_service')

    @property
    def ads_key(self):
        return self.get_option('ads', 'key')

    @property
    def service_app_path(self):
        return self.get_option('ads', 'service_app_path')
    
    @property
    def browser_type(self):
        try:
            return self.get_option('ads', 'browser_type')
        except:
            return 'adspower'  # Default to AdsPower
    
    @property
    def bitbrowser_port(self):
        try:
            return self.get_option('ads', 'bitbrowser_port')
        except:
            return '54345'  # Default BitBrowser port
    
    @property
    def bitbrowser_api_url(self):
        try:
            return self.get_option('ads', 'bitbrowser_api_url')
        except:
            port = self.bitbrowser_port
            return f'http://127.0.0.1:{port}'

    @property
    def keep_browser_open(self):
        """Keep browser open after collection stops"""
        try:
            return self.get_option('ads', 'keep_browser_open').lower() == 'true'
        except:
            return True  # Default: keep browser open

    @property
    def max_scroll_count(self):
        """Maximum scroll count for data collection"""
        try:
            return int(self.get_option('main', 'max_scroll_count'))
        except:
            return 10  # Default: 10 scrolls

    @property
    def max_thread_count(self):
        """Maximum thread count for concurrent operations"""
        try:
            return int(self.get_option('main', 'max_thread_count'))
        except:
            return 2  # Default: 2 threads

    # IP Pool properties
    @property
    def ip_pool_enabled(self):
        try:
            return self.get_option('ip_pool', 'enabled').lower() == 'true'
        except:
            return False
    
    @property
    def ip_pool_proxy_type(self):
        try:
            return self.get_option('ip_pool', 'proxy_type')
        except:
            return 'http'
    
    @property
    def ip_pool_proxies(self):
        try:
            return json.loads(self.get_option('ip_pool', 'proxies'))
        except:
            return []
    
    @property
    def ip_pool_assignment_mode(self):
        try:
            return self.get_option('ip_pool', 'assignment_mode')
        except:
            return 'round_robin'
    
    @property
    def ip_pool_rotate_after_requests(self):
        try:
            return int(self.get_option('ip_pool', 'rotate_after_requests'))
        except:
            return 0
    
    @property
    def ip_pool_test_before_use(self):
        try:
            return self.get_option('ip_pool', 'test_before_use').lower() == 'true'
        except:
            return True
    
    @property
    def ip_pool_timeout(self):
        try:
            return int(self.get_option('ip_pool', 'timeout'))
        except:
            return 10

    @property
    def greets_xpath_send_btn(self):
        return json.loads(self.get_option('greets', 'xpath_send_btn'))

    @property
    def greets_xpath_close_btn_row(self):
        return json.loads(self.get_option('greets', 'xpath_close_btn_row'))

    @property
    def greets_xpath_mwchat_textbox(self):
        return json.loads(self.get_option('greets', 'xpath_mwchat_textbox'))

    @property
    def greets_xpath_mwchat_file(self):
        return json.loads(self.get_option('greets', 'xpath_mwchat_file'))

    @property
    def contact_phone(self):
        return self.get_option('contact', 'telegram')

    @property
    def contact_email(self):
        return self.get_option('contact', 'email')

    # Posts configuration
    @property
    def posts_table(self):
        return self.get_option('posts', 'table')

    @property
    def post_groups_nums(self):
        return json.loads(self.get_option('posts', 'groups_nums'))

    @property
    def posts_xpath(self):
        return json.loads(self.get_option('posts', 'xpath_post'))

    # Pages configuration
    @property
    def pages_table(self):
        return self.get_option('pages', 'table')

    @property
    def page_keywords(self):
        return json.loads(self.get_option('pages', 'keywords'))

    @property
    def page_urls(self):
        return json.loads(self.get_option('pages', 'urls'))

    @property
    def pages_xpath(self):
        return json.loads(self.get_option('pages', 'xpath_page'))

    # Instagram configuration
    @property
    def ins_target_users(self):
        return json.loads(self.get_option('instagram', 'target_users'))

    @property
    def ins_reels_urls(self):
        return json.loads(self.get_option('instagram', 'reels_urls'))

    @property
    def ins_follower_table(self):
        return self.get_option('instagram', 'follower_table')

    @property
    def ins_following_table(self):
        return self.get_option('instagram', 'following_table')

    @property
    def ins_profile_table(self):
        return self.get_option('instagram', 'profile_table')

    @property
    def ins_reels_comment_table(self):
        return self.get_option('instagram', 'reels_comment_table')

    @property
    def ins_max_thread_count(self):
        try:
            return int(self.get_option('instagram', 'max_thread_count'))
        except:
            return 2

    @property
    def ins_max_scroll_count(self):
        try:
            return int(self.get_option('instagram', 'max_scroll_count'))
        except:
            return 5

    # Automation configuration
    @property
    def like_mode(self):
        try:
            return self.get_option('automation', 'like_mode')
        except:
            return 'all'

    @property
    def like_keywords(self):
        try:
            return json.loads(self.get_option('automation', 'like_keywords'))
        except:
            return []

    @property
    def like_groups(self):
        try:
            return json.loads(self.get_option('automation', 'like_groups'))
        except:
            return []

    @property
    def like_count(self):
        try:
            return int(self.get_option('automation', 'like_count'))
        except:
            return 10

    @property
    def like_interval(self):
        try:
            return int(self.get_option('automation', 'like_interval'))
        except:
            return 5

    @property
    def comment_mode(self):
        try:
            return self.get_option('automation', 'comment_mode')
        except:
            return 'keywords'

    @property
    def comment_keywords(self):
        try:
            return json.loads(self.get_option('automation', 'comment_keywords'))
        except:
            return []

    @property
    def comment_content(self):
        try:
            return json.loads(self.get_option('automation', 'comment_content'))
        except:
            return ["Nice post!", "Great content!"]

    @property
    def comment_count(self):
        try:
            return int(self.get_option('automation', 'comment_count'))
        except:
            return 5

    @property
    def comment_interval(self):
        try:
            return int(self.get_option('automation', 'comment_interval'))
        except:
            return 10

    @property
    def follow_mode(self):
        try:
            return self.get_option('automation', 'follow_mode')
        except:
            return 'fans'

    @property
    def follow_keywords(self):
        try:
            return json.loads(self.get_option('automation', 'follow_keywords'))
        except:
            return []

    @property
    def follow_count(self):
        try:
            return int(self.get_option('automation', 'follow_count'))
        except:
            return 10

    @property
    def follow_interval(self):
        try:
            return int(self.get_option('automation', 'follow_interval'))
        except:
            return 5

    @property
    def add_friend_mode(self):
        try:
            return self.get_option('automation', 'add_friend_mode')
        except:
            return 'random'

    @property
    def add_friend_count(self):
        try:
            return int(self.get_option('automation', 'add_friend_count'))
        except:
            return 10

    @property
    def add_friend_interval(self):
        try:
            return int(self.get_option('automation', 'add_friend_interval'))
        except:
            return 5

    @property
    def add_friend_location(self):
        try:
            return self.get_option('automation', 'add_friend_location')
        except:
            return ''

    @property
    def add_friend_single_url(self):
        try:
            return self.get_option('automation', 'add_friend_single_url')
        except:
            return ''

    @property
    def group_action(self):
        try:
            return self.get_option('automation', 'group_action')
        except:
            return 'join'

    @property
    def group_keywords(self):
        try:
            return json.loads(self.get_option('automation', 'group_keywords'))
        except:
            return []

    @property
    def group_join_count(self):
        try:
            return int(self.get_option('automation', 'group_join_count'))
        except:
            return 5

    @property
    def group_post_content(self):
        try:
            return json.loads(self.get_option('automation', 'group_post_content'))
        except:
            return []

    @property
    def group_post_images(self):
        try:
            return json.loads(self.get_option('automation', 'group_post_images'))
        except:
            return []

    @property
    def group_post_interval(self):
        try:
            return int(self.get_option('automation', 'group_post_interval'))
        except:
            return 30

    @property
    def group_post_public(self):
        try:
            return self.get_option('automation', 'group_post_public').lower() == 'true'
        except:
            return False

    @property
    def main_post_content(self):
        try:
            return json.loads(self.get_option('automation', 'main_post_content'))
        except:
            return ["Hello Facebook!"]

    @property
    def main_post_images(self):
        try:
            return json.loads(self.get_option('automation', 'main_post_images'))
        except:
            return []

    @property
    def main_post_count(self):
        try:
            return int(self.get_option('automation', 'main_post_count'))
        except:
            return 1

    @property
    def main_post_interval(self):
        try:
            return int(self.get_option('automation', 'main_post_interval'))
        except:
            return 60

    @property
    def main_post_public(self):
        try:
            return self.get_option('automation', 'main_post_public').lower() == 'true'
        except:
            return True

    @property
    def message_mode(self):
        try:
            return self.get_option('automation', 'message_mode')
        except:
            return 'all_friends'

    @property
    def advanced_message_content(self):
        try:
            return json.loads(self.get_option('automation', 'advanced_message_content'))
        except:
            return ["Hello!"]

    @property
    def advanced_message_images(self):
        try:
            return json.loads(self.get_option('automation', 'advanced_message_images'))
        except:
            return []

    @property
    def advanced_message_interval(self):
        try:
            return int(self.get_option('automation', 'advanced_message_interval'))
        except:
            return 5

    @property
    def advanced_message_count(self):
        try:
            return int(self.get_option('automation', 'advanced_message_count'))
        except:
            return 10

    @property
    def message_anti_ban(self):
        try:
            return self.get_option('automation', 'message_anti_ban').lower() == 'true'
        except:
            return False

    @property
    def message_cloud_backup(self):
        try:
            return self.get_option('automation', 'message_cloud_backup').lower() == 'true'
        except:
            return False

    @property
    def register_count(self):
        try:
            return int(self.get_option('automation', 'register_count'))
        except:
            return 1

    @property
    def register_name_lang(self):
        try:
            return self.get_option('automation', 'register_name_lang')
        except:
            return 'en'

    @property
    def register_country_code(self):
        try:
            return self.get_option('automation', 'register_country_code')
        except:
            return '+1'

    @property
    def register_sms_platform(self):
        try:
            return self.get_option('automation', 'register_sms_platform')
        except:
            return ''

    @property
    def register_sms_api(self):
        try:
            return self.get_option('automation', 'register_sms_api')
        except:
            return ''

    @property
    def register_old_version(self):
        try:
            return self.get_option('automation', 'register_old_version').lower() == 'true'
        except:
            return False

    @property
    def contact_action(self):
        try:
            return self.get_option('automation', 'contact_action')
        except:
            return 'generate'

    @property
    def contact_count(self):
        try:
            return int(self.get_option('automation', 'contact_count'))
        except:
            return 100

    @property
    def contact_region(self):
        try:
            return self.get_option('automation', 'contact_region')
        except:
            return 'US'

    @property
    def contact_language(self):
        try:
            return self.get_option('automation', 'contact_language')
        except:
            return 'en'

    @property
    def contact_country_code(self):
        try:
            return self.get_option('automation', 'contact_country_code')
        except:
            return '+1'

    @property
    def contact_area_code(self):
        try:
            return self.get_option('automation', 'contact_area_code')
        except:
            return ''

    @property
    def contact_sequential(self):
        try:
            return self.get_option('automation', 'contact_sequential').lower() == 'true'
        except:
            return False

    @property
    def contact_file_path(self):
        try:
            return self.get_option('automation', 'contact_file_path')
        except:
            return './contacts/contact_list.txt'

    @property
    def contact_import_file(self):
        try:
            return self.get_option('automation', 'contact_import_file')
        except:
            return ''

    # Cloud Deduplication properties
    @property
    def cloud_dedup_enabled(self):
        try:
            return self.get_option('cloud_dedup', 'enabled').lower() == 'true'
        except:
            return False

    @property
    def cloud_dedup_db_name(self):
        try:
            return self.get_option('cloud_dedup', 'db_name')
        except:
            return 'default'

    @property
    def cloud_dedup_mode(self):
        try:
            return self.get_option('cloud_dedup', 'mode')
        except:
            return 'local'

    @property
    def cloud_dedup_remote_url(self):
        try:
            return self.get_option('cloud_dedup', 'remote_url')
        except:
            return ''

    @property
    def cloud_dedup_local_db_path(self):
        try:
            return self.get_option('cloud_dedup', 'local_db_path')
        except:
            return './dedup_cache/'

    # Account Management properties
    @property
    def accounts_file(self):
        try:
            return self.get_option('accounts', 'accounts_file')
        except:
            return './accounts.json'

    @property
    def accounts_skip_used(self):
        try:
            return self.get_option('accounts', 'skip_used').lower() == 'true'
        except:
            return True

    @property
    def accounts_auto_mark_used(self):
        try:
            return self.get_option('accounts', 'auto_mark_used').lower() == 'true'
        except:
            return True

    @property
    def members_selected_file(self):
        try:
            return self.get_option('members', 'selected_file')
        except:
            return ''
    
    @members_selected_file.setter
    def members_selected_file(self, value):
        """Set the selected member file path"""
        self.set_option('members', 'selected_file', value if value else '')

    @property
    def members_save_links_only(self):
        """只保存links文件 - Only save links file (no JSON format)"""
        try:
            val = self.get_option('members', 'save_links_only')
            return val.lower() == 'true' if val else False
        except:
            return True  # Default to true per client request

    @property
    def groups_selected_file(self):
        try:
            return self.get_option('groups', 'selected_file')
        except:
            return ''
    
    @groups_selected_file.setter
    def groups_selected_file(self, value):
        """Set the selected group file path"""
        self.set_option('groups', 'selected_file', value if value else '')

    @property
    def groups_save_links_only(self):
        """只保存links文件 - Only save links file for groups (no JSON format)
        
        TRUE: 只创建 _links.txt 文件 (1个文件)
        FALSE: 创建 .txt JSON 和 _links.txt 文件 (2个文件)
        
        ✅ 现在支持TRUE: 采集成员功能已修改为可以从 _links.txt 文件读取群组链接
        """
        try:
            val = self.get_option('groups', 'save_links_only')
            return val.lower() == 'true' if val else True  # Default to TRUE (1 file only)
        except:
            return True  # Default: only save links file

    @property
    def screen_width(self):
        """屏幕宽度 - Screen width for browser auto-arrangement"""
        try:
            return int(self.get_option('main', 'screen_width'))
        except:
            return 1920

    @property
    def screen_height(self):
        """屏幕高度 - Screen height for browser auto-arrangement"""
        try:
            return int(self.get_option('main', 'screen_height'))
        except:
            return 1080


config = Config()

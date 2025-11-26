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


config = Config()

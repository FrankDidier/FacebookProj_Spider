# -*- coding: utf-8 -*-
"""
Created on 2018-10-08 15:33:37
---------
@summary: 重新定义 selector
---------
@author: Boris
@email:  boris_liu@foxmail.com
"""
import re

class Selector(object):
    selectorlist_cls = None

    def __str__(self):
        data = repr(self.get())
        return "<%s xpath=%r data=%s>" % (type(self).__name__, self._expr, data)

    __repr__ = __str__

    def __init__(self, text=None, *args, **kwargs):
        # 先将&nbsp; 转为空格，否则selector 会转为 \xa0
        if text:
            text = re.sub("&nbsp;", "\x20", text)
        super(Selector, self).__init__(text, *args, **kwargs)

    def re_first(self, regex, default=None, replace_entities=True, flags=re.S):
        """
        Apply the given regex and return the first unicode string which
        matches. If there is no match, return the default value (``None`` if
        the argument is not provided).

        By default, character entity references are replaced by their
        corresponding character (except for ``&amp;`` and ``&lt;``.
        Passing ``replace_entities`` as ``False`` switches off these
        replacements.
        """

        datas = self.re(regex, replace_entities=replace_entities, flags=flags)

        return datas[0] if datas else default

    def re(self, regex, replace_entities=True, flags=re.S):
        """
        Apply the given regex and return a list of unicode strings with the
        matches.

        ``regex`` can be either a compiled regular expression or a string which
        will be compiled to a regular expression using ``re.compile(regex)``.

        By default, character entity references are replaced by their
        corresponding character (except for ``&amp;`` and ``&lt;``.
        Passing ``replace_entities`` as ``False`` switches off these
        replacements.
        """

        pass

    def _get_root(self, text, base_url=None):
        pass

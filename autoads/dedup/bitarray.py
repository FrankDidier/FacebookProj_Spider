# -*- coding: utf-8 -*-

from __future__ import absolute_import

class BitArray:
    def setall(self, value):
        pass

    def __repr__(self):
        raise ImportError("this method mush be implement")

    def set(self, offsets, values):
        """
        设置字符串数字某一位的值， 返回之前的值
        @param offsets: 支持列表或单个值
        @param values: 支持列表或单个值
        @return: list / 单个值
        """
        raise ImportError("this method mush be implement")

    def get(self, offsets):
        """
        取字符串数字某一位的值
        @param offsets: 支持列表或单个值
        @return: list / 单个值
        """
        raise ImportError("this method mush be implement")

    def count(self, value=True):
        raise ImportError("this method mush be implement")


class MemoryBitArray(BitArray):
    def __init__(self, num_bits):
        try:
            import bitarray
        except Exception as e:
            raise Exception(
                "需要安装feapder完整版\ncommand: pip install myfeapder[all]\n若安装出错，参考：https://boris.org.cn/myfeapder/#/question/%E5%AE%89%E8%A3%85%E9%97%AE%E9%A2%98"
            )

        self.num_bits = num_bits
        self.bitarray = bitarray.bitarray(num_bits, endian="little")

        self.setall(0)

    def __repr__(self):
        return "MemoryBitArray: {}".format(self.num_bits)

    def setall(self, value):
        self.bitarray.setall(value)

    def set(self, offsets, values):
        """
        设置字符串数字某一位的值， 返回之前的值
        @param offsets: 支持列表或单个值
        @param values: 支持列表或单个值
        @return: list / 单个值
        """

        old_values = []

        if isinstance(offsets, list):
            if not isinstance(values, list):
                values = [values] * len(offsets)
            else:
                assert len(offsets) == len(values), "offsets值要与values值一一对应"

            for offset, value in zip(offsets, values):
                old_values.append(int(self.bitarray[offset]))
                self.bitarray[offset] = value

        else:
            old_values = int(self.bitarray[offsets])
            self.bitarray[offsets] = values

        return old_values

    def get(self, offsets):
        """
        取字符串数字某一位的值
        @param offsets: 支持列表或单个值
        @return: list / 单个值
        """
        if isinstance(offsets, list):
            return [self.bitarray[offset] for offset in offsets]
        else:
            return self.bitarray[offsets]

    def count(self, value=True):
        return self.bitarray.count(value)

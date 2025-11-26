import pyDes
import base64
import random
import string
import time
import datetime


class TripleDes(object):
    des_mode = {"CBC": pyDes.CBC, "ECB": pyDes.ECB}
    des_pad_mode = {"PAD_PKCS5": pyDes.PAD_PKCS5, "PAD_NORMAL": pyDes.PAD_NORMAL}

    def __init__(self, mode='CBC', pad_mode='PAD_PKCS5', pad=None, trans_base64=False):
        """
        :param mode: des 加密模式，目前支持 CBC，ECB
        :param pad_mode: 目前支持 PAD_PKCS5，PAD_NORMAL
        :param trans_base64: 加密结果是否以 base64 格式输出
        :param key: 密钥
        :param iv: 偏移量
        :param pad:
        """
        self.key = 'ccqazlrjlR19PFERIRooiIie'
        self.iv = 'cc201511'
        self.trans_base64 = trans_base64
        # 3des
        self.k = pyDes.triple_des(self.key, TripleDes.des_mode.get(mode), self.iv, pad,
                                  TripleDes.des_pad_mode.get(pad_mode))

    def encryption(self, data: str) -> str:
        """
        3des 加密
        说明: 3DES数据块长度为64位，所以IV长度需要为8个字符（ECB模式不用IV），密钥长度为16或24个字符（8个字符以内则结果与DES相同
        IV与密钥超过长度则截取，不足则在末尾填充'\0'补足
        :param data: 待加密数据
        :return:
        """
        _encryption_result = self.k.encrypt(data)
        if self.trans_base64:
            _encryption_result = self._base64encode(_encryption_result)
        return _encryption_result.decode()

    @staticmethod
    def _base64encode(data):
        """
        base 64 encode
        :param data: encode data
        :return:
        """
        try:
            _b64encode_result = base64.b64encode(data)
        except Exception as e:
            raise Exception(f"base64 encode error:{e}")
        return _b64encode_result


des = TripleDes(trans_base64=True)

if __name__ == "__main__":
    # 按照随机8-20位大写小写特殊字符+iv-开始时间-结束时间-随机5-15位数字-随机8-20位大写小写特殊字符

    DesObj = TripleDes(trans_base64=True)
    # test_data=TripleDes._gen_data()
    #
    # result = DesObj.encryption(test_data)
    # print(f"加密结果: {result}")

    result2 = DesObj.decrypt(
        'p6RcLSS3QbZAJOqxzmHeCihqNiugzyYJeeyj1NF5p1O+sDV2uG7RAh+79DXPURkc5QvLXvyTb+W9YhN9HtYSksXoFLSiOFwT')
    print(f"解密结果: {result2}")

    # print(TripleDes._expired_data('PDucnbct7STKfbvkF-1660175304.0-1660434504.0-k6G6xcX1tsld8w62sh5ZeByQ7mx'))

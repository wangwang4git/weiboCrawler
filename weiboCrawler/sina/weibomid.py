#!/usr/bin/python
#-*- encoding: utf-8 -*-

def sinaWburl2ID(url):
    surl2 = str62to10(url[len(url) - 4:])
    surl1 = str62to10(url[len(url) - 8: len(url) - 4])
    surl0 = str62to10(url[0: len(url) - 8])
    int10 = surl0 + surl1 + surl2
    while int10.startswith('0'):
        int10 = int10[1:]
    return int10


def str62to10(str62) :
    """ 62进制到10进制  """
    str1 = 0;
    for i in  range(len(str62)):
        vi = pow(62, (len(str62) - i - 1))
        str1 += vi * str62keys(str62[i])
    str2 = str(str1)
    while len(str2) < 7 :
        str2 = '0' + str2
    return str2;


def str62keys(ks) :
    """ 62进制字典 """
    str62keys = [\
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", \
        "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", \
        "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", \
        "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X","Y","Z"\
    ]
    return str62keys.index(ks)


def midToStr(mid) :
    mid_length = len(mid);
    url = ''
    str = mid[::-1]
    strs = [str[i: i+7] for i in range(0, len(str), 7)]
    for v in strs:
        char = intTo62(v[::-1]);
        while len(char) < 4 :
            char = char + '0'
        url += char;

    url_str = url[::-1]

    while url_str.startswith('0'):
        url_str = url_str[1:]
    return url_str


def str62keys_int_62(key) :
    """ 62进制字典 """
    str62keys = [\
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", \
        "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", \
        "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", \
        "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X","Y","Z"\
    ]
    return str62keys[key]


def intTo62(int10) :
    """ url 10 进制 转62进制  """
    s62 = ''
    r = 0
    int10 = int(int10)
    while (int10 != 0) :
        r = int10 % 62
        s62 += str62keys_int_62(r)
        int10 = int10 / 62

    return s62


if __name__ == '__main__':
    # 调用
    print sinaWburl2ID('y1v8Y8MqR');
    # 调用
    print midToStr('3403580482092801');

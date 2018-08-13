from django.test import TestCase

# Create your tests here.
def func(args):
    st = ''
    for i in args:
        new_i = bin(i)  # 将数字转化为二进制
        new_i = new_i[2:]  # 将转化后的二进制去除'0b'前缀
        new_i = new_i[2:].rjust(8, '0')  # 二进制前面填充0，固定总长度8
        st += new_i[2:].rjust(8, '0')  # 将四个数字的二进制进行拼接
    st = int(st, base=2)  # 拼接后的字符串转化为10进制数字
    return st


li = [10, 3, 9, 12]
print(func(li))

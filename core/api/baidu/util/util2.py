# @Time    : 2023/06/03 11:57
# @Author  : fyq
# @File    : util2.py
# @Software: PyCharm

__author__ = 'fyq'

from typing import List

from core.util.default_list import DefaultList
from core.util.js_displace import left_shift, unsigned_right_shift


def algorithm1(data: str):
    """
        function o(t) {
            for (var r = 1 + (t.length + 8 >> 6), e = new Array(16 * r), n = 0; n < 16 * r; n++)
                e[n] = 0;
            for (n = 0; n < t.length; n++)
                e[n >> 2] |= t.charCodeAt(n) << 24 - 8 * (3 & n);
            return e[n >> 2] |= 128 << 24 - 8 * (3 & n),
            e[16 * r - 1] = 8 * t.length,
            e
        }
    """
    r = 1 + (len(data) + 8 >> 6)
    res = [0 for _ in range(0, 16 * r)]
    n = 0
    for n in range(0, len(data)):
        res[n >> 2] |= left_shift(ord(data[n]), 24 - 8 * (3 & n))
    n += 1
    res[n >> 2] |= left_shift(128, 24 - 8 * (3 & n))
    res[16 * r - 1] = 8 * len(data)
    return res


def algorithm2(data: str):
    """
        function g(t) { for (var r = t, e = Array(80), n = 1732584193, i = -271733879, o = -1732584194, a = 271733878,
        s = -1009589776, c = 0; c < r.length; c += 16) { for (var h = n, f = i, u = o, l = a, d = s, p = 0; p < 80; p++)
        { e[p] = p < 16 ? r[c + p] : B(e[p - 3] ^ e[p - 8] ^ e[p - 14] ^ e[p - 16], 1); var v = w(w(B(n, 5), y(p, i, o,
        a)), w(w(s, e[p]), (_ = p) < 20 ? 1518500249 : _ < 40 ? 1859775393 : _ < 60 ? -1894007588 : -899497514)); s = a,
        a = o, o = B(i, 30), i = n, n = v } n = w(n, h), i = w(i, f), o = w(o, u), a = w(a, l), s = w(s, d) } var _;
        return new Array(n,i,o,a,s) }
    """
    data_list = DefaultList(data)
    res = [0 for _ in range(0, 80)]
    var1 = 1732584193
    var2 = -271733879
    var3 = -1732584194
    var4 = 271733878
    var5 = -1009589776
    for c in range(0, len(data_list), 16):
        var6 = var1
        var7 = var2
        var8 = var3
        var9 = var4
        var10 = var5
        for p in range(0, 80):
            res[p] = data_list[c + p] if p < 16 else algorithm3(res[p - 3] ^ res[p - 8] ^ res[p - 14] ^ res[p - 16], 1)
            _var1 = algorithm4(algorithm3(var1, 5), algorithm5(p, var2, var3, var4))
            _ = p
            if _ < 20:
                var11 = 1518500249
            elif _ < 40:
                var11 = 1859775393
            elif _ < 60:
                var11 = -1894007588
            else:
                var11 = -899497514
            _var2 = algorithm4(algorithm4(var5, res[p]), var11)
            var12 = algorithm4(_var1, _var2)
            var5 = var4
            var4 = var3
            var3 = algorithm3(var2, 30)
            var2 = var1
            var1 = var12
        var1 = algorithm4(var1, var6)
        var2 = algorithm4(var2, var7)
        var3 = algorithm4(var3, var8)
        var4 = algorithm4(var4, var9)
        var5 = algorithm4(var5, var10)
    return [var1, var2, var3, var4, var5]


def algorithm3(data: int, shift_len: int):
    return left_shift(data, shift_len) | unsigned_right_shift(data, 32 - shift_len)


def algorithm4(data1: int, data2: int):
    """
        function w(t, r) {
            var e = (65535 & t) + (65535 & r);
            return (t >> 16) + (r >> 16) + (e >> 16) << 16 | 65535 & e
        }
    """
    res = (65535 & data1) + (65535 & data2)
    return left_shift((data1 >> 16) + (data2 >> 16) + (res >> 16), 16) | 65535 & res


def algorithm5(d1: int, d2: int, d3: int, d4: int):
    """
        function y(t, r, e, n) {
            return t < 20 ? r & e | ~r & n : t < 40 ? r ^ e ^ n : t < 60 ? r & e | r & n | e & n : r ^ e ^ n
        }
    """
    if d1 < 20:
        return d2 & d3 | ~d2 & d4
    elif d1 < 40:
        return d2 ^ d3 ^ d4
    elif d1 < 60:
        return d2 & d3 | d2 & d4 | d3 & d4
    return d2 ^ d3 ^ d4


def algorithm6(data: List[int], upper: bool = False):
    """
        function i(t) {
                for (var r = a ? "0123456789ABCDEF" : "0123456789abcdef", e = "", n = 0; n < 4 * t.length; n++)
                    e += r.charAt(t[n >> 2] >> 8 * (3 - n % 4) + 4 & 15) + r.charAt(t[n >> 2] >> 8 * (3 - n % 4) & 15);
            return e
        }
    """
    if upper:
        constant = "0123456789ABCDEF"
    else:
        constant = "0123456789abcdef"
    res = ""
    for n in range(0, 4 * len(data)):
        res += constant[data[n >> 2] >> 8 * (3 - n % 4) + 4 & 15] + constant[data[n >> 2] >> 8 * (3 - n % 4) & 15]
    return res

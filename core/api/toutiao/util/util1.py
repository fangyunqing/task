# @Time    : 2023/06/29 15:52
# @Author  : fyq
# @File    : util1.py
# @Software: PyCharm

__author__ = 'fyq'


def algorithm1(data):
    """
    function(e) {
        var t, n = [];
        if (void 0 === e)
            return "";
        t = function(e) {
            for (var t, n = e.toString(), o = [], r = 0; r < n.length; r++)
                0 <= (t = n.charCodeAt(r)) && t <= 127 ? o.push(t) :
                128 <= t && t <= 2047 ? (o.push(192 | 31 & t >> 6),
                o.push(128 | 63 & t)) :
                (2048 <= t && t <= 55295 || 57344 <= t && t <= 65535) && (o.push(224 | 15 & t >> 12),
                o.push(128 | 63 & t >> 6),
                o.push(128 | 63 & t));
            for (var a = 0; a < o.length; a++)
                o[a] &= 255;
            return o
        }(e);
        for (var o = 0, r = t.length; o < r; ++o)
            n.push((5 ^ t[o]).toString(16));
        return n.join("")
    }
    :param data:
    :return:
    """
    if not data:
        return ""
    var1 = algorithm2(data)
    res = []
    for s in var1:
        res.append(hex(5 ^ s)[2:])
    return "".join(res)


def algorithm2(data):
    """
    function(e) {
        for (var t, n = e.toString(), o = [], r = 0; r < n.length; r++)
            0 <= (t = n.charCodeAt(r)) && t <= 127 ? o.push(t) : 128 <= t && t <= 2047 ? (o.push(192 | 31 & t >> 6),
            o.push(128 | 63 & t)) :
            (2048 <= t && t <= 55295 || 57344 <= t && t <= 65535) && (o.push(224 | 15 & t >> 12),
            o.push(128 | 63 & t >> 6),
            o.push(128 | 63 & t));
        for (var a = 0; a < o.length; a++)
            o[a] &= 255;
        return o
    }
    :param data:
    :return:
    """
    res = []
    for s in str(data):
        var1 = ord(s)
        if 0 <= var1 <= 127:
            res.append(var1)
        elif 128 <= var1 <= 2047:
            res.append(192 | 31 & var1 >> 6)
            res.append(128 | 63 & var1)
        elif 2048 <= var1 <= 55295 or 57344 <= var1 <= 65535:
            res.append(224 | 15 & var1 >> 12)
            res.append(128 | 63 & var1 >> 6),
            res.append(128 | 63 & var1)
    for s_idx, s in enumerate(res):
        res[s_idx] &= 255
    return res


if __name__ == "__main__":
    print(algorithm1("24"))

from core.util.default_list import DefaultList
from core.util.js_displace import left_shift, unsigned_right_shift


def algorithm1(d1, d2):
    """
        function u(t, r) {
            var e = (65535 & t) + (65535 & r);
            return (t >> 16) + (r >> 16) + (e >> 16) << 16 | 65535 & e
        }
    """
    d1 = d1 if d1 else 0
    e = (65535 & d1) + (65535 & d2)
    return left_shift((d1 >> 16) + (d2 >> 16) + (e >> 16), 16) | 65535 & e


def algorithm2(d1, d2, d3, d4, d5, d6):
    """
        function s(t, r, e, n, i, o) {
            return u(function a(t, r) {
                return t << r | t >>> 32 - r
            }(u(u(r, t), u(n, o)), i), e)
        }
    """

    def a(var1, var2):
        return left_shift(var1, var2) | unsigned_right_shift(var1, 32 - var2)

    return algorithm1(a(algorithm1(algorithm1(d2, d1), algorithm1(d4, d6)), d5), d3)


def algorithm3(d1, d2, d3, d4, d5, d6, d7):
    """
        function l(t, r, e, n, i, o, a) {
            return s(r & e | ~r & n, t, r, i, o, a)
        }
    """
    return algorithm2(d2 & d3 | ~d2 & d4, d1, d2, d5, d6, d7)


def algorithm4(d1, d2, d3, d4, d5, d6, d7):
    """
        function d(t, r, e, n, i, o, a) {
            return s(r & n | e & ~n, t, r, i, o, a)
        }
    """
    return algorithm2(d2 & d4 | d3 & ~d4, d1, d2, d5, d6, d7)


def algorithm5(d1, d2, d3, d4, d5, d6, d7):
    """
        function p(t, r, e, n, i, o, a) {
            return s(r ^ e ^ n, t, r, i, o, a)
        }
    """
    return algorithm2(d2 ^ d3 ^ d4, d1, d2, d5, d6, d7)


def algorithm6(d1, d2, d3, d4, d5, d6, d7):
    """
        function v(t, r, e, n, i, o, a) {
            return s(e ^ (r | ~n), t, r, i, o, a)
        }
    """
    return algorithm2(d3 ^ (d2 | ~d4), d1, d2, d5, d6, d7)


def algorithm7(d1, d2):
    """
    function c(t, r) { t[r >> 5] |= 128 << r % 32, t[14 + (r + 64 >>> 9 << 4)] = r; var e, n, i, o, a,
    s = 1732584193, c = -271733879, h = -1732584194, f = 271733878; for (e = 0; e < t.length; e += 16) c = v(c = v(c
    = v(c = v(c = p(c = p(c = p(c = p(c = d(c = d(c = d(c = d(c = l(c = l(c = l(c = l(i = c, h = l(o = h,
    f = l(a = f, s = l(n = s, c, h, f, t[e], 7, -680876936), c, h, t[e + 1], 12, -389564586), s, c, t[e + 2], 17,
    606105819), f, s, t[e + 3], 22, -1044525330), h = l(h, f = l(f, s = l(s, c, h, f, t[e + 4], 7, -176418897), c, h,
    t[e + 5], 12, 1200080426), s, c, t[e + 6], 17, -1473231341), f, s, t[e + 7], 22, -45705983), h = l(h, f = l(f,
    s = l(s, c, h, f, t[e + 8], 7, 1770035416), c, h, t[e + 9], 12, -1958414417), s, c, t[e + 10], 17, -42063), f, s,
    t[e + 11], 22, -1990404162), h = l(h, f = l(f, s = l(s, c, h, f, t[e + 12], 7, 1804603682), c, h, t[e + 13], 12,
    -40341101), s, c, t[e + 14], 17, -1502002290), f, s, t[e + 15], 22, 1236535329), h = d(h, f = d(f, s = d(s, c, h,
    f, t[e + 1], 5, -165796510), c, h, t[e + 6], 9, -1069501632), s, c, t[e + 11], 14, 643717713), f, s, t[e], 20,
    -373897302), h = d(h, f = d(f, s = d(s, c, h, f, t[e + 5], 5, -701558691), c, h, t[e + 10], 9, 38016083), s, c,
    t[e + 15], 14, -660478335), f, s, t[e + 4], 20, -405537848), h = d(h, f = d(f, s = d(s, c, h, f, t[e + 9], 5,
    568446438), c, h, t[e + 14], 9, -1019803690), s, c, t[e + 3], 14, -187363961), f, s, t[e + 8], 20, 1163531501),
    h = d(h, f = d(f, s = d(s, c, h, f, t[e + 13], 5, -1444681467), c, h, t[e + 2], 9, -51403784), s, c, t[e + 7],
    14, 1735328473), f, s, t[e + 12], 20, -1926607734), h = p(h, f = p(f, s = p(s, c, h, f, t[e + 5], 4, -378558), c,
    h, t[e + 8], 11, -2022574463), s, c, t[e + 11], 16, 1839030562), f, s, t[e + 14], 23, -35309556), h = p(h,
    f = p(f, s = p(s, c, h, f, t[e + 1], 4, -1530992060), c, h, t[e + 4], 11, 1272893353), s, c, t[e + 7], 16,
    -155497632), f, s, t[e + 10], 23, -1094730640), h = p(h, f = p(f, s = p(s, c, h, f, t[e + 13], 4, 681279174), c,
    h, t[e], 11, -358537222), s, c, t[e + 3], 16, -722521979), f, s, t[e + 6], 23, 76029189), h = p(h, f = p(f,
    s = p(s, c, h, f, t[e + 9], 4, -640364487), c, h, t[e + 12], 11, -421815835), s, c, t[e + 15], 16, 530742520), f,
    s, t[e + 2], 23, -995338651), h = v(h, f = v(f, s = v(s, c, h, f, t[e], 6, -198630844), c, h, t[e + 7], 10,
    1126891415), s, c, t[e + 14], 15, -1416354905), f, s, t[e + 5], 21, -57434055), h = v(h, f = v(f, s = v(s, c, h,
    f, t[e + 12], 6, 1700485571), c, h, t[e + 3], 10, -1894986606), s, c, t[e + 10], 15, -1051523), f, s, t[e + 1],
    21, -2054922799), h = v(h, f = v(f, s = v(s, c, h, f, t[e + 8], 6, 1873313359), c, h, t[e + 15], 10, -30611744),
    s, c, t[e + 6], 15, -1560198380), f, s, t[e + 13], 21, 1309151649), h = v(h, f = v(f, s = v(s, c, h, f, t[e + 4],
    6, -145523070), c, h, t[e + 11], 10, -1120210379), s, c, t[e + 2], 15, 718787259), f, s, t[e + 9], 21,
    -343485551), s = u(s, n), c = u(c, i), h = u(h, o), f = u(f, a); return [s, c, h, f] }
    """
    d1[d2 >> 5] |= left_shift(128, d2 % 32)
    location = 14 + left_shift(unsigned_right_shift(d2 + 64, 9), 4)
    while len(d1) < location + 1:
        d1.append(0)
    d1[location] = d2

    d1 = DefaultList(d1)

    var1 = 1732584193
    var2 = -271733879
    var3 = -1732584194
    var4 = 271733878

    for _ in range(0, len(d1), 16):
        var5 = var2
        var6 = var3
        var7 = var4
        var8 = var1

        var1 = algorithm3(var8, var2, var3, var4, d1[_], 7, -680876936)
        var4 = algorithm3(var7, var1, var2, var3, d1[_ + 1], 12, -389564586)
        var3 = algorithm3(var6, var4, var1, var2, d1[_ + 2], 17, 606105819)
        var2 = algorithm3(var5, var3, var4, var1, d1[_ + 3], 22, -1044525330)

        var1 = algorithm3(var1, var2, var3, var4, d1[_ + 4], 7, -176418897)
        var4 = algorithm3(var4, var1, var2, var3, d1[_ + 5], 12, 1200080426)
        var3 = algorithm3(var3, var4, var1, var2, d1[_ + 6], 17, -1473231341)
        var2 = algorithm3(var2, var3, var4, var1, d1[_ + 7], 22, -45705983)

        var1 = algorithm3(var1, var2, var3, var4, d1[_ + 8], 7, 1770035416)
        var4 = algorithm3(var4, var1, var2, var3, d1[_ + 9], 12, -1958414417)
        var3 = algorithm3(var3, var4, var1, var2, d1[_ + 10], 17, -42063)
        var2 = algorithm3(var2, var3, var4, var1, d1[_ + 11], 22, -1990404162)

        var1 = algorithm3(var1, var2, var3, var4, d1[_ + 12], 7, 1804603682)
        var4 = algorithm3(var4, var1, var2, var3, d1[_ + 13], 12, -40341101)
        var3 = algorithm3(var3, var4, var1, var2, d1[_ + 14], 17, -1502002290)
        var2 = algorithm3(var2, var3, var4, var1, d1[_ + 15], 22, 1236535329)

        var1 = algorithm4(var1, var2, var3, var4, d1[_ + 1], 5, -165796510)
        var4 = algorithm4(var4, var1, var2, var3, d1[_ + 6], 9, -1069501632)
        var3 = algorithm4(var3, var4, var1, var2, d1[_ + 11], 14, 643717713)
        var2 = algorithm4(var2, var3, var4, var1, d1[_], 20, -373897302)

        var1 = algorithm4(var1, var2, var3, var4, d1[_ + 5], 5, -701558691)
        var4 = algorithm4(var4, var1, var2, var3, d1[_ + 10], 9, 38016083)
        var3 = algorithm4(var3, var4, var1, var2, d1[_ + 15], 14, -660478335)
        var2 = algorithm4(var2, var3, var4, var1, d1[_ + 4], 20, -405537848)

        var1 = algorithm4(var1, var2, var3, var4, d1[_ + 9], 5, 568446438)
        var4 = algorithm4(var4, var1, var2, var3, d1[_ + 14], 9, -1019803690)
        var3 = algorithm4(var3, var4, var1, var2, d1[_ + 3], 14, -187363961)
        var2 = algorithm4(var2, var3, var4, var1, d1[_ + 8], 20, 1163531501)

        var1 = algorithm4(var1, var2, var3, var4, d1[_ + 13], 5, -1444681467)
        var4 = algorithm4(var4, var1, var2, var3, d1[_ + 2], 9, -51403784)
        var3 = algorithm4(var3, var4, var1, var2, d1[_ + 7], 14, 1735328473)
        var2 = algorithm4(var2, var3, var4, var1, d1[_ + 12], 20, -1926607734)

        var1 = algorithm5(var1, var2, var3, var4, d1[_ + 5], 4, -378558)
        var4 = algorithm5(var4, var1, var2, var3, d1[_ + 8], 11, -2022574463)
        var3 = algorithm5(var3, var4, var1, var2, d1[_ + 11], 16, 1839030562)
        var2 = algorithm5(var2, var3, var4, var1, d1[_ + 14], 23, -35309556)

        var1 = algorithm5(var1, var2, var3, var4, d1[_ + 1], 4, -1530992060)
        var4 = algorithm5(var4, var1, var2, var3, d1[_ + 4], 11, 1272893353)
        var3 = algorithm5(var3, var4, var1, var2, d1[_ + 7], 16, -155497632)
        var2 = algorithm5(var2, var3, var4, var1, d1[_ + 10], 23, -1094730640)

        var1 = algorithm5(var1, var2, var3, var4, d1[_ + 13], 4, 681279174)
        var4 = algorithm5(var4, var1, var2, var3, d1[_], 11, -358537222)
        var3 = algorithm5(var3, var4, var1, var2, d1[_ + 3], 16, -722521979)
        var2 = algorithm5(var2, var3, var4, var1, d1[_ + 6], 23, 76029189)

        var1 = algorithm5(var1, var2, var3, var4, d1[_ + 9], 4, -640364487)
        var4 = algorithm5(var4, var1, var2, var3, d1[_ + 12], 11, -421815835)
        var3 = algorithm5(var3, var4, var1, var2, d1[_ + 15], 16, 530742520)
        var2 = algorithm5(var2, var3, var4, var1, d1[_ + 2], 23, -995338651)

        var1 = algorithm6(var1, var2, var3, var4, d1[_], 6, -198630844)
        var4 = algorithm6(var4, var1, var2, var3, d1[_ + 7], 10, 1126891415)
        var3 = algorithm6(var3, var4, var1, var2, d1[_ + 14], 15, -1416354905)
        var2 = algorithm6(var2, var3, var4, var1, d1[_ + 5], 21, -57434055)

        var1 = algorithm6(var1, var2, var3, var4, d1[_ + 12], 6, 1700485571)
        var4 = algorithm6(var4, var1, var2, var3, d1[_ + 3], 10, -1894986606)
        var3 = algorithm6(var3, var4, var1, var2, d1[_ + 10], 15, -1051523)
        var2 = algorithm6(var2, var3, var4, var1, d1[_ + 1], 21, -2054922799)

        var1 = algorithm6(var1, var2, var3, var4, d1[_ + 8], 6, 1873313359)
        var4 = algorithm6(var4, var1, var2, var3, d1[_ + 15], 10, -30611744)
        var3 = algorithm6(var3, var4, var1, var2, d1[_ + 6], 15, -1560198380)
        var2 = algorithm6(var2, var3, var4, var1, d1[_ + 13], 21, 1309151649)

        var1 = algorithm6(var1, var2, var3, var4, d1[_ + 4], 6, -145523070)
        var4 = algorithm6(var4, var1, var2, var3, d1[_ + 11], 10, -1120210379)
        var3 = algorithm6(var3, var4, var1, var2, d1[_ + 2], 15, 718787259)
        var2 = algorithm6(var2, var3, var4, var1, d1[_ + 9], 21, -343485551)

        var1 = algorithm1(var1, var8)
        var2 = algorithm1(var2, var5)
        var3 = algorithm1(var3, var6)
        var4 = algorithm1(var4, var7)

    return [var1, var2, var3, var4]


def algorithm8(data):
    res = [0 for _ in range(0, (len(data) >> 2) + 1)]
    for index in range(0, len(data) * 8, 8):
        res[index >> 5] |= left_shift((255 & ord(data[index // 8])), index % 32)
    return res


def algorithm9(data):
    """
        function h(t) {
            var r, e = "";
            for (r = 0; r < 32 * t.length; r += 8)
                e += String.fromCharCode(t[r >> 5] >>> r % 32 & 255);
            return e
        }
    """
    res = ""
    for r in range(0, len(data) * 32, 8):
        res += chr(unsigned_right_shift(data[r >> 5], r % 32) & 255)
    return res


def algorithm10(t):
    """
       function o(t) {
        var r, e, n = "0123456789abcdef", i = "";
        for (e = 0; e < t.length; e += 1)
            r = t.charCodeAt(e),
            i += n.charAt(r >>> 4 & 15) + n.charAt(15 & r);
        return i
    }
    """
    constant = "0123456789abcdef"
    res = ""
    for _ in range(0, len(t)):
        r = ord(t[_])
        res += constant[unsigned_right_shift(r, 4) & 15] + constant[15 & r]
    return res


def algorithm11():
    """
        function _(t, r) {
            return function s(t, r) {
                var e, n, i = f(t), o = [], a = [];
                for (o[15] = a[15] = undefined,
                16 < i.length && (i = c(i, 8 * t.length)),
                e = 0; e < 16; e += 1)
                    o[e] = 909522486 ^ i[e],
                    a[e] = 1549556828 ^ i[e];
                return n = c(o.concat(f(r)), 512 + 8 * r.length),
                h(c(a.concat(n), 640))
            }(e(t), e(r))
        }
    """
    return []


def algorithm12(data):
    """
        function e(t) {
            return unescape(encodeURIComponent(t))
        }
    """
    return data


def algorithm13(data):
    """
        function a(t) {
            return function r(t) {
                return h(c(f(t), 8 * t.length))
            }(e(t))
        }
    """

    def func(var):
        return algorithm9(algorithm7(algorithm8(var), 8 * len(var)))

    return func(str(data))


def algorithm14(d1, d2, d3):
    """
        t.exports = function g(t, r, e) {
            return r ? e ? _(r, t) : function n(t, r) {
                return o(_(t, r))
            }(r, t) : e ? a(t) : function i(t) {
                return o(a(t))
            }(t)
    """
    if d2:
        if d3:
            return algorithm11()
        else:
            return algorithm10(algorithm11())
    else:
        if d3:
            return algorithm13(d1)
        else:
            return algorithm10(algorithm13(d1))

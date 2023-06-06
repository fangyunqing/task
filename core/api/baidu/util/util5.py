from core.api.baidu.util import util4
from core.util.default_list import DefaultList

_map = {
    "a": "3",
    "b": "4",
    "c": "5",
    "d": "9",
    "e": "8",
    "f": "7",
    "g": "1",
    "h": "2",
    "i": "6",
    "j": "0",
    "k": "a",
    "l": "b",
    "m": "c",
    "n": "d",
    "o": "e",
    "p": "f",
    "q": "g",
    "r": "z",
    "s": "y",
    "t": "x",
    "u": "w",
    "v": "v",
    "w": "u",
    "x": "o",
    "y": "p",
    "z": "q",
    "0": "s",
    "1": "t",
    "2": "r",
    "3": "h",
    "4": "i",
    "5": "j",
    "6": "k",
    "7": "l",
    "8": "m",
    "9": "n"
}


def add_screen(d1, d2):
    """
        function(t, r) {
            var e = [];
            for (var n in t)
                t.hasOwnProperty(n) && e.push(n);
            e.sort();
            for (var i = [], o = 0, a = e.length; o < a; o++) {
                var s = e[o];
                i.push(s + "=" + t[s])
            }
            var c = l(i.join("&"))
              , h = ""
              , f = (window.screen.width + "" + window.screen.height).split("");
            for (o = 0; o < f.length; o++)
                h += d[f[o]];
            return function u(t, r) {
                var e, n = "", i = t.split(""), o = r.split("");
                if (i.length >= o.length) {
                    for (e = 0; e < o.length; e++)
                        n += i[e] + o[e];
                    n += t.substring(e)
                } else {
                    for (e = 0; e < i.length; e++)
                        n += i[e] + o[e];
                    n += r.substring(e)
                }
                return n
            }(c, h)
        }
    """
    var1 = DefaultList(list(d1.keys()))
    var1.sort()
    var2 = []
    for s in var1:
        var2.append(f"{s}={d1[s]}")
    c = util4.algorithm14("&".join(var2), None, None)
    h = ""
    f = ["1", "9", "2", "0", "1", "0", "8", "0"]
    for v_o in range(0, len(f)):
        h += _map[f[v_o]]

    return algorithm1(c, h)


def algorithm1(d1, d2):
    """
    function u(t, r) {
            var e, n = "", i = t.split(""), o = r.split("");
            if (i.length >= o.length) {
                for (e = 0; e < o.length; e++)
                    n += i[e] + o[e];
                n += t.substring(e)
            } else {
                for (e = 0; e < i.length; e++)
                    n += i[e] + o[e];
                n += r.substring(e)
            }
            return n
    }
    """
    res = ""
    var1 = d1
    var2 = d2
    if len(var1) >= len(var2):
        for e in range(0, len(var2)):
            res += var1[e] + var2[e]
        res += d1[len(var2):]
    else:
        for e in range(0, len(var1)):
            res += var1[e] + var2[e]
        res += d1[len(var1):]
    return res

# @Time    : 2023/03/21 20:08
# @Author  : fyq
# @File    : func3.py
# @Software: PyCharm

__author__ = 'fyq'

import json
from typing import Any, Dict

from core.api.baidu.util import util3, util4
from core.util.time import thirteen_digits_time
from core.util import random


def jsonp(params: Dict[str, Any],
          fuid: str = None,
          trace_id: bool = False) -> Dict[str, Any]:
    """
    n.jsonp = function(n, i, s) { s = s || {}, e && e.traceID && e.traceID.createTraceID && (i.traceid =
    e.traceID.createTraceID()); var o = {}; for (var a in i) { var c = i[a]; void 0 !== c && null !== c && (o[a] = c)
    } try { var l = "OOOO00" , d = "OOO00O" , g = "OOO000" , p = "OOO0OO" , m = "O0OOO0" , f = { OOOOO0: l,
    O00000: d, O0O00O: g, O000OO: p, O0O000: m } , h = (new Date).getTime() / 1e3 , v = parseInt(h / 86400, 10) % 5 ,
    b = []; if (Object && Object.keys) b = Object.keys(f); else { b = []; for (var y in f) b.push(y) } var _ = f[b[
    v]] || ""; window.moonshadV3 && window.moonshadV3[_] && i && (i = baidu.extend(i, window.moonshadV3[_](o,
    baidu))) } catch (w) { console.log(w) } return new t(function(e, t) { n = r(n, i), u(n, function(t) {
    s.processData && (t = s.processData(t)), e && e(t) }, { charset: s.charset, queryField: s.queryField,
    timeOut: s.timeOut, onfailure: function() { t && t() } }) } ) }
    """
    if trace_id:
        params["traceid"] = random.random_trace_id()
    var1 = {}
    for k, var4 in params.items():
        if k:
            var1[k] = var4

    var2 = {
        "OOOOO0": "OOOO00",
        "O00000": "OOO00O",
        "O0O00O": "OOO000",
        "O000OO": "OOO0OO",
        "O0O000": "O0OOO0"
    }

    var3 = thirteen_digits_time() / 1000
    var4 = int(var3 / 86400) % 5
    var5 = list(var2.keys())
    _ = ""
    if var4 < len(var5):
        _ = var2[var5[var4]]
    if _ in util3.moonshadV3:
        params = {**params, **util3.moonshadV3[_](var1, {})}

    if fuid:
        params["rinfo"] = json.dumps({"fuid": util4.algorithm14(fuid, None, None)})

    return params

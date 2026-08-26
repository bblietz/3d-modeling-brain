#!/usr/bin/env python3
"""Run FreeCAD code over XML-RPC and optionally grab screenshots.

Usage:
  fc.py exec <codefile>            -> prints result dict
  fc.py shot <View> <outfile.png>  -> saves screenshot
"""
import sys, base64, xmlrpc.client

srv = xmlrpc.client.ServerProxy("http://127.0.0.1:9875", allow_none=True)

cmd = sys.argv[1]
if cmd == "exec":
    code = open(sys.argv[2]).read()
    res = srv.execute_code(code)
    print(res)
    if isinstance(res, dict) and not res.get("success", True):
        sys.exit(1)
elif cmd == "shot":
    view, out = sys.argv[2], sys.argv[3]
    b64 = srv.get_active_screenshot(view)
    with open(out, "wb") as f:
        f.write(base64.b64decode(b64))
    print(f"saved {out}")
else:
    sys.exit(f"unknown command {cmd}")

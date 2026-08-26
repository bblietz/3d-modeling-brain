#!/usr/bin/env python3
"""End-to-end smoke test for the FreeCAD MCP system.

Talks directly to the addon's XML-RPC server (same backend the MCP bridge
uses): creates a 10mm cube, captures a screenshot, exports an STL, validates
both, then cleans up. Exit 0 = healthy.
"""
import base64
import os
import struct
import sys
import tempfile
import xmlrpc.client

RPC_URL = "http://127.0.0.1:9875"
DOC = "SmokeTest"


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def rpc_code(srv, code, what):
    res = srv.execute_code(code)
    if not res.get("success"):
        fail(f"{what}: {res.get('error', res)}")
    return res


def main():
    out = tempfile.mkdtemp(prefix="freecad-smoke-")
    try:
        srv = xmlrpc.client.ServerProxy(RPC_URL, allow_none=True)
        if not srv.ping():
            fail("ping returned falsy")
    except Exception as e:
        fail(f"cannot reach RPC server at {RPC_URL}: {e}")
    print("ok: ping")

    # Best-effort: a previous failed run may have left a stale SmokeTest doc
    # open. Close it now so newDocument() doesn't get auto-renamed (e.g.
    # SmokeTest1) and getDocument() below doesn't grab the stale one.
    try:
        srv.execute_code(
            "import FreeCAD\n"
            f"if '{DOC}' in FreeCAD.listDocuments():\n"
            f"    FreeCAD.closeDocument('{DOC}')\n"
        )
    except Exception:
        pass

    try:
        rpc_code(srv, (
            "import FreeCAD\n"
            f"doc = FreeCAD.newDocument('{DOC}')\n"
            "box = doc.addObject('Part::Box', 'TestCube')\n"
            "box.Length = 10\nbox.Width = 10\nbox.Height = 10\n"
            "doc.recompute()\n"
            "FreeCAD.Gui.ActiveDocument.ActiveView.fitAll()\n"
        ), "create cube")
        print("ok: cube created")

        b64 = srv.get_active_screenshot("Isometric", 800, 600)
        if not b64:
            fail("get_active_screenshot returned empty")
        png = base64.b64decode(b64)
        if png[:4] != b"\x89PNG":
            fail("screenshot is not a PNG")
        shot = os.path.join(out, "smoke_screenshot.png")
        with open(shot, "wb") as f:
            f.write(png)
        print(f"ok: screenshot ({len(png)} bytes) -> {shot}")

        stl = os.path.join(out, "test_cube.stl")
        rpc_code(srv, (
            "import FreeCAD, Mesh\n"
            f"doc = FreeCAD.getDocument('{DOC}')\n"
            f"Mesh.export([doc.getObject('TestCube')], '{stl}')\n"
        ), "export STL")
        if not os.path.exists(stl):
            fail("STL file not written")
        data = open(stl, "rb").read()
        if data[:5] == b"solid":
            if b"facet" not in data:
                fail("ASCII STL has no facets")
        else:
            if len(data) < 84:
                fail(f"binary STL too small ({len(data)} bytes)")
            (n,) = struct.unpack("<I", data[80:84])
            if n < 12 or len(data) != 84 + 50 * n:
                fail(f"binary STL malformed: {n} triangles, {len(data)} bytes")
        print(f"ok: STL valid ({len(data)} bytes) -> {stl}")

        print("ok: cleanup")
        print(f"SMOKE TEST PASSED (artifacts in {out})")
    finally:
        # Best-effort: always close the SmokeTest doc, even on failure, so a
        # mid-run error doesn't leak an open document into the next run.
        # Swallow errors here so the original failure message/exit code (if
        # any) from the block above is what the caller sees.
        try:
            srv.execute_code(f"import FreeCAD\nFreeCAD.closeDocument('{DOC}')\n")
        except Exception:
            pass


if __name__ == "__main__":
    main()

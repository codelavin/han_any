"""
han_any - 汉字任意转
Run: python app.py   （或双击 run.bat）
URL: http://localhost:5057
"""
import os
import sys
import threading
import webbrowser

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from flask import Flask, jsonify, request, send_from_directory  # noqa: E402

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 页面与 app.py 同目录（扁平结构，便于 GitHub 一次性上传）
PAGE_DIR = BASE_DIR if os.path.exists(os.path.join(BASE_DIR, "index.html")) \
    else os.path.join(BASE_DIR, "templates")

app = Flask(__name__)


@app.route("/")
def index():
    return send_from_directory(PAGE_DIR, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(PAGE_DIR, filename)


@app.post("/api/convert")
def api_convert():
    from han_any import auto_convert, convert, detect
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "") or ""
    mode = data.get("mode", "s2t")
    auto = bool(data.get("auto"))
    try:
        out = auto_convert(text, mode) if auto else convert(text, mode)
        return jsonify({"ok": True, "result": out, "detect": detect(text)})
    except Exception as e:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(e)}), 400


@app.get("/api/modes")
def api_modes():
    from han_any import MODES
    return jsonify({"ok": True, "modes": MODES})


def main() -> int:
    port = int(os.environ.get("HAN_ANY_PORT", "5057"))
    url = f"http://localhost:{port}"
    print("=" * 52)
    print("  han_any - 汉字任意转")
    print(f"  URL: {url}")
    print("  Python: " + sys.executable)
    print("=" * 52)
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    app.run(host="0.0.0.0", port=port, debug=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

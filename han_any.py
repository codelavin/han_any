# -*- coding: utf-8 -*-
"""
han_any - 汉字任意转（简繁互译核心引擎 + CLI）
han = 汉, any = 任意；手写体里两词互为 180° 旋转对称。

依赖: opencc-python-reimplemented (import opencc), zhconv
"""
from __future__ import annotations

import argparse
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import opencc  # noqa: E402
import zhconv  # noqa: E402

__version__ = "1.0.0"

# OpenCC 模式：字形/地区标准转换（含词汇表）
OPENCC_MODES = {
    "s2t": "简体 → 繁体（通用）",
    "t2s": "繁体 → 简体（通用）",
    "s2tw": "简体 → 台湾正体（字形）",
    "s2twp": "简体 → 台湾正体（含当地用词，如 软件→軟體）",
    "s2hk": "简体 → 香港繁体",
    "tw2s": "台湾正体 → 简体（字形）",
    "tw2sp": "台湾正体 → 简体（含当地用词）",
    "hk2s": "香港繁体 → 简体",
    "t2tw": "繁体 → 台湾正体（标准化）",
    "t2hk": "繁体 → 香港繁体（标准化）",
}

# MediaWiki 地区词模式（zhconv）：更贴近各地用语
ZHCONV_MODES = {
    "zh-cn": "大陆简体（含大陆用词）",
    "zh-tw": "台灣正體（含台灣用詞）",
    "zh-hk": "香港繁體（含香港用詞）",
    "zh-sg": "马新简体",
    "zh-hans": "简体（仅字形）",
    "zh-hant": "繁體（仅字形）",
}

MODES = {**OPENCC_MODES, **ZHCONV_MODES}

# 用于方向推断的常用特征字（只在另一方出现）
_S_ONLY = "体车马门风软件打印机内存鼠标网络视频"
_T_ONLY = "體車馬門風軟體印表機記憶體滑鼠網路視訊"


def convert(text: str, mode: str = "s2t") -> str:
    """核心转换。mode 见 MODES。"""
    if not text:
        return ""
    mode = (mode or "s2t").strip()
    if mode in ZHCONV_MODES:
        return zhconv.convert(text, mode)
    if mode not in OPENCC_MODES:
        raise ValueError(f"未知模式: {mode}，可选: {', '.join(MODES)}")
    return opencc.OpenCC(mode).convert(text)


def detect(text: str) -> str:
    """粗略判断文本倾向：'simplified' / 'traditional' / 'unknown'"""
    s = sum(ch in _S_ONLY for ch in text)
    t = sum(ch in _T_ONLY for ch in text)
    if s == t == 0:
        return "unknown"
    return "traditional" if t > s else "simplified"


def auto_convert(text: str, prefer: str = "s2t") -> str:
    """自动判断方向后转换。prefer 为判定不出时的兜底模式。"""
    d = detect(text)
    if d == "traditional":
        return convert(text, "t2s")
    if d == "simplified":
        return convert(text, "s2t")
    return convert(text, prefer)


def convert_file(src: str, dst: str, mode: str) -> None:
    with open(src, "r", encoding="utf-8") as f:
        text = f.read()
    out = convert(text, mode)
    os.makedirs(os.path.dirname(os.path.abspath(dst)) or ".", exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(out)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="han_any",
        description="han_any 汉字任意转 - 简繁互译（OpenCC + MediaWiki 地区词）",
    )
    p.add_argument("text", nargs="?", help="要转换的文本；省略则从 stdin 读取")
    p.add_argument("-m", "--mode", default="s2t", help="转换模式，默认 s2t；--list 查看全部")
    p.add_argument("-f", "--file", help="输入文件路径（UTF-8）")
    p.add_argument("-o", "--output", help="输出文件路径；不指定则打印到 stdout")
    p.add_argument("-a", "--auto", action="store_true", help="自动判断方向（简↔繁互转）")
    p.add_argument("-d", "--detect", action="store_true", help="仅检测文本倾向")
    p.add_argument("--list", action="store_true", help="列出所有模式")
    p.add_argument("--web", action="store_true", help="启动 WebUI（等同 python server.py）")
    p.add_argument("--version", action="version", version=f"han_any {__version__}")
    args = p.parse_args(argv)

    if args.list:
        print("OpenCC 模式：")
        for k, v in OPENCC_MODES.items():
            print(f"  {k:8s} {v}")
        print("MediaWiki 地区词模式（zhconv）：")
        for k, v in ZHCONV_MODES.items():
            print(f"  {k:8s} {v}")
        return 0

    if args.web:
        from app import main as app_main
        return app_main()

    # 取输入
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    elif args.text is not None:
        text = args.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        p.print_help()
        return 1

    if args.detect:
        print(detect(text))
        return 0

    out = auto_convert(text, args.mode) if args.auto else convert(text, args.mode)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"已写入 {args.output}（{len(out)} 字，模式 {args.mode}）")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

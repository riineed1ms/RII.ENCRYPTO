#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RII ENCRYPTO - terminal text encryption tool.

Encryption uses the substitution table stored in data.json
(one character is replaced by exactly one character).
Text can be typed in directly or read from / written to a text file.
"""

import json
import os
import sys
from pathlib import Path

from colorama import Fore, Style, init as colorama_init

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.json"

VERSION = "V: 1.0.0"
TIKTOK = "@rii_project"
ACCOUNT = "@riineed1mshaujvz"
CHANNEL = "https://whatsapp.com/channel/0029Vb9CF7cLCoX3LWHm0A10"

# ASCII block font (same family as the original banner).
GLYPHS = {
    "R": [
        "██████╗ ",
        "██╔══██╗",
        "██████╔╝",
        "██╔══██╗",
        "██║  ██║",
        "╚═╝  ╚═╝",
    ],
    "I": [
        "██╗",
        "██║",
        "██║",
        "██║",
        "██║",
        "╚═╝",
    ],
    "E": [
        "███████╗",
        "██╔════╝",
        "█████╗  ",
        "██╔══╝  ",
        "███████╗",
        "╚══════╝",
    ],
    "N": [
        "███╗   ██╗",
        "████╗  ██║",
        "██╔██╗ ██║",
        "██║╚██╗██║",
        "██║ ╚████║",
        "╚═╝  ╚═══╝",
    ],
    "C": [
        " ██████╗",
        "██╔════╝",
        "██║     ",
        "██║     ",
        "╚██████╗",
        " ╚═════╝",
    ],
    "Y": [
        "██╗   ██╗",
        "╚██╗ ██╔╝",
        " ╚████╔╝ ",
        "  ╚██╔╝  ",
        "   ██║   ",
        "   ╚═╝   ",
    ],
    "P": [
        "██████╗ ",
        "██╔══██╗",
        "██████╔╝",
        "██╔═══╝ ",
        "██║     ",
        "╚═╝     ",
    ],
    "T": [
        "████████╗",
        "╚══██╔══╝",
        "   ██║   ",
        "   ██║   ",
        "   ██║   ",
        "   ╚═╝   ",
    ],
    "O": [
        " ██████╗ ",
        "██╔═══██╗",
        "██║   ██║",
        "██║   ██║",
        "╚██████╔╝",
        " ╚═════╝ ",
    ],
}

WIDTH = 68  # inner width of every panel


# ---------------------------------------------------------------- core logic
def load_table(path=DATA_FILE):
    """Load data.json and verify that it is a one-to-one table."""
    with open(path, encoding="utf-8") as fh:
        table = json.load(fh)
    values = list(table.values())
    if len(set(values)) != len(values):
        raise ValueError("data.json contains duplicate values; decryption would be ambiguous.")
    return table


def encrypt_text(text, table):
    """Replace every character found in the table; keep all others unchanged."""
    return "".join(table.get(ch, ch) for ch in text)


def decrypt_text(text, table):
    """Reverse of encrypt_text using the same table."""
    reverse = {value: key for key, value in table.items()}
    return "".join(reverse.get(ch, ch) for ch in text)


MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


def is_termux():
    return "com.termux" in os.environ.get("PREFIX", "") or "TERMUX_VERSION" in os.environ


def clean_path(raw):
    """Strip quotes/spaces and expand ~ so pasted paths work."""
    raw = raw.strip().strip('"').strip("'").strip()
    return Path(os.path.expanduser(raw))


def unique_path(path):
    """Return path, or path with _1, _2 ... if it already exists (never overwrite)."""
    if not path.exists():
        return path
    n = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{n}{path.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def output_path(src, mode):
    """encrypt: name.ext -> name.ext.enc ; decrypt: name.ext.enc -> name.ext (else name.ext.dec)"""
    if mode == "encrypt":
        return unique_path(src.with_name(src.name + ".enc"))
    if src.suffix.lower() == ".enc" and src.stem:
        return unique_path(src.with_name(src.stem))
    return unique_path(src.with_name(src.name + ".dec"))


def process_file(src, mode, table):
    """Read a UTF-8 text file, encrypt/decrypt it and write the result next to it.

    Returns (output_path, number_of_characters). Raises ValueError with a
    readable message for problems the user can fix.
    """
    if not src.exists():
        raise ValueError("File not found.")
    if not src.is_file():
        raise ValueError("That path is a folder, not a file.")
    if src.stat().st_size > MAX_FILE_SIZE:
        raise ValueError("File is larger than 20 MB.")
    try:
        with open(src, encoding="utf-8", newline="") as fh:
            text = fh.read()
    except UnicodeDecodeError:
        raise ValueError("Not a UTF-8 text file. Only text files (txt, md, json, py, ...) are supported.")
    except PermissionError:
        raise ValueError("Permission denied while reading the file.")
    func = encrypt_text if mode == "encrypt" else decrypt_text
    result = func(text, table)
    out = output_path(src, mode)
    try:
        with open(out, "w", encoding="utf-8", newline="") as fh:
            fh.write(result)
    except PermissionError:
        raise ValueError("Permission denied while writing the output file.")
    except OSError as exc:
        raise ValueError(f"Cannot write output file: {exc}")
    return out, len(text)


# ---------------------------------------------------------------- rendering
C = Style.BRIGHT + Fore.CYAN
W = Style.BRIGHT + Fore.WHITE
D = Style.NORMAL + Fore.CYAN
R = Style.RESET_ALL


def render_word(word):
    rows = ["", "", "", "", "", ""]
    for letter in word:
        for i, part in enumerate(GLYPHS[letter]):
            rows[i] += part
    return rows


def clear_screen():
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


def line(left, fill, right, title=""):
    if title:
        head = f"{fill} {title} "
        return D + left + head + fill * (WIDTH - len(head)) + right + R
    return D + left + fill * WIDTH + right + R


def row(text="", label=None):
    body = f"  {label:<10}{text}" if label else f"  {text}"
    if len(body) > WIDTH:
        body = body[:2] + "..." + body[-(WIDTH - 5):]
    return D + "│" + W + body.ljust(WIDTH) + D + "│" + R


def panel(title, rows):
    out = [line("┌", "─", "┐", title)]
    out.extend(rows)
    out.append(line("└", "─", "┘"))
    return "\n".join(out)


def banner():
    clear_screen()
    print()
    for r_line in render_word("RII"):
        print(" " + W + r_line + R)
    for e_line in render_word("ENCRYPTO"):
        print(" " + C + e_line + R)
    print()
    info = [
        row(VERSION, "Version"),
        row(TIKTOK, "TikTok"),
        row(ACCOUNT, "Account"),
        row("WhatsApp Channel"),
        row(CHANNEL),
    ]
    print(panel("INFORMATION", info))


def menu():
    items = [
        row("[1]  Encrypt Text"),
        row("[2]  Decrypt Text"),
        row("[3]  Encrypt File"),
        row("[4]  Decrypt File"),
        row("[5]  Exit"),
    ]
    print()
    print(panel("MENU", items))


def result_panel(title, text):
    print()
    print(line("┌", "─", "┐", title))
    chunks = [text[i:i + WIDTH - 4] for i in range(0, len(text), WIDTH - 4)] or [""]
    for chunk in chunks:
        print(D + "│" + W + ("  " + chunk).ljust(WIDTH) + D + "│" + R)
    print(line("└", "─", "┘"))
    print(D + "  Result (raw text, safe to copy):" + R)
    print(W + text + R)


def prompt(label):
    return input("\n" + C + label + R + " " + W)


# ---------------------------------------------------------------- actions
def action_encrypt(table):
    text = prompt("Enter text to encrypt >")
    print(R, end="")
    result_panel("ENCRYPTED OUTPUT", encrypt_text(text, table))


def action_decrypt(table):
    text = prompt("Enter text to decrypt >")
    print(R, end="")
    result_panel("DECRYPTED OUTPUT", decrypt_text(text, table))


def action_file(table, mode):
    word = "encrypt" if mode == "encrypt" else "decrypt"
    print()
    print(D + "  Enter the full path of a text file to " + word + "." + R)
    if is_termux():
        print(D + "  Termux example : ~/storage/downloads/catatan.txt" + R)
        print(D + "  First time?      run  termux-setup-storage  and allow access." + R)
    else:
        print(D + "  Example        : /home/user/catatan.txt  or  C:\\Users\\user\\catatan.txt" + R)
    raw = prompt(f"File to {word} >")
    print(R, end="")
    if not raw.strip():
        print("\n" + Fore.WHITE + "  No path entered." + R)
        return
    src = clean_path(raw)
    try:
        out, count = process_file(src, mode, table)
    except ValueError as exc:
        print("\n" + Fore.WHITE + "  Failed: " + str(exc) + R)
        if str(exc) == "File not found." and is_termux():
            print(D + "  Tip: run  termux-setup-storage  then use ~/storage/downloads/..." + R)
        return
    print()
    print(panel("FILE " + ("ENCRYPTED" if mode == "encrypt" else "DECRYPTED"), [
        row(src.name, "Input"),
        row(out.name, "Output"),
        row(f"{count} characters", "Size"),
        row("Saved in:"),
        row(str(out.parent)),
    ]))


def goodbye():
    print()
    print(panel("RII ENCRYPTO", [
        row("Thank you for using RII ENCRYPTO."),
        row(),
        row(TIKTOK, "TikTok"),
        row(ACCOUNT, "Account"),
        row("WhatsApp Channel"),
        row(CHANNEL),
    ]))
    print()


def main():
    colorama_init()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    try:
        table = load_table()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Failed to load {DATA_FILE.name}: {exc}")
        return 1

    try:
        while True:
            banner()
            menu()
            choice = prompt("Select an option [1-5] >").strip()
            print(R, end="")
            if choice == "1":
                action_encrypt(table)
            elif choice == "2":
                action_decrypt(table)
            elif choice == "3":
                action_file(table, "encrypt")
            elif choice == "4":
                action_file(table, "decrypt")
            elif choice == "5":
                goodbye()
                return 0
            else:
                print("\n" + Fore.WHITE + "  Invalid option. Please choose 1 to 5." + R)

            back = prompt("Return to menu? [y = menu / n = exit] >").strip().lower()
            print(R, end="")
            if back in ("n", "no"):
                goodbye()
                return 0
    except (KeyboardInterrupt, EOFError):
        print(R)
        goodbye()
        return 0


if __name__ == "__main__":
    sys.exit(main())

# RII ENCRYPTO

Terminal text encryption tool with a clean, professional black, cyan and white interface.
Letters, numbers and spaces are substituted using the table in `data.json`, so text encrypted
with this tool can be decrypted again with the same table.

Version: V: 1.0.0

## Features

- Encrypt Text
- Decrypt Text
- Encrypt File: read a text file and save the result as a new file (`name.ext.enc`)
- Decrypt File: read an encrypted file and save the original text (`name.ext`)
- Return to menu or exit after every operation
- Fully compatible with the original `data.json` substitution table

## Requirements

- Python 3.7 or newer
- colorama (listed in `requirements.txt`)

## Installation and Usage

```
pip install -r requirements.txt
python3 rii_encrypto.py
```

On Windows use `python rii_encrypto.py`.

## Encrypt and Decrypt Files

Choose menu `[3] Encrypt File` or `[4] Decrypt File`, then type the full path of the file.

- Only UTF-8 text files are supported (txt, md, json, py, csv, ...). Images, PDF, ZIP and other
  binary files cannot be processed because the table works on text characters.
- The result is saved in the same folder as the input file. An existing file is never overwritten;
  a number is added instead (for example `catatan.txt_1.enc`).
- Encrypt: `catatan.txt` becomes `catatan.txt.enc`. Decrypt: `catatan.txt.enc` becomes `catatan.txt`.
  A file without the `.enc` extension is saved as `name.dec`.

### Termux (Android)

Termux needs permission to read and write phone storage. Run this once and tap Allow:

```
termux-setup-storage
```

After that your phone folders are available at `~/storage/`:

| Path                   | Folder on the phone |
| ---------------------- | ------------------- |
| `~/storage/downloads/` | Download            |
| `~/storage/shared/`    | Internal storage    |
| `~/storage/dcim/`      | DCIM                |

Example path: `~/storage/downloads/catatan.txt`. The output file appears in the same folder, so you
can open it with any file manager. Files kept only inside the Termux home folder are not visible to
other Android apps.

## Project Structure

| File               | Description                                  |
| ------------------ | -------------------------------------------- |
| `rii_encrypto.py`  | Main program (banner, menu, encrypt, decrypt) |
| `data.json`        | Substitution table (unchanged)               |
| `requirements.txt` | Python dependencies                          |
| `test_rii_encrypto.py` | Automated tests (`python3 test_rii_encrypto.py`) |
| `LICENSE`          | Original license (Boost Software License 1.0) |

## Notes

Characters that are not in `data.json` (for example punctuation) are kept as they are.
Do not include characters from the encrypted alphabet (such as accented letters used by the
table) in your original text, because they would be converted back during decryption.

## Creator

- TikTok: @rii_project
- Account: @riineed1mshaujvz
- WhatsApp Channel: https://whatsapp.com/channel/0029Vb9CF7cLCoX3LWHm0A10

This project is derived from Black-Encrypto and keeps its original license.

import json
import tempfile
import unittest
from pathlib import Path

import rii_encrypto as m

TABLE = json.load(open(Path(__file__).parent / "data.json", encoding="utf-8"))


def original_encrypt(text, data):
    enc = ""
    for i in text:
        for j in data.keys():
            if i == j:
                enc = enc + data.get(i)
        if i not in data.keys():
            enc = enc + i
    return enc


def original_decrypt(text, data):
    dec = ""
    for i in text:
        for key, value in data.items():
            if i == value:
                dec = dec + key
        if i not in data.values():
            dec = dec + i
    return dec


class Tests(unittest.TestCase):
    samples = ["Hello World 123", "RII ENCRYPTO V 1.0.0", "abc XYZ 0987654321",
               "teks, dengan! tanda? baca.", "", "   "]

    def test_matches_original_algorithm(self):
        t = m.load_table()
        for s in self.samples:
            self.assertEqual(m.encrypt_text(s, t), original_encrypt(s, TABLE))
            self.assertEqual(m.decrypt_text(s, t), original_decrypt(s, TABLE))

    def test_roundtrip(self):
        t = m.load_table()
        for s in self.samples:
            self.assertEqual(m.decrypt_text(m.encrypt_text(s, t), t), s)

    def test_known_values(self):
        t = m.load_table()
        self.assertEqual(m.encrypt_text("Aa", t), "Çü")

    def test_all_table_chars(self):
        t = m.load_table()
        s = "".join(t.keys())
        self.assertEqual(m.decrypt_text(m.encrypt_text(s, t), t), s)

    def test_file_roundtrip(self):
        t = m.load_table()
        original = "Catatan Rahasia 2026\r\nBaris kedua, ada tanda baca!\n\nAkhir."
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "catatan.txt"
            src.write_bytes(original.encode("utf-8"))
            enc, count = m.process_file(src, "encrypt", t)
            self.assertEqual(enc.name, "catatan.txt.enc")
            self.assertEqual(count, len(original))
            self.assertEqual(enc.read_bytes().decode("utf-8"), m.encrypt_text(original, t))
            src.unlink()
            dec, _ = m.process_file(enc, "decrypt", t)
            self.assertEqual(dec.name, "catatan.txt")
            self.assertEqual(dec.read_bytes().decode("utf-8"), original)

    def test_file_never_overwrites(self):
        t = m.load_table()
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "a.txt"
            src.write_text("halo", encoding="utf-8")
            first, _ = m.process_file(src, "encrypt", t)
            second, _ = m.process_file(src, "encrypt", t)
            self.assertNotEqual(first, second)
            self.assertTrue(first.exists() and second.exists())

    def test_file_errors(self):
        t = m.load_table()
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                m.process_file(Path(tmp) / "tidak-ada.txt", "encrypt", t)
            with self.assertRaises(ValueError):
                m.process_file(Path(tmp), "encrypt", t)
            binf = Path(tmp) / "x.bin"
            binf.write_bytes(b"\xff\xfe\x00\x80\x81")
            with self.assertRaises(ValueError):
                m.process_file(binf, "encrypt", t)


if __name__ == "__main__":
    unittest.main()

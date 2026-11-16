"""Test akceptacyjny na działającym emulatorze z zainstalowanym AeroRun."""
import argparse
from datetime import datetime, timedelta
import os
from pathlib import Path
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", default="emulator-5554")
    args = parser.parse_args()
    sdk = os.getenv("ANDROID_HOME")
    adb = str(Path(sdk) / "platform-tools" / ("adb.exe" if os.name == "nt" else "adb")) if sdk else "adb"

    def shell(*command):
        return subprocess.check_output([adb, "-s", args.device, "shell", *command], timeout=20).decode("utf-8")

    def tree():
        shell("uiautomator", "dump", "/sdcard/aerorun-window.xml")
        return list(ET.fromstring(shell("cat", "/sdcard/aerorun-window.xml")).iter("node"))

    def label(node):
        return node.get("content-desc") or node.get("text") or ""

    def wait_for(text):
        end = time.monotonic() + 60
        while time.monotonic() < end:
            nodes = tree()
            for node in nodes:
                if text in label(node):
                    return node
            time.sleep(1)
        raise RuntimeError(f"Brak elementu {text!r}. Widoczne: {[label(n) for n in nodes if label(n)][:12]}")

    def tap(text):
        node = wait_for(text)
        x1, y1, x2, y2 = map(int, re.findall(r"\d+", node.get("bounds")))
        shell("input", "tap", str((x1 + x2) // 2), str((y1 + y2) // 2))

    shell("am", "force-stop", "pl.aerorun.mobile")
    shell("am", "start", "-n", "pl.aerorun.mobile/.MainActivity")
    for offset, day in ((1, "JUTRO"), (0, "DZISIAJ")):
        tap(day)
        tap("SPRAWDŹ")
        expected = datetime.now(ZoneInfo("Europe/Warsaw")).date() + timedelta(days=offset)
        wait_for("00:00")
        visible = [label(n) for n in tree()]
        assert any("/100" in text or "BRAK DANYCH" in text for text in visible), visible
        assert not any(word in text for text in visible for word in ("PM10", "Temperatura", "Wiatr", "Opady", "AeroRun", "Score ·", str(expected))), visible
        tap("00:00")
        for name in ("PM10 · średnia dobowa", "Temperatura", "Wiatr", "Opady"):
            wait_for(name)
        tap("00:00")
        assert not any("PM10" in label(n) for n in tree())
        print(day, expected, "OK")


if __name__ == "__main__":
    main()

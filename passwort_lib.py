import os
import json
from cryptography.fernet import Fernet

# === Schlüsselverwaltung ===
def lade_key():
    if not os.path.exists("key.key"):
        key = Fernet.generate_key()
        with open("key.key", "wb") as f:
            f.write(key)
    with open("key.key", "rb") as f:
        return f.read()

fernet = Fernet(lade_key())

PIN_DATEI = "pin.txt"
DATEINAME = "passwoerter.json"

# === PIN prüfen ===
def pin_pruefen(pin):
    if not os.path.exists(PIN_DATEI):
        return False
    try:
        with open(PIN_DATEI, "r") as f:
            verschluesselt = f.read().strip()
        gespeicherter_pin = fernet.decrypt(verschluesselt.encode()).decode()
        return pin == gespeicherter_pin
    except:
        return False

# === Daten laden ===
def lade_daten():
    if not os.path.exists(DATEINAME):
        return {}
    try:
        with open(DATEINAME, "r") as f:
            daten = json.load(f)
        for dienst in daten:
            daten[dienst]["passwort"] = fernet.decrypt(daten[dienst]["passwort"].encode()).decode()
        return daten
    except:
        return {}

# === Daten speichern ===
def speichere_daten(daten):
    daten_enc = {}
    for dienst, eintrag in daten.items():
        daten_enc[dienst] = {
            "benutzername": eintrag["benutzername"],
            "kategorie": eintrag["kategorie"],
            "passwort": fernet.encrypt(eintrag["passwort"].encode()).decode()
        }
    with open(DATEINAME, "w") as f:
        json.dump(daten_enc, f, indent=4)

# === Passwortoperationen ===
def passwort_hinzufuegen(dienst, benutzername, passwort, kategorie):
    daten = lade_daten()
    daten[dienst] = {"benutzername": benutzername, "passwort": passwort, "kategorie": kategorie}
    speichere_daten(daten)

def passwort_loeschen(dienst):
    daten = lade_daten()
    if dienst in daten:
        del daten[dienst]
        speichere_daten(daten)

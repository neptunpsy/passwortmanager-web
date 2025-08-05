import os
import json
from cryptography.fernet import Fernet

# === Schlüsselverwaltung ===
def erstelle_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

def lade_key():
    if not os.path.exists("key.key"):
        erstelle_key()
    with open("key.key", "rb") as key_file:
        return key_file.read()

fernet = Fernet(lade_key())

# === PIN-Verwaltung ===
PIN_DATEI = "pin.txt"

def master_pin_setzen():
    if not os.path.exists(PIN_DATEI):
        pin = input("Neuen Master-PIN festlegen: ").strip()
        verschluesselt = fernet.encrypt(pin.encode()).decode()
        with open(PIN_DATEI, "w") as f:
            f.write(verschluesselt)
        print("🔐 Master-PIN wurde verschlüsselt gespeichert.")

def master_pin_abfragen():
    if not os.path.exists(PIN_DATEI):
        print("⚠ Kein Master-PIN gefunden.")
        return False

    with open(PIN_DATEI, "r") as f:
        verschluesselt = f.read().strip()
        try:
            richtiger_pin = fernet.decrypt(verschluesselt.encode()).decode()
        except Exception:
            print("❌ Fehler beim Entschlüsseln des Master-PINs.")
            return False

    for versuch in range(3):
        eingabe = input("Master-PIN eingeben: ").strip()
        if eingabe == richtiger_pin:
            return True
        else:
            print("❌ Falscher PIN.")
    return False

# === Daten laden und speichern ===
DATEINAME = "passwoerter.json"

def lade_daten():
    if os.path.exists(DATEINAME):
        with open(DATEINAME, "r") as f:
            try:
                daten = json.load(f)
                # Passwörter entschlüsseln
                for dienst in daten:
                    verschluesselt = daten[dienst]["passwort"]
                    entschluesselt = fernet.decrypt(verschluesselt.encode()).decode()
                    daten[dienst]["passwort"] = entschluesselt
                return daten
            except Exception as e:
                print(f"Fehler beim Laden der Datei: {e}")
                return {}
    else:
        print("Datei nicht gefunden – neue wird erstellt.")
        return {}

def speichere_daten(daten):
    daten_verschluesselt = {}
    for dienst, eintrag in daten.items():
        verschluesselt = fernet.encrypt(eintrag["passwort"].encode()).decode()
        daten_verschluesselt[dienst] = {
            "benutzername": eintrag["benutzername"],
            "kategorie": eintrag["kategorie"],
            "passwort": verschluesselt
        }

    with open(DATEINAME, "w") as f:
        json.dump(daten_verschluesselt, f, indent=4)

# === Funktionen ===
def passwort_hinzufuegen(daten):
    dienst = input("Dienstname: ").strip()
    benutzer = input("Benutzername: ").strip()
    passwort = input("Passwort: ").strip()
    kategorie = input("Kategorie: ").strip()

    daten[dienst] = {
        "benutzername": benutzer,
        "passwort": passwort,
        "kategorie": kategorie
    }
    print(f"✔ Passwort für '{dienst}' hinzugefügt.")

def passwort_suchen(daten):
    begriff = input("Suche nach Dienstname oder Kategorie: ").strip().lower()
    gefunden = False
    for dienst, eintrag in daten.items():
        if begriff in dienst.lower() or begriff in eintrag["kategorie"].lower():
            print(f"🔎 Dienst: {dienst}")
            print(f"   Benutzername: {eintrag['benutzername']}")
            print(f"   Kategorie: {eintrag['kategorie']}")
            print(f"   Passwort: {eintrag['passwort']}")
            print("-" * 20)
            gefunden = True
    if not gefunden:
        print("Keine passenden Einträge gefunden.")

def passwort_loeschen(daten):
    dienst = input("Dienstname zum Löschen: ").strip()
    if dienst in daten:
        del daten[dienst]
        print(f"🗑 Passwort für '{dienst}' gelöscht.")
    else:
        print("Kein Eintrag gefunden.")

# === Menü ===
def hauptmenue(daten):
    while True:
        print("\n=== Passwortmanager ===")
        print("1. Passwort suchen")
        print("2. Passwort hinzufügen")
        print("3. Passwort löschen")
        print("4. Beenden")
        wahl = input("Wähle (1–4): ")

        if wahl == "1":
            passwort_suchen(daten)
        elif wahl == "2":
            passwort_hinzufuegen(daten)
            speichere_daten(daten)
        elif wahl == "3":
            passwort_loeschen(daten)
            speichere_daten(daten)
        elif wahl == "4":
            speichere_daten(daten)
            print("📁 Daten gespeichert. Programm beendet.")
            break
        else:
            print("Ungültige Eingabe.")

# === Startpunkt ===
if __name__ == "__main__":
    master_pin_setzen()
    if master_pin_abfragen():
        daten = lade_daten()
        hauptmenue(daten)
    else:
        print("🚫 Zugriff verweigert.")

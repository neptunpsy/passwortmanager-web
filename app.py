from flask import Flask, render_template, request, redirect, url_for, session
from passwort_lib import lade_daten, passwort_hinzufuegen, passwort_loeschen, pin_pruefen

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Ändere das!

# === Login ===
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pin = request.form["pin"]
        if pin_pruefen(pin):
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", fehler="Falscher PIN!")
    return render_template("login.html")

# === Dashboard ===
@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    daten = lade_daten()
    return render_template("index.html", daten=daten)

# === Passwort hinzufügen ===
@app.route("/add", methods=["POST"])
def add_passwort():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    dienst = request.form["dienst"]
    benutzername = request.form["benutzername"]
    passwort = request.form["passwort"]
    kategorie = request.form["kategorie"]
    passwort_hinzufuegen(dienst, benutzername, passwort, kategorie)
    return redirect(url_for("dashboard"))

# === Passwort löschen ===
@app.route("/delete/<dienst>")
def delete_passwort(dienst):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    passwort_loeschen(dienst)
    return redirect(url_for("dashboard"))

# === Logout ===
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)

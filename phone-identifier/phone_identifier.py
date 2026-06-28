import tkinter as tk
from tkinter import ttk, messagebox
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import phonenumbers.phonenumberutil as pnu

# ── Couleurs & style ──────────────────────────────────────────────
BG        = "#1a1a2e"
CARD      = "#16213e"
ACCENT    = "#0f3460"
HIGHLIGHT = "#e94560"
TEXT      = "#eaeaea"
SUBTEXT   = "#a0a0b0"
GREEN     = "#4ade80"
RED       = "#f87171"
YELLOW    = "#fbbf24"

FONT_TITLE  = ("Segoe UI", 20, "bold")
FONT_LABEL  = ("Segoe UI", 11)
FONT_SMALL  = ("Segoe UI", 9)
FONT_RESULT = ("Segoe UI", 12)
FONT_MONO   = ("Consolas", 13)

# ── Données résultat ──────────────────────────────────────────────
result_fields = [
    ("🌍 Pays",      "country"),
    ("📡 Opérateur", "carrier"),
    ("🕐 Fuseau",    "timezone"),
    ("📋 Type",      "type"),
    ("✅ Statut",    "status"),
    ("🔢 Format E164","e164"),
    ("📞 Format Int.","intl"),
    ("📱 Format Nat.","national"),
]

def get_number_type(num_type):
    types = {
        phonenumbers.PhoneNumberType.MOBILE:          "Mobile",
        phonenumbers.PhoneNumberType.FIXED_LINE:      "Fixe",
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixe ou Mobile",
        phonenumbers.PhoneNumberType.TOLL_FREE:       "Numéro gratuit",
        phonenumbers.PhoneNumberType.PREMIUM_RATE:    "Numéro surtaxé",
        phonenumbers.PhoneNumberType.VOIP:            "VoIP",
        phonenumbers.PhoneNumberType.UNKNOWN:         "Inconnu",
    }
    return types.get(num_type, "Autre")

def analyse(number_str):
    try:
        parsed = phonenumbers.parse(number_str, None)
    except Exception:
        return None, "Numéro invalide ou format incorrect.\nExemple : +33 6 12 34 56 78"

    if not phonenumbers.is_valid_number(parsed):
        return None, "Ce numéro n'est pas valide."

    possible = phonenumbers.is_possible_number(parsed)
    country  = geocoder.description_for_number(parsed, "fr") or "Inconnu"
    op       = carrier.name_for_number(parsed, "fr") or "Non disponible"
    tz       = ", ".join(timezone.time_zones_for_number(parsed)) or "Inconnu"
    ntype    = get_number_type(phonenumbers.number_type(parsed))
    e164     = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    intl     = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    natl     = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
    status   = "✅ Valide" if possible else "⚠️ Possible"

    data = {
        "country":  country,
        "carrier":  op,
        "timezone": tz,
        "type":     ntype,
        "status":   status,
        "e164":     e164,
        "intl":     intl,
        "national": natl,
    }
    return data, None

# ── Application ───────────────────────────────────────────────────
class PhoneApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Phone Identifier")
        self.geometry("540x660")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._build_ui()

    def _build_ui(self):
        # Titre
        tk.Label(self, text="📞 Phone Identifier",
                 font=FONT_TITLE, bg=BG, fg=HIGHLIGHT).pack(pady=(28, 4))
        tk.Label(self, text="Identifiez n'importe quel numéro de téléphone",
                 font=FONT_SMALL, bg=BG, fg=SUBTEXT).pack()

        # Champ de saisie
        frame_in = tk.Frame(self, bg=BG)
        frame_in.pack(pady=20, padx=30, fill="x")

        tk.Label(frame_in, text="Entrez un numéro avec l'indicatif pays :",
                 font=FONT_LABEL, bg=BG, fg=TEXT).pack(anchor="w")

        self.entry = tk.Entry(frame_in, font=FONT_MONO, bg=CARD, fg=TEXT,
                              insertbackground=TEXT, relief="flat",
                              highlightthickness=2, highlightcolor=HIGHLIGHT,
                              highlightbackground=ACCENT)
        self.entry.pack(fill="x", ipady=10, pady=(6, 0))
        self.entry.insert(0, "+33 6 12 34 56 78")
        self.entry.bind("<FocusIn>",  self._clear_placeholder)
        self.entry.bind("<Return>",   lambda e: self._search())

        tk.Label(frame_in, text="Exemples : +1 415 555 0100  |  +44 7911 123456  |  +33612345678",
                 font=FONT_SMALL, bg=BG, fg=SUBTEXT).pack(anchor="w", pady=(4, 0))

        # Bouton
        self.btn = tk.Button(self, text="🔍  Analyser",
                             font=("Segoe UI", 12, "bold"),
                             bg=HIGHLIGHT, fg="white", activebackground="#c73652",
                             activeforeground="white", relief="flat",
                             cursor="hand2", command=self._search)
        self.btn.pack(pady=4, ipadx=20, ipady=8)

        # Zone résultats
        self.card = tk.Frame(self, bg=CARD, bd=0)
        self.card.pack(padx=30, pady=16, fill="both", expand=True)

        self.label_vars = {}
        for i, (label, key) in enumerate(result_fields):
            row = tk.Frame(self.card, bg=CARD)
            row.pack(fill="x", padx=16, pady=5)

            tk.Label(row, text=label, font=FONT_LABEL, bg=CARD,
                     fg=SUBTEXT, width=18, anchor="w").pack(side="left")

            var = tk.StringVar(value="—")
            lbl = tk.Label(row, textvariable=var, font=FONT_RESULT,
                           bg=CARD, fg=TEXT, anchor="w")
            lbl.pack(side="left", fill="x", expand=True)
            self.label_vars[key] = (var, lbl)

        # Erreur
        self.err_var = tk.StringVar()
        self.err_lbl = tk.Label(self, textvariable=self.err_var,
                                font=FONT_SMALL, bg=BG, fg=RED, wraplength=480)
        self.err_lbl.pack()

        # Pied
        tk.Label(self, text="Propulsé par la librairie phonenumbers de Google",
                 font=FONT_SMALL, bg=BG, fg=SUBTEXT).pack(side="bottom", pady=10)

    def _clear_placeholder(self, event):
        if self.entry.get() == "+33 6 12 34 56 78":
            self.entry.delete(0, "end")

    def _reset_fields(self):
        for var, lbl in self.label_vars.values():
            var.set("—")
            lbl.config(fg=TEXT)

    def _search(self):
        self.err_var.set("")
        self._reset_fields()
        number = self.entry.get().strip()
        if not number or number == "+33 6 12 34 56 78":
            self.err_var.set("Veuillez entrer un numéro de téléphone.")
            return

        data, err = analyse(number)
        if err:
            self.err_var.set(err)
            return

        for key, value in data.items():
            var, lbl = self.label_vars[key]
            var.set(value)
            if key == "status":
                lbl.config(fg=GREEN if "Valide" in value else YELLOW)
            elif key == "carrier" and value == "Non disponible":
                lbl.config(fg=SUBTEXT)
            else:
                lbl.config(fg=TEXT)

if __name__ == "__main__":
    app = PhoneApp()
    app.mainloop()

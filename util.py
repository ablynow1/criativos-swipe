import re, datetime, unicodedata
HOJE = datetime.date(2026, 9, 26)
MESES = {"jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6, "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12}
def data_pt(s):
    m = re.search(r"(\d{1,2}) de (\w{3})\w* de (\d{4})", s or "")
    if not m: return None
    return datetime.date(int(m.group(3)), MESES.get(m.group(2).lower()[:3], 1), int(m.group(1)))
def dias(s):
    d = data_pt(s); return (HOJE - d).days if d else None
def num_tot(s):
    m = re.search(r"([\d.]+)", s or ""); return int(m.group(1).replace(".", "")) if m else 0
def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if unicodedata.category(c) != "Mn")
def dominio(u):
    m = re.match(r"https?://([^/?#]+)", u or ""); return (m.group(1).lower().removeprefix("www.") if m else "")

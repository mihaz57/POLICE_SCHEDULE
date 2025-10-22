
import json
from pathlib import Path

J, D, N_ight, O, A = "J","D","N","O","A"
BASE_CYCLE = [J, J, D, D, N_ight, N_ight, O, O]


def load_all(path="data.json"):
    js = json.loads(Path(path).read_text(encoding="utf-8"))

    NUM_OFF = int(js.get("officers", {}).get("count"))
    names = js.get("officers", {}).get("names") 
    

    DAYS = int(js.get("planning", {}).get("days"))
    WEEKDAY_NAMES = js.get("planning", {}).get("weekday_names")
    WEEKEND_IDX = {5, 6}

    labels_csv = js.get("shifts", {}).get("labels_csv")
    min_staff  = js.get("shifts", {}).get("min_staff")

    ga = js.get("ga", {})
    POP_SIZE  = int(ga.get("pop_size"))
    GENS      = int(ga.get("gens"))
    TOURN_K   = int(ga.get("tourn_k"))
    MUT_RATE  = float(ga.get("mut_rate"))
    CROSS_RATE= float(ga.get("cross_rate"))
    ELITISM   = int(ga.get("elitism"))

    pen = js.get("penalties", {})
    W_MIN_STAFF     = int(pen.get("W_MIN_STAFF"))
    W_N_TO_M        = int(pen.get("W_N_TO_M"))
    W_ONE_PER_DAY   = int(pen.get("W_ONE_PER_DAY"))
    W_ABSENCE       = int(pen.get("W_ABSENCE"))
    W_CYCLE         = int(pen.get("W_CYCLE"))
    W_BAL_NIGHTS    = int(pen.get("W_BAL_NIGHTS"))
    W_BAL_WEEKENDS  = int(pen.get("W_BAL_WEEKENDS"))
    W_MAX_CONSEC    = int(pen.get("W_MAX_CONSEC"))
    MAX_CONSEC_WORK = int(pen.get("MAX_CONSEC_WORK"))

    name_to_idx = {nm: i for i, nm in enumerate(names)}
    raw_abs = js.get("absences", {}) or {}

    absences = {
    name_to_idx[name]: {int(d) - 1 for d in days if 1 <= int(d) <= DAYS}
    for name, days in raw_abs.items()
    }

    cfg = {
        "NUM_OFFICERS": NUM_OFF, "DAYS": DAYS, "WEEKDAY_NAMES": WEEKDAY_NAMES, "WEEKEND_IDX": WEEKEND_IDX,
        "J": J, "D": D, "N": N_ight, "O": O, "A": A, "BASE_CYCLE": BASE_CYCLE, "CYCLE_LEN": len(BASE_CYCLE),
        "labels_csv": labels_csv, "min_staff": min_staff,
        "POP_SIZE": POP_SIZE, "GENS": GENS, "TOURN_K": TOURN_K, "MUT_RATE": MUT_RATE, "CROSS_RATE": CROSS_RATE, "ELITISM": ELITISM,
        "W_MIN_STAFF": W_MIN_STAFF, "W_N_TO_M": W_N_TO_M, "W_ONE_PER_DAY": W_ONE_PER_DAY, "W_ABSENCE": W_ABSENCE,
        "W_CYCLE": W_CYCLE, "W_BAL_NIGHTS": W_BAL_NIGHTS, "W_BAL_WEEKENDS": W_BAL_WEEKENDS,
        "W_MAX_CONSEC": W_MAX_CONSEC, "MAX_CONSEC_WORK": MAX_CONSEC_WORK
    }
    return cfg, names, absences


import csv

def day_headers(cfg):
    return [f"Dan{d+1} {cfg['WEEKDAY_NAMES'][d%7]}" for d in range(cfg["DAYS"])]

def print_by_day(schedule, cfg, names):
    print("\nRASPORED PO DANIMA:")
    NUM = cfg["NUM_OFFICERS"]; DAYS = cfg["DAYS"]; J=cfg["J"]; D=cfg["D"]; N_ight=cfg["N"]
    for d in range(DAYS):
        j_list, d_list, n_list = [], [], []
        for p in range(NUM):
            s = schedule[p][d]
            if s == J: j_list.append(names[p])
            elif s == D: d_list.append(names[p])
            elif s == N_ight: n_list.append(names[p])
        print(f"Dan{d+1:02d}: Jutro={','.join(j_list) or '-'} | Dan={','.join(d_list) or '-'} | Noć={','.join(n_list) or '-'}")

def per_officer_stats(schedule, cfg, p):
    J=cfg["J"]; D=cfg["D"]; N_ight=cfg["N"]; O=cfg["O"]; A=cfg["A"]
    DAYS = cfg["DAYS"]
    cntJ = sum(1 for d in range(DAYS) if schedule[p][d] == J)
    cntD = sum(1 for d in range(DAYS) if schedule[p][d] == D)
    cntN = sum(1 for d in range(DAYS) if schedule[p][d] == N_ight)
    cntO = sum(1 for d in range(DAYS) if schedule[p][d] == O)
    cntA = sum(1 for d in range(DAYS) if schedule[p][d] == A)
    weekend = sum(1 for d in range(DAYS) if (d%7) in cfg["WEEKEND_IDX"] and schedule[p][d] not in (O, A))
    consec = 0; max_consec = 0
    for d in range(DAYS):
        if schedule[p][d] in (O, A): consec = 0
        else: consec += 1; max_consec = max(max_consec, consec)
    return {"J":cntJ,"D":cntD,"N":cntN,"O":cntO,"A":cntA,"WeekendShifts":weekend,"MaxConsec":max_consec}

def count_personal_violations(schedule, cfg, absences, p):
    J=cfg["J"]; N_ight=cfg["N"]; O=cfg["O"]; A=cfg["A"]; DAYS=cfg["DAYS"]
    v = 0
    for d in range(DAYS):
        s = schedule[p][d]
        if d in absences.get(p, set()) and s != A: v += 1
        if d > 0 and schedule[p][d-1] == N_ight and s == J: v += 1
        if s not in (J, cfg["D"], N_ight, O, A): v += 1
    return v

def build_analysis_matrix(schedule, cfg, absences, names):
    header = ["Policajac\\Dan"] + day_headers(cfg) + ["Jutro","Dan","Noć","Slobodan","GO","Noćne smjene","Vikend smjene","Maks. uzastopno","Kršenja"]
    rows = [header]
    for p in range(cfg["NUM_OFFICERS"]):
        labels = [cfg["labels_csv"].get(schedule[p][d], schedule[p][d]) for d in range(cfg["DAYS"])]
        st = per_officer_stats(schedule, cfg, p)
        viol = count_personal_violations(schedule, cfg, absences, p)
        summary = [st["J"], st["D"], st["N"], st["O"], st["A"], st["N"], st["WeekendShifts"], st["MaxConsec"], viol]
        rows.append([names[p]] + labels + [str(x) for x in summary])
    return rows

def save_schedule_csv(schedule, cfg, names, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Policajac\\Dan"] + [f"Dan{d+1}" for d in range(cfg["DAYS"])])
        for p in range(cfg["NUM_OFFICERS"]):
            row = [names[p]] + [cfg["labels_csv"].get(schedule[p][d], schedule[p][d]) for d in range(cfg["DAYS"])]
            w.writerow(row)

def save_matrix_csv(matrix, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for row in matrix:
            w.writerow(row)

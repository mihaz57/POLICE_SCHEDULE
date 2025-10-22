
import json, time, csv, statistics
from pathlib import Path
from data import load_all
from ga import run_ga
from greedy import build_greedy
from fitness import validate_hard
from export import build_analysis_matrix, save_schedule_csv, save_matrix_csv

def _stats(sched, cfg):  
    N, D = cfg["NUM_OFFICERS"], cfg["DAYS"]
    Ncode, O, A = cfg["N"], cfg["O"], cfg["A"]
    ns, ws, ms = [], [], []
    for p in range(N):
        ns.append(sum(1 for d in range(D) if sched[p][d] == Ncode))
        ws.append(sum(1 for d in range(D) if (d % 7) in cfg["WEEKEND_IDX"] and sched[p][d] not in (O, A)))
        c = 0; m = 0
        for d in range(D):
            if sched[p][d] in (O, A): c = 0
            else: c += 1; m = max(m, c)
        ms.append(m)
    std_n = statistics.pstdev(ns) if N > 1 else 0.0
    std_w = statistics.pstdev(ws) if N > 1 else 0.0
    avg_mc = sum(ms) / N
    return std_n, std_w, avg_mc

def _save_errors(errs, path: Path):
    path.write_text("Nema kršenja tvrdih pravila.\n" if not errs else "\n".join(
        f"{i+1:02d}. {e}" for i, e in enumerate(errs)
    ), encoding="utf-8")

if __name__ == "__main__":
    
    BASE_DIR = Path(__file__).parent  
    DATA_FILE = BASE_DIR / "data.json"  

    cfg, names, absences = load_all(DATA_FILE)


   
    js = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    run = js["run"]                       
    algo = run["algo"].upper()            
    seed = run["seed"]                    
    ga_gens = run["gens"]                 
    outdir = Path(run["out"])             
    outdir.mkdir(parents=True, exist_ok=True)

    rows = []

    
    if algo in ("GA", "BOTH"):
        t0 = time.time()
        ga_sched, ga_fit = run_ga(cfg, absences, gens=ga_gens, seed=seed)
        ga_time = time.time() - t0
        ga_errs = validate_hard(ga_sched, cfg, absences)
        save_schedule_csv(ga_sched, cfg, names, outdir / "solution_GA.csv")
        save_matrix_csv(build_analysis_matrix(ga_sched, cfg, absences, names), outdir / "solution_GA_tablica.csv")
        _save_errors(ga_errs, outdir / "krsenja_GA.txt")
        ga_std_n, ga_std_w, ga_avg_mc = _stats(ga_sched, cfg)
        rows.append({"algoritam":"GA","fitness":ga_fit,"time":ga_time,"viol":len(ga_errs),
                     "std_n":ga_std_n,"std_w":ga_std_w,"avg_mc":ga_avg_mc})

    
    if algo in ("GREEDY", "BOTH"):
        t0 = time.time()
        gr_sched, gr_fit = build_greedy(cfg, absences, seed=seed)
        gr_time = time.time() - t0
        gr_errs = validate_hard(gr_sched, cfg, absences)
        save_schedule_csv(gr_sched, cfg, names, outdir / "solution_GREEDY.csv")
        save_matrix_csv(build_analysis_matrix(gr_sched, cfg, absences, names), outdir / "solution_GREEDY_tablica.csv")
        _save_errors(gr_errs, outdir / "krsenja_GREEDY.txt")
        gr_std_n, gr_std_w, gr_avg_mc = _stats(gr_sched, cfg)
        rows.append({"algoritam":"GREEDY","fitness":gr_fit,"time":gr_time,"viol":len(gr_errs),
                     "std_n":gr_std_n,"std_w":gr_std_w,"avg_mc":gr_avg_mc})

    
    with open(outdir / "usporedba_metoda.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["algoritam","fitness","kršenja_tvrda","vrijeme_s","std_noćne","std_vikend","prosjek_maks_uzastopno"])
        for r in rows:
            w.writerow([r["algoritam"], f"{r['fitness']:.0f}", r["viol"],
                        f"{r['time']:.2f}", f"{r['std_n']:.3f}", f"{r['std_w']:.3f}", f"{r['avg_mc']:.2f}"])

    
    print("Algoritmi su zavrseni!")

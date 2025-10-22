

import random
from collections import Counter
from fitness import fitness
from ga import repair_daywise  

def build_greedy(cfg, absences, seed=None):
    if seed is not None:
        random.seed(seed)

    N, D = cfg["NUM_OFFICERS"], cfg["DAYS"]
    J, Dv, Ng, O, A = cfg["J"], cfg["D"], cfg["N"], cfg["O"], cfg["A"]
    min_staff = cfg["min_staff"]
    base_cycle = cfg["BASE_CYCLE"]
    cycle_len = cfg["CYCLE_LEN"]

    def is_weekend(day_idx):
        return (day_idx % 7) in cfg["WEEKEND_IDX"]

    
    sched = [[O for _ in range(D)] for _ in range(N)]
    for p, days in absences.items():
        for d in days:
            if 0 <= d < D:
                sched[p][d] = A

    
    nights = [0] * N
    weekends = [0] * N
    consec = [0] * N
    max_consec = [0] * N

    def local_cost(p, d, s):
        cost = 0.0
        base = base_cycle[(d) % cycle_len]
        if s != base:
            cost += cfg["W_CYCLE"]

        if s == Ng:
            cost += (nights[p] + 1 - min(nights)) * cfg["W_BAL_NIGHTS"]

        if is_weekend(d) and s not in (O, A):
            cost += (weekends[p] + 1 - min(weekends)) * cfg["W_BAL_WEEKENDS"]

        nxt_consec = consec[p] + 1
        if nxt_consec > cfg["MAX_CONSEC_WORK"]:
            cost += (nxt_consec - cfg["MAX_CONSEC_WORK"]) * cfg["W_MAX_CONSEC"]

        return cost
    shift_order = [Ng, Dv, J]

    for d in range(D):
        need = {s: int(min_staff.get(s, 0)) for s in (J, Dv, Ng)}
        counts = Counter(sched[p][d] for p in range(N))
        for s in (J, Dv, Ng):
            need[s] = max(0, need[s] - counts.get(s, 0))

        picked_today = set(p for p in range(N) if sched[p][d] not in (O, A))

        for s in shift_order:
            while need[s] > 0:
                cand = []
                for p in range(N):
                    if sched[p][d] != O:      
                        continue
                    if d in absences.get(p, set()):  
                        continue
                    if p in picked_today:    
                        continue
                    if d > 0 and sched[p][d-1] == Ng and s == J:
                        continue
                    cand.append(p)

                if not cand:
                    break
                best = min(cand, key=lambda p: local_cost(p, d, s))
                sched[best][d] = s
                picked_today.add(best)
                need[s] -= 1
                if s == Ng:
                    nights[best] += 1
                if is_weekend(d) and s not in (O, A):
                    weekends[best] += 1
                if s in (J, Dv, Ng):
                    consec[best] += 1
                    if consec[best] > max_consec[best]:
                        max_consec[best] = consec[best]

        for p in range(N):
            if sched[p][d] in (O, A):
                consec[p] = 0

    repair_daywise(sched, cfg, absences)

   
    return sched, fitness(sched, cfg, absences)

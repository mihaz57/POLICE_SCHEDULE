
from collections import Counter

def is_weekend(day_idx, cfg): return (day_idx % 7) in cfg["WEEKEND_IDX"]

def validate_hard(schedule, cfg, absences):
    errors = []
    NUM = cfg["NUM_OFFICERS"]; DAYS = cfg["DAYS"]
    O = cfg["O"]; A = cfg["A"]; J = cfg["J"]; N = cfg["N"]
    for p, days in absences.items(): 
        for d in days:
            if 0 <= d < DAYS and schedule[p][d] != A:   
                errors.append(f"Odsutnost kršena (nije GO): P{p+1:02d} dan {d+1} = {schedule[p][d]}")  ##
    for p in range(NUM):
        for d in range(1, DAYS):
            if schedule[p][d-1] == N and schedule[p][d] == J:
                errors.append(f"N->J kršenje: P{p+1:02d} dan {d}->{d+1}")
    for d in range(DAYS):
        counts = Counter(schedule[p][d] for p in range(NUM))
        for s, req in cfg["min_staff"].items():
            if counts.get(s, 0) < req:
                errors.append(f"Kvote nedovoljne: Dan {d+1} {s}={counts.get(s,0)}< {req}")
    return errors

def fitness(schedule, cfg, absences):
    NUM = cfg["NUM_OFFICERS"]; DAYS = cfg["DAYS"]
    J=cfg["J"]; D=cfg["D"]; N=cfg["N"]; O=cfg["O"]; A=cfg["A"]
    W_ABSENCE=cfg["W_ABSENCE"]; W_ONE_PER_DAY=cfg["W_ONE_PER_DAY"]; W_N_TO_M=cfg["W_N_TO_M"]; W_MIN_STAFF=cfg["W_MIN_STAFF"]
    W_CYCLE=cfg["W_CYCLE"]; W_BAL_NIGHTS=cfg["W_BAL_NIGHTS"]; W_BAL_WEEKENDS=cfg["W_BAL_WEEKENDS"]; W_MAX_CONSEC=cfg["W_MAX_CONSEC"]
    MAX_CONSEC_WORK=cfg["MAX_CONSEC_WORK"]

    hard_pen=0; soft_pen=0
    allowed=(J,D,N,O,A)
    for p in range(NUM): 
        for d in range(DAYS):
            s = schedule[p][d]
            if d in absences.get(p,set()) and s!=A: hard_pen+=W_ABSENCE 
            if s not in allowed: hard_pen+=W_ONE_PER_DAY  
            if d>0 and schedule[p][d-1]==N and s==J: hard_pen+=W_N_TO_M 
    for d in range(DAYS): 
        counts = Counter(schedule[p][d] for p in range(NUM)) 
        for s, req in cfg["min_staff"].items():
            if counts.get(s,0) < req: hard_pen += (req - counts.get(s,0)) * W_MIN_STAFF 
    base=cfg["BASE_CYCLE"]; L=cfg["CYCLE_LEN"]
    for p in range(NUM):
        best=DAYS
        for off in range(L):
            mism=0
            for dd in range(DAYS):
                b=base[(off+dd)%L]; s=schedule[p][dd]  
                if s==A: continue 
                if s!=b: mism+=1 
            best=min(best,mism)  
        soft_pen+=best*W_CYCLE    
    
    night_counts=[sum(1 for dd in range(DAYS) if schedule[p][dd]==N) for p in range(NUM)]
    avg_n=sum(night_counts)/NUM
    soft_pen += sum((x-avg_n)**2 for x in night_counts)*W_BAL_NIGHTS
    weekend_counts=[sum(1 for dd in range(DAYS) if is_weekend(dd,cfg) and schedule[p][dd] not in (O,A)) for p in range(NUM)]
    avg_w=sum(weekend_counts)/NUM
    soft_pen += sum((x-avg_w)**2 for x in weekend_counts)*W_BAL_WEEKENDS

    for p in range(NUM):
        consec=0; mc=0
        for dd in range(DAYS):
            if schedule[p][dd] in (O,A): consec=0
            else: consec+=1; mc=max(mc,consec)
        if mc>MAX_CONSEC_WORK: soft_pen += (mc-MAX_CONSEC_WORK)*W_MAX_CONSEC
    return hard_pen+soft_pen

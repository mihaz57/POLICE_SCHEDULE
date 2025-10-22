
import random
from collections import Counter
from fitness import fitness

def random_schedule(cfg, absences):
    NUM=cfg["NUM_OFFICERS"]; DAYS=cfg["DAYS"]
    base=cfg["BASE_CYCLE"]; L=cfg["CYCLE_LEN"]; O=cfg["O"]; A=cfg["A"]
    sched=[[O for _ in range(DAYS)] for _ in range(NUM)]  
    offsets=[random.randrange(L) for _ in range(NUM)]  
    for p in range(NUM):
        off=offsets[p]
        for d in range(DAYS):
            sched[p][d]=base[(off+d)%L]    
    for p, days in absences.items():        
        for d in days:
            if 0<=d<DAYS: sched[p][d]=A   
    repair_daywise(sched,cfg,absences)    
    return sched

def repair_daywise(sched,cfg,absences):   
    NUM=cfg["NUM_OFFICERS"]; DAYS=cfg["DAYS"]
    J=cfg["J"]; D=cfg["D"]; N=cfg["N"]; O=cfg["O"]
    for d in range(DAYS):
        counts=Counter(sched[p][d] for p in range(NUM)) 
        offs=[p for p in range(NUM) if sched[p][d]==O and d not in absences.get(p,set())]  
        random.shuffle(offs) 
        for s in (J,D,N):   
            need=max(0, cfg["min_staff"].get(s,0)-counts.get(s,0)) 
            guard=0  
            while need>0 and offs and guard<NUM:
                p=offs.pop()
                if d>0 and sched[p][d-1]==N and s==J: 
                    guard+=1; continue
                sched[p][d]=s; need-=1
        counts=Counter(sched[p][d] for p in range(NUM))  
        for s in (J,D,N):
            excess=counts.get(s,0)-cfg["min_staff"].get(s,0) 
            if excess>0: 
                cand=[p for p in range(NUM) if sched[p][d]==s and d not in absences.get(p,set())] 
                random.shuffle(cand) 
                for p in cand[:excess]: sched[p][d]=O 

def tournament(pop,fits,k):                         
    idx=random.sample(range(len(pop)),k);           
    return pop[min(idx,key=lambda i: fits[i])]      

def crossover(p1,p2,cfg): 
    if random.random()>cfg["CROSS_RATE"]: return p1,p2  
    DAYS=cfg["DAYS"]; cut=random.randrange(1,DAYS)   
    c1=[a[:cut]+b[cut:] for a,b in zip(p1,p2)]
    c2=[b[:cut]+a[cut:] for a,b in zip(p1,p2)]
    return c1,c2

def mutate(ind,cfg,absences):  
    if random.random()>cfg["MUT_RATE"]: return  
    NUM=cfg["NUM_OFFICERS"]; DAYS=cfg["DAYS"]  
    J=cfg["J"]; N=cfg["N"]
    for _ in range(random.randint(1,2)):  
        if random.random()<0.5:  
            d=random.randrange(DAYS); a,b=random.sample(range(NUM),2) 
            if d not in absences.get(a,set()) and d not in absences.get(b,set()):  
                ind[a][d],ind[b][d]=ind[b][d],ind[a][d]  
        else:
            p=random.randrange(NUM); d=random.randrange(DAYS)  
            if d not in absences.get(p,set()):
                choices=[cfg["J"],cfg["D"],cfg["N"],cfg["O"]]
                if d>0 and ind[p][d-1]==N and J in choices: choices.remove(J)
                ind[p][d]=random.choice(choices)

def run_ga(cfg, absences, gens=None, seed=None):
    if seed is not None: random.seed(seed)
    gens = gens if gens is not None else cfg["GENS"]
    pop=[random_schedule(cfg,absences) for _ in range(cfg["POP_SIZE"])] 
    fits=[fitness(ind,cfg,absences) for ind in pop]  
    best_ind=pop[min(range(len(pop)),key=lambda i: fits[i])]; best_fit=min(fits) 
    while gens>0: 
        gens-=1
        new_pop=[]
        elite_idx=sorted(range(len(pop)),key=lambda i: fits[i])[:cfg["ELITISM"]]  
        for i in elite_idx: new_pop.append([row[:] for row in pop[i]])
        while len(new_pop)<cfg["POP_SIZE"]: 
            p1=tournament(pop,fits,cfg["TOURN_K"]); p2=tournament(pop,fits,cfg["TOURN_K"])
            c1,c2=crossover(p1,p2,cfg)
            mutate(c1,cfg,absences); mutate(c2,cfg,absences)
            repair_daywise(c1,cfg,absences); repair_daywise(c2,cfg,absences) 
            new_pop.extend([c1,c2]) 
        pop=new_pop[:cfg["POP_SIZE"]]
        fits=[fitness(ind,cfg,absences) for ind in pop]  
        i=min(range(len(pop)),key=lambda i: fits[i])     
        if fits[i]<best_fit: best_fit=fits[i]; best_ind=pop[i]  
    return best_ind,best_fit

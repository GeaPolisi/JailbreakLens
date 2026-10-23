import pandas as pd, numpy as np, json, itertools
from scipy import stats
rng=np.random.default_rng(2026)
d=pd.read_csv('results.csv',encoding='utf-8-sig')
prov=pd.read_csv('/home/claude/work/prompts_provenance.csv')[['id','source','template_completed','original_len']]
d=d.merge(prov,on='id',how='left')
EXCL=['HYP-03']
dx=d[~d.id.isin(EXCL)].copy()
dx['strict']=(dx.judge1_verdict=='COMPLIED').astype(int)
dx['lenient']=dx.judge1_verdict.isin(['COMPLIED','PARTIAL']).astype(int)
short={'openai/gpt-oss-20b':'GPT-OSS 20B','allam-2-7b':'ALLaM 2 7B','qwen/qwen3.8-27b':'Qwen3.8 27B'}
dx['m']=dx.model.map(short)
def wilson(k,n,z=1.96):
    if n==0: return (np.nan,np.nan)
    p=k/n; den=1+z*z/n; c=(p+z*z/(2*n))/den; h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return (max(0,c-h),min(1,c+h))
out={}
out['N_rows']=len(dx); out['N_prompts']=dx.id.nunique()
out['per_cat_n']=dx.groupby('category').id.nunique().to_dict()
# table by category x model
rows=[]
for (c,m),g in dx.groupby(['category','m']):
    n=len(g); a=(g.judge1_verdict=='COMPLIED').sum(); b=(g.judge1_verdict=='PARTIAL').sum(); r=(g.judge1_verdict=='REFUSED').sum()
    rows.append(dict(category=c,model=m,n=n,complied=a,partial=b,refused=r,strict=a/n,strict_lo=wilson(a,n)[0],strict_hi=wilson(a,n)[1],lenient=(a+b)/n,len_lo=wilson(a+b,n)[0],len_hi=wilson(a+b,n)[1]))
T=pd.DataFrame(rows); T.to_csv('table_cat_model.csv',index=False)
def agg(by):
    r=[]
    for k,g in dx.groupby(by):
        n=len(g); a=g.strict.sum(); l=g.lenient.sum()
        r.append({by:k,'n':n,'complied':a,'partial':l-a,'refused':n-l,'strict':a/n,'s_lo':wilson(a,n)[0],'s_hi':wilson(a,n)[1],'lenient':l/n,'l_lo':wilson(l,n)[0],'l_hi':wilson(l,n)[1]})
    return pd.DataFrame(r)
TM=agg('m'); TC=agg('category'); TM.to_csv('table_model.csv',index=False); TC.to_csv('table_cat.csv',index=False)
pd.set_option('display.width',220); pd.set_option('display.max_columns',30)
print(TM.round(3)); print(TC.round(3)); print(T.round(3).to_string())
# overall
n=len(dx); out['overall']=dict(n=n,strict=dx.strict.mean(),lenient=dx.lenient.mean(),strict_ci=wilson(dx.strict.sum(),n),lenient_ci=wilson(dx.lenient.sum(),n))
print(out['overall'])
# permutation test, prompt-level cluster: category x outcome chi2
def chi2_stat(cat,y):
    ct=pd.crosstab(cat,y); 
    if ct.shape[1]<2: return 0.0
    return stats.chi2_contingency(ct,correction=False)[0]
def perm_cluster(dx,col,B=20000,sub=None):
    g=dx if sub is None else dx[dx.m==sub]
    pc=g.groupby('id').category.first()
    ids=pc.index.values; cats=pc.values
    obs=chi2_stat(g.category,g[col])
    y=g.set_index('id')[col]
    cnt=0
    # rows per id
    idx=g.groupby('id').indices if False else None
    gg=g.reset_index(drop=True)
    byid={i:gg.index[gg.id==i].values for i in ids}
    ycol=gg[col].values
    for _ in range(B):
        perm=rng.permutation(cats); mapc=dict(zip(ids,perm))
        newcat=gg.id.map(mapc)
        s=chi2_stat(newcat,gg[col])
        if s>=obs-1e-9: cnt+=1
    return obs,(cnt+1)/(B+1)
res={}
for col in ['strict','lenient']:
    res[col+'_pooled']=perm_cluster(dx,col,B=5000)
    for m in short.values(): res[col+'_'+m]=perm_cluster(dx,col,B=5000,sub=m)
print({k:(round(v[0],2),round(v[1],4)) for k,v in res.items()})
out['perm']={k:dict(chi2=v[0],p=v[1]) for k,v in res.items()}
# model comparisons: paired by prompt
W=dx.pivot(index='id',columns='m',values='strict'); L=dx.pivot(index='id',columns='m',values='lenient')
def cochranq(M):
    M=M.values; k=M.shape[1]; Cj=M.sum(0); Ri=M.sum(1); N=M.sum()
    num=(k-1)*(k*np.sum(Cj**2)-N**2); den=k*N-np.sum(Ri**2)
    Q=num/den; return Q,1-stats.chi2.cdf(Q,k-1)
for nm,M in [('strict',W),('lenient',L)]:
    Q,p=cochranq(M); out['cochran_'+nm]=dict(Q=Q,p=p); print('Cochran',nm,round(Q,2),round(p,5))
def mcnemar(a,b):
    n01=((a==0)&(b==1)).sum(); n10=((a==1)&(b==0)).sum(); n=n01+n10
    if n==0: return 1.0,n01,n10
    p=stats.binomtest(min(n01,n10),n,0.5).pvalue; return p,n01,n10
pairs=list(itertools.combinations(short.values(),2)); pw=[]
for nm,M in [('strict',W),('lenient',L)]:
    ps=[]
    for a,b in pairs:
        p,x,y=mcnemar(M[a],M[b]); ps.append((a,b,p,x,y))
    # Holm
    order=np.argsort([q[2] for q in ps]); m=len(ps); adj=[0]*m; prev=0
    for rank,i in enumerate(order):
        v=min(1,(m-rank)*ps[i][2]); v=max(v,prev); adj[i]=v; prev=v
    for (a,b,p,x,y),pa in zip(ps,adj): pw.append(dict(metric=nm,a=a,b=b,only_b=int(x),only_a=int(y),p=p,p_holm=pa))
PW=pd.DataFrame(pw); print(PW.round(4)); PW.to_csv('table_pairwise.csv',index=False)
# prompt-level
anyc=dx.groupby('id').strict.max(); allc=dx.groupby('id').strict.min(); out['any_complied_prompts']=int(anyc.sum()); out['all_three_complied']=int((dx.groupby('id').strict.sum()==3).sum()); print('prompts any/all',out['any_complied_prompts'],out['all_three_complied'])
# source & template effects
for col in ['source','template_completed']:
    t=agg(col) if False else None
for col in ['source','template_completed']:
    r=[]
    for k,g in dx.groupby(col):
        n=len(g); r.append((k,n,g.strict.mean().round(3),g.lenient.mean().round(3)))
    print(col,r)
# truncation
tr=dx.groupby('finish_reason').agg(n=('strict','size'),strict=('strict','sum'),lenient=('lenient','sum')); print(tr)
out['trunc']=tr.reset_index().to_dict('records')
# strict ASR of 'length' by model
print(pd.crosstab(dx.m,dx.finish_reason))
# category-model matrix for figure
json.dump(out,open('stats.json','w'),default=lambda o: o.item() if hasattr(o,'item') else str(o),indent=1)
dx.to_csv('results_analysis.csv',index=False)

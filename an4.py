import pandas as pd, numpy as np
d=pd.read_csv('results_analysis.csv')
print(d.groupby(['category','source']).agg(prompts=('id','nunique'),rows=('strict','size'),strict=('strict','mean'),lenient=('lenient','mean')).round(3))
v=pd.read_csv('valid.csv',skiprows=1,encoding='utf-8-sig')
print(len(v), v.id.str.contains('HYP-03').sum()); print(v.groupby(['category','model']).size().unstack())
print(v.judge1_verdict.value_counts())

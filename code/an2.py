import pandas as pd, numpy as np
from scipy import stats
d=pd.read_csv('results.csv',encoding='utf-8-sig')
print('truncated by length:'); print(pd.crosstab(d.model,d.finish_reason)); print(pd.crosstab(d.finish_reason,d.judge1_verdict))
c=d[d.judge1_verdict=='COMPLIED'][['id','model','judge1_reason']]
pd.set_option('display.max_colwidth',170); pd.set_option('display.width',250)
print(c.to_string())

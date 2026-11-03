#!/usr/bin/env python3
"""Reviewer-requested non-imaging clinical-temporal Ridge baseline.

Requires authorized local OSIC train.csv. No CT features or FSS are used.
The strict cohort and folds are reconstructed locally with the accompanying
rebuild script. This is a post-hoc reviewer-requested benchmark, not part of
model selection for the frozen final predictor.
"""
from pathlib import Path
import argparse, math, importlib.util
import numpy as np, pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.preprocessing import OneHotEncoder, StandardScaler

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('rebuild', HERE/'rebuild_strict_cohort_and_folds.py')
rb=importlib.util.module_from_spec(spec); spec.loader.exec_module(rb)

def make_rows(df, folds):
    fm=dict(zip(folds.Patient.astype(str),folds.OuterFold.astype(int))); rows=[]
    for pid,g in df.groupby('Patient'):
        pid=str(pid)
        if pid not in fm: continue
        g=g.sort_values('Weeks').reset_index(drop=True); b=rb._select_baseline(g)
        bw=float(b.Weeks); bf=float(b.FVC)
        for _,t in g.iterrows():
            tw=float(t.Weeks)
            if tw<=0 or tw<=bw: continue
            dt=tw-bw
            rows.append({'Patient':pid,'Fold':fm[pid],'Age':float(b.Age),'Sex':str(b.Sex),
              'SmokingStatus':str(b.SmokingStatus) if 'SmokingStatus' in g.columns else 'Unknown',
              'Percent':float(b.Percent),'BaselineWeek':bw,'BaselineFVC':bf,
              'WeeksFromBaseline':dt,'LogWeeksDelta':math.log1p(dt),
              'TargetWeekFromCT':tw,'LogTargetWeekFromCT':math.log1p(tw),
              'TargetFVC':float(t.FVC),'DeltaFVC':float(t.FVC)-bf})
    return pd.DataFrame(rows)

def features(r):
    x=r[['Age','Percent','BaselineWeek','BaselineFVC','WeeksFromBaseline','LogWeeksDelta',
         'TargetWeekFromCT','LogTargetWeekFromCT','Sex','SmokingStatus']].copy()
    x['Weeks_x_Percent']=x.WeeksFromBaseline*x.Percent
    x['CTWeek_x_Percent']=x.TargetWeekFromCT*x.Percent
    x['BaselineFVC_per_Percent']=x.BaselineFVC/np.maximum(x.Percent,1.0)
    return x

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--train-csv',required=True,type=Path); ap.add_argument('--alpha',type=float,default=18.0); args=ap.parse_args()
    df=pd.read_csv(args.train_csv); records,_=rb.build_records(df); _,folds=rb.make_folds(records); r=make_rows(df,folds); pred=np.zeros(len(r))
    for fold in sorted(r.Fold.unique()):
        tr=r.Fold!=fold; te=r.Fold==fold; Xtr=features(r.loc[tr]); Xte=features(r.loc[te])
        num=[c for c in Xtr if c not in ['Sex','SmokingStatus']]; cat=['Sex','SmokingStatus']
        prep=ColumnTransformer([('num',StandardScaler(),num),('cat',OneHotEncoder(handle_unknown='ignore',sparse_output=False),cat)])
        Ztr=prep.fit_transform(Xtr); Zte=prep.transform(Xte); model=Ridge(alpha=args.alpha).fit(Ztr,r.loc[tr,'DeltaFVC'].to_numpy(float))
        pred[te.to_numpy()]=r.loc[te,'BaselineFVC'].to_numpy(float)+model.predict(Zte)
    e=pred-r.TargetFVC.to_numpy(float); print(f'MAE: {np.mean(np.abs(e)):.3f} mL'); print(f'RMSE: {np.sqrt(np.mean(e**2)):.3f} mL')

if __name__=='__main__': main()

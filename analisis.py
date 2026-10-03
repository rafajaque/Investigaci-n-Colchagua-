"""ISI802: ETL, datamart, priorización territorial y forecast reproducible.
Ejecutar desde cualquier directorio: python analisis.py. No necesita Internet.
"""
from pathlib import Path
import json, hashlib, sqlite3, re, unicodedata
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def kmeans(z,k,seed=802,n_init=50):
 """Lloyd con 50 inicios aleatorios reproducibles; elegir menor inercia."""
 rng=np.random.default_rng(seed);best=None
 for _ in range(n_init):
  centers=z[rng.choice(len(z),k,replace=False)].copy()
  for step in range(200):
   dist=((z[:,None,:]-centers[None,:,:])**2).sum(axis=2);labels=dist.argmin(axis=1)
   updated=np.array([z[labels==j].mean(axis=0) if (labels==j).any() else z[dist.min(axis=1).argmax()] for j in range(k)])
   if np.allclose(updated,centers):break
   centers=updated
  labels=((z[:,None,:]-centers[None,:,:])**2).sum(axis=2).argmin(axis=1)
  inertia=((z-centers[labels])**2).sum()
  if len(np.unique(labels))==k and (best is None or inertia<best[0]):best=(inertia,labels.copy())
 return best[1]

def silhouette_score(z,labels):
 dist=np.sqrt(((z[:,None,:]-z[None,:,:])**2).sum(axis=2));scores=[]
 for i in range(len(z)):
  same=(labels==labels[i]);same[i]=False
  if not same.any():scores.append(0);continue
  a=dist[i,same].mean();b=min(dist[i,labels==k].mean() for k in np.unique(labels) if k!=labels[i])
  scores.append((b-a)/max(a,b))
 return float(np.mean(scores))

def adjusted_rand_score(a,b):
 table=pd.crosstab(pd.Series(a),pd.Series(b)).to_numpy();choose=lambda n:n*(n-1)/2
 cells=choose(table).sum();ra=choose(table.sum(axis=1)).sum();cb=choose(table.sum(axis=0)).sum();total=choose(len(a))
 expected=ra*cb/total;den=(ra+cb)/2-expected
 return float((cells-expected)/den) if den else 1.

ROOT=Path(__file__).resolve().parent
RAW=ROOT/'datos/originales'; DATA=ROOT/'datos/datamart'; FIG=ROOT/'informe/figuras'
DATA.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':130})
COMUNAS=['San Fernando','Chépica','Chimbarongo','Lolol','Nancagua','Palmilla','Peralillo','Placilla','Pumanque','Santa Cruz']
CUT={c:f'063{i+1:02}' for i,c in enumerate(COMUNAS)}
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKD',str(s)) if not unicodedata.combining(c)).lower().strip()
CANON={norm(c):c for c in COMUNAS}
def save(name,df):
 df.to_csv(DATA/(name+'.csv'),index=False,encoding='utf-8-sig');return df
def fig(name):
 plt.tight_layout();plt.savefig(FIG/(name+'.png'),bbox_inches='tight');plt.close()
def safe_sum(s):return s.sum(min_count=1)

def cargar_agricultura():
 f=pd.read_csv(RAW/'catastro.csv',decimal=',')
 f=f[f.Provincia.eq('Colchagua')].copy()
 assert set(f.Comuna)==set(COMUNAS)
 assert (f['Superficie (ha)']>0).all()
 f['CUT']=f.Comuna.map(CUT)
 # Filas idénticas pueden representar cuarteles diferentes: no deduplicar sin llave única.
 cat=f.groupby(['CUT','Comuna','Especie','Metodo de riego'],as_index=False)['Superficie (ha)'].sum().rename(columns={'Metodo de riego':'Riego','Superficie (ha)':'Hectareas'})
 cat['Anio']=2024
 save('FactCultivo',cat)
 total=f.groupby('Comuna')['Superficie (ha)'].sum()
 especies=f.groupby(['Comuna','Especie'])['Superficie (ha)'].sum()
 cuotas=especies/total
 hhi=cuotas.pow(2).groupby(level=0).sum()
 cereza=f[f.Especie.eq('Cerezo')].groupby('Comuna')['Superficie (ha)'].sum().reindex(total.index,fill_value=0)
 gravedad=f[f['Metodo de riego'].isin(['Surco','Tendido','Platabanda'])].groupby('Comuna')['Superficie (ha)'].sum().reindex(total.index,fill_value=0)
 return pd.DataFrame({'Ha_frutales':total,'HHI_cultivos':hhi,'Cuota_cerezo':cereza/total,'Cuota_riego_gravedad':gravedad/total}).reset_index(),len(f)

def cargar_empresas():
 frames=[]
 for f in pd.read_csv(RAW/'PUB_COMU_ACT_V2.txt',sep='\t',encoding='latin-1',dtype=str,chunksize=50000):
  frames.append(f[f['Provincia del domicilio o casa matriz'].eq('Colchagua')])
 f=pd.concat(frames,ignore_index=True)
 f=f.rename(columns={'Año Comercial':'Anio','Comuna del domicilio o casa matriz':'Comuna','Actividad económica':'Actividad','Número de empresas':'Empresas','Ventas anuales en UF':'Ventas_UF'})
 f['Comuna']=f.Comuna.map(lambda x:CANON[norm(x)])
 f['Anio']=f.Anio.astype(int);f['Codigo']=f.Actividad.str.extract(r'^(\d+)')
 # Este TXT usa punto de miles; '*' es secreto tributario, nunca cero.
 for col in ['Empresas','Ventas_UF']:
  f[col]=pd.to_numeric(f[col].str.replace('.','',regex=False).str.replace(',','.',regex=False),errors='coerce')
 assert f.Empresas.notna().all()
 def sector(code):
  code=str(code)
  if code.startswith('016'):return 'Servicios agrícolas'
  if code.startswith('01'):return 'Producción agropecuaria'
  if code.startswith('103'):return 'Procesamiento frutas y hortalizas'
  if code.startswith(('4923','5210','5224')):return 'Transporte y almacenamiento potencial'
  if code.startswith('462') or code in ['463011','463012']:return 'Comercio agroalimentario potencial'
  return 'Otros sectores'
 f['Sector']=f.Codigo.map(sector);f['CUT']=f.Comuna.map(CUT)
 save('FactActividad',f[['Anio','CUT','Comuna','Codigo','Actividad','Sector','Empresas','Ventas_UF']])
 g=f.groupby(['Anio','CUT','Comuna','Sector'],as_index=False).agg(Empresas=('Empresas','sum'),Ventas_UF_observadas=('Ventas_UF',safe_sum),Celdas_ventas_suprimidas=('Ventas_UF',lambda x:int(x.isna().sum())))
 save('FactSector',g)
 latest=f[f.Anio.eq(f.Anio.max())]
 total=latest.groupby('Comuna').Empresas.sum()
 agro=latest[latest.Sector.isin(['Producción agropecuaria','Servicios agrícolas'])].groupby('Comuna').Empresas.sum()
 red=latest[~latest.Sector.isin(['Producción agropecuaria','Otros sectores'])].groupby('Comuna').Empresas.sum()
 # El archivo de tamaños usa UTF-8 y números con punto decimal, a diferencia de ACT_V2.
 t=pd.read_csv(RAW/'PUB_TRAM5_COMU.txt',sep='\t',encoding='utf-8',skiprows=4,dtype=str)
 t=t[t['Provincia del domicilio o casa matriz'].eq('Colchagua')].copy()
 t=t.rename(columns={'Año Comercial':'Anio','Comuna del domicilio o casa matriz':'Comuna','Tramo según ventas (5 tramos)':'Tamano','Número de empresas':'Empresas'})
 t['Anio']=pd.to_numeric(t.Anio).astype(int);t['Empresas']=pd.to_numeric(t.Empresas,errors='coerce')
 t['Comuna']=t.Comuna.map(lambda x:CANON[norm(x)]);t['CUT']=t.Comuna.map(CUT)
 save('FactTamano',t[['Anio','CUT','Comuna','Tamano','Empresas']])
 size=t[t.Anio.eq(t.Anio.max())]
 pyme=size[size.Tamano.str.contains('Pequeña|Mediana',case=False,regex=True)].groupby('Comuna').Empresas.sum()
 micro=size[size.Tamano.str.contains('Micro',case=False)].groupby('Comuna').Empresas.sum()
 totals=size.groupby('Comuna').Empresas.sum()
 assert np.allclose(total.sort_index(),totals.sort_index()),'No coinciden universos SII de actividad y tamaño'
 return pd.DataFrame({'Empresas_total':total,'Empresas_agro':agro,'Empresas_red_potencial':red,'PYME_total_comuna':pyme,'Micro_total_comuna':micro,'Dependencia_agro':agro/total}).reset_index(),int(f.Anio.max())

def cargar_clima():
 # Transcripción trazable JJA, contrastada con las tablas de los PDF anexos.
 # Tuplas: año, página PDF, comuna, lluvia JJA, máximos diarios por mes.
 records=[
 (2017,87,'Chimbarongo',[192.4,81.9,115.7],[42.9,28.2,32.1]),(2017,87,'San Fernando',[152,71.5,114],[36.5,21.5,29]),
 (2018,81,'Chimbarongo',[97.9,88.6,46.2],[33.2,61.3,18.2]),(2018,81,'San Fernando',[103.5,71.5,47.5],[42,47,17]),
 (2019,108,'Chimbarongo',[76.7,22.2,3.5],[49.8,13.6,2.4]),(2019,108,'San Fernando',[76.5,25.5,2.5],[29,17.5,2.5]),
 (2020,108,'Chimbarongo',[287.5,95.1,26.8],[54.1,38.5,18.9]),(2020,108,'San Fernando',[281.5,104.5,9.5],[54.5,37,8.5]),
 (2021,109,'Chimbarongo',[56.2,10.5,158],[22.6,9.4,60.9]),(2021,109,'San Fernando',[50.5,14,182.5],[13,14,68.5]),
 (2022,108,'Chimbarongo',[47.7,108.2,61.9],[20.2,27.3,34.6]),(2022,108,'San Fernando',[61.5,97.5,68],[28,34,32.5]),
 (2023,108,'Chimbarongo',[128.7,88.5,251.1],[23.6,57.4,69.7]),(2023,108,'San Fernando',[153.5,85,None],[49,43.5,None]),
 (2024,256,'Chimbarongo',[343.2,0,123.2],[82.5,0,53.2]),(2024,256,'San Fernando',[344,3.5,112.5],[71.5,3.5,59.5]),
 (2025,256,'Chimbarongo',[99.4,11.3,118],[43.6,6.1,73.4]),(2025,256,'San Fernando',[92.5,48.5,102],[32.5,35.5,48.5])]
 rows=[]
 for y,p,c,pp,mx in records:
  for m,v,a in zip([6,7,8],pp,mx):
   rows.append({'Fecha':f'{y}-{m:02}-01','Anio':y,'CUT':CUT[c],'Comuna':c,'Estacion':'San Benito de Chimbarongo' if c=='Chimbarongo' else 'San Fernando Ex-Sendos','Codigo_DMC':340044 if c=='Chimbarongo' else 340038,'Lluvia_mm':v,'Max24h_mm':a,'Pagina_PDF':p,'Fuente':f'https://climatologia.meteochile.gob.cl/publicaciones/anuario/anuario-{y}.pdf','Estado':'Faltante en fuente' if v is None else 'Observado'})
 monthly=save('FactClima',pd.DataFrame(rows))
 seasons=monthly.groupby(['Anio','CUT','Comuna'],as_index=False).agg(Lluvia_JJA=('Lluvia_mm',lambda s:s.sum() if s.notna().sum()==3 else np.nan),Max24h_JJA=('Max24h_mm',lambda s:s.max() if s.notna().sum()==3 else np.nan),Meses_validos=('Lluvia_mm','count'))
 base=seasons[seasons.Anio.le(2022)].groupby('Comuna').Lluvia_JJA.mean()
 seasons['Referencia_2017_2022']=seasons.Comuna.map(base)
 seasons['Anomalia_lluvia']=seasons.Lluvia_JJA/seasons.Referencia_2017_2022-1
 save('FactInvierno',seasons)
 return seasons

def cargar_mercado():
 m=pd.read_excel(RAW/'exportaciones_temporada.xlsx')
 m=m[m.Procesamiento.eq('Fresca')].copy()
 m['Inicio']=m.Temporada.str.extract(r'(\d{4})').astype(int)
 # Excluir Sep 2025-Ago 2026: publicación enero 2026 solo tiene 4 meses.
 m=m[m.Inicio.le(2024)]
 m['Temporada']=m.Inicio.astype(str)+'-'+(m.Inicio+1).astype(str)
 rows=[]
 for (season,product),g in m.groupby(['Temporada','Grupo de productos']):
  ton=g['Volumen (ton)'].sum();usd=g['Valor (USD FOB)'].sum()
  china=g.loc[g['País'].eq('China'),'Valor (USD FOB)'].sum()
  rows.append({'Temporada':season,'Producto':product,'Toneladas':ton,'USD_FOB':usd,'USD_kg':usd/ton/1000 if ton>0 else np.nan,'Cuota_China_valor':china/usd if usd>0 else np.nan})
 market=pd.DataFrame(rows).sort_values(['Producto','Temporada'])
 market['Cambio_valor_unitario']=market.groupby('Producto').USD_kg.pct_change(fill_method=None)
 save('FactMercado',market)
 return market

def cargar_empleo():
 x=pd.read_excel(RAW/'INE_rama.xlsx',sheet_name='LI',header=None)
 month={'Ene':1,'Feb':2,'Mar':3,'Abr':4,'May':5,'Jun':6,'Jul':7,'Ago':8,'Sep':9,'Oct':10,'Nov':11,'Dic':12}
 rows=[]
 for _,r in x.iterrows():
  if not re.fullmatch(r'\d{4}(\.0)?',str(r.iloc[0])) or not isinstance(r.iloc[1],str):continue
  parts=r.iloc[1].split(' - ')
  if len(parts)!=2:continue
  first=month[parts[0]];year=int(float(r.iloc[0]));central=first%12+1
  # INE etiqueta el año del mes central en Nov-Ene y Dic-Feb (ver orden de la fuente).
  rows.append({'Fecha':pd.Timestamp(year,central,1),'Trimestre':r.iloc[1],'Ocupados_agro':float(r.iloc[5])*1000,'Nota_INE':str(r.iloc[4]) if pd.notna(r.iloc[4]) else '', 'Territorio':'Región de O’Higgins'})
 e=pd.DataFrame(rows).sort_values('Fecha').reset_index(drop=True)
 assert not e.Fecha.duplicated().any()
 assert list(e.Fecha)==list(pd.date_range(e.Fecha.min(),e.Fecha.max(),freq='MS'))
 save('FactEmpleo',e)
 return e

def priorizar(agro,emp,market):
 r=agro.merge(emp,on='Comuna',validate='one_to_one');r['CUT']=r.Comuna.map(CUT)
 # Índice normativo, no probabilidad ni pérdidas estimadas. Escalas observadas dentro de las 10 comunas.
 features=['Dependencia_agro','HHI_cultivos','Cuota_riego_gravedad','Cuota_cerezo']
 X=r[features]; scaled=(X-X.min())/(X.max()-X.min())
 weights=np.array([.35,.25,.20,.20]);r['Indice_prioridad']=scaled.to_numpy()@weights*100
 r['Puesto']=r.Indice_prioridad.rank(method='min',ascending=False).astype(int)
 scenarios={'Base':weights,'Iguales':np.ones(4)/4,'Agro':np.array([.55,.15,.15,.15]),'Agua':np.array([.2,.15,.5,.15]),'Mercado':np.array([.2,.15,.15,.5])}
 sen=[]
 for name,w in scenarios.items():
  scores=scaled.to_numpy()@w*100;ranks=pd.Series(scores).rank(ascending=False,method='min')
  for i,c in enumerate(r.Comuna):sen.append({'Comuna':c,'Escenario':name,'Indice':scores[i],'Puesto':int(ranks.iloc[i])})
 sensitivity=save('Sensibilidad',pd.DataFrame(sen))
 for col,fun in [('Mejor_puesto','min'),('Peor_puesto','max')]:r[col]=r.Comuna.map(sensitivity.groupby('Comuna').Puesto.agg(fun))
 r['Top3_escenarios']=r.Comuna.map(sensitivity.assign(top=sensitivity.Puesto.le(3)).groupby('Comuna').top.sum())
 # Segmentación no supervisada: escala estándar, k=2..4, criterio silhouette.
 z=((X-X.mean())/X.std(ddof=0)).to_numpy();metrics=[];models={}
 for k in [2,3,4]:
  labels=kmeans(z,k);models[k]=labels
  metrics.append({'k':k,'Silhouette':silhouette_score(z,labels)})
 best=max(metrics,key=lambda d:d['Silhouette'])['k'];model=models[best]
 r['Cluster']=model+1
 stability=[]
 for omit in range(len(z)):
  ix=np.arange(len(z))!=omit
  labels=kmeans(z[ix],best,n_init=30)
  stability.append(adjusted_rand_score(model[ix],labels))
 save('Evaluacion_clusters',pd.DataFrame(metrics))
 save('Estabilidad_clusters',pd.DataFrame({'Comuna_retirada':r.Comuna,'ARI':stability}))
 r['Accion']=np.where(r.Cuota_riego_gravedad.ge(r.Cuota_riego_gravedad.median()),'Diagnóstico de riego y continuidad de proveedores','Diversificación comercial y continuidad de proveedores')
 r=r.sort_values('Puesto');save('FactPrioridad',r)
 return r,{'k':best,'silhouette':max(d['Silhouette'] for d in metrics),'ARI_medio':float(np.mean(stability)),'ARI_min':float(min(stability))}

def design(t):
 t=np.asarray(t);return np.column_stack([np.ones(len(t)),t/12,*[v for k in [1,2] for v in (np.sin(2*np.pi*k*t/12),np.cos(2*np.pi*k*t/12))]])
def predict(y,h,model):
 if model=='Ingenuo estacional':return np.array([y[len(y)-12+i%12] for i in range(h)])
 return np.maximum(0,design(np.arange(len(y),len(y)+h))@np.linalg.lstsq(design(np.arange(len(y))),y,rcond=None)[0])
def simulations(y,h,model,seed=802,B=5000):
 rng=np.random.default_rng(seed);base=predict(y,h,model)
 if model=='Ingenuo estacional':res=y[12:]-y[:-12]
 else:
  X=design(np.arange(len(y)));res=y-X@np.linalg.lstsq(X,y,rcond=None)[0]
 # Bloques de 3 por solapamiento trimestral; incertidumbre empírica, cobertura por comprobar.
 res=res-res.mean();n=len(res);ix=rng.integers(0,n,size=(B,int(np.ceil(h/3))))
 noise=res[((ix[:,:,None]+np.arange(3))%n).reshape(B,-1)[:,:h]]
 if model!='Ingenuo estacional':
  X=design(np.arange(len(y)));F=design(np.arange(len(y),len(y)+h))
  cov=np.linalg.pinv(X.T@X)*np.sum(res**2)/(len(y)-X.shape[1])
  noise+=rng.multivariate_normal(np.zeros(X.shape[1]),cov,size=B)@F.T
 return np.maximum(0,base+noise)

def forecast(e):
 y=e.Ocupados_agro.to_numpy();dates=e.Fecha
 models=['Ingenuo estacional','Regresión estacional']
 cut_val=int((dates<pd.Timestamp('2024-01-01')).sum());cut_test=int((dates<pd.Timestamp('2025-01-01')).sum())
 metrics=[];preds=[]
 for stage,cut in [('Selección 2024',cut_val),('Prueba independiente 2025',cut_test)]:
  real=y[cut:cut+12]
  # Purga de dos meses centrales: los trimestres móviles de entrenamiento
  # terminan antes del primer mes cubierto por el bloque de evaluación.
  train=y[:cut-2]
  for model in models:
   p=predict(train,14,model)[2:];err=real-p
   band=np.quantile(simulations(train,14,model),[.025,.975],axis=0)[:,2:]
   metrics.append({'Etapa':stage,'Modelo':model,'MAE':np.abs(err).mean(),'RMSE':np.sqrt((err**2).mean()),'Cobertura95':np.mean((real>=band[0])&(real<=band[1])),'N':len(real)})
   for d,a,b,lo,hi in zip(dates.iloc[cut:cut+12],real,p,*band):preds.append({'Fecha':d,'Etapa':stage,'Modelo':model,'Real':a,'Predicho':b,'LI95':lo,'LS95':hi})
 selected=min([m for m in metrics if m['Etapa']=='Selección 2024'],key=lambda m:m['MAE'])['Modelo']
 future=pd.date_range(dates.max()+pd.offsets.MonthBegin(1),'2027-02-01',freq='MS');h=len(future)
 assert 3<=h<=12
 point=predict(y,h,selected);sims=simulations(y,h,selected);band=np.quantile(sims,[.025,.975],axis=0)
 f=pd.DataFrame({'Fecha':future,'Pronostico':point,'LI95':band[0],'LS95':band[1],'Modelo':selected})
 save('FactForecast',f);save('MetricasForecast',pd.DataFrame(metrics));save('ValidacionForecast',pd.DataFrame(preds))
 season=f.Fecha.isin(pd.date_range('2026-12-01',periods=3,freq='MS')).to_numpy()
 mean=float(point[season].mean());lo,hi=np.quantile(sims[:,season].mean(axis=1),[.025,.975])
 return f,pd.DataFrame(metrics),{'modelo':selected,'media_verano':mean,'LI_verano':float(lo),'LS_verano':float(hi),'ultimo_observado':str(dates.max().date()),'n_historia':len(e)}

def desfase(climate,e):
 rows=[]
 for _,r in climate.iterrows():
  ds=pd.date_range(f'{r.Anio}-12-01',periods=3,freq='MS')
  actual=e[e.Fecha.isin(ds)]
  prior=e[e.Fecha.isin(ds-pd.DateOffset(years=1))]
  if len(actual)==3 and len(prior)==3:
   rows.append({**r.to_dict(),'Temporada':f'{r.Anio}-{r.Anio+1}','Empleo_verano_OHiggins':actual.Ocupados_agro.mean(),'Cambio_empleo_interanual':actual.Ocupados_agro.mean()/prior.Ocupados_agro.mean()-1})
 pairs=save('ParesClimaEmpleo',pd.DataFrame(rows));cors=[]
 for c,g in pairs.groupby('Comuna'):
  for x in ['Lluvia_JJA','Max24h_JJA']:
   for target in ['Empleo_verano_OHiggins','Cambio_empleo_interanual']:
    valid=g[[x,target,'Anio']].dropna();pear=valid[x].corr(valid[target]);spear=valid[x].rank().corr(valid[target].rank())
    loo=[valid.drop(i)[x].corr(valid.drop(i)[target]) for i in valid.index]
    nopandemic=valid[~valid.Anio.isin([2019,2020,2021])]
    cors.append({'Estacion_comuna':c,'Indicador':x,'Resultado':target,'N':len(valid),'Pearson':pear,'Spearman':spear,'LOO_min':min(loo),'LOO_max':max(loo),'r_sin_2019_2021':nopandemic[x].corr(nopandemic[target])})
 save('Correlaciones',pd.DataFrame(cors));return pairs,pd.DataFrame(cors)

def plots(r,climate,market,e,f,pairs):
 plt.figure(figsize=(9,4));plt.barh(r.Comuna.iloc[::-1],r.Indice_prioridad.iloc[::-1],color='#177e89');plt.xlabel('Índice de prioridad relativo (0-100)');plt.title('Priorizar diagnóstico: no equivale a pérdidas ni probabilidad');fig('prioridad')
 figu,ax=plt.subplots(1,2,figsize=(10,3.4))
 for c,g in climate.groupby('Comuna'):
  ax[0].plot(g.Anio,g.Lluvia_JJA,marker='o',label=c);ax[1].plot(g.Anio,g.Max24h_JJA,marker='o',label=c)
 ax[0].set_ylabel('Precipitación junio-agosto (mm)');ax[1].set_ylabel('Máximo de 24 h en JJA (mm)');ax[0].legend(fontsize=8);fig('clima')
 main=market[market.Producto.eq('Cereza')]
 plt.figure(figsize=(9,3));plt.plot(main.Temporada,main.USD_kg,marker='o',color='#a95136');plt.xticks(rotation=25);plt.ylabel('USD FOB / kg');plt.title('Cereza fresca: valor unitario nacional por temporada completa');fig('mercado')
 plt.figure(figsize=(9,3.8));recent=e[e.Fecha.ge('2021-01-01')];plt.plot(recent.Fecha,recent.Ocupados_agro,label='Observado regional',color='#173c4c');plt.plot(f.Fecha,f.Pronostico,label='Proyección',color='#d5773b');plt.fill_between(f.Fecha,f.LI95,f.LS95,alpha=.2,color='#d5773b',label='Banda empírica nominal 95%');plt.ylabel('Personas ocupadas, rama agro');plt.legend(fontsize=8);fig('forecast')
 plt.figure(figsize=(8,3.5));s=pairs[pairs.Comuna.eq('Chimbarongo')].dropna(subset=['Lluvia_JJA']);plt.scatter(s.Lluvia_JJA,s.Cambio_empleo_interanual*100,color='#177e89')
 for _,v in s.iterrows():plt.annotate(str(v.Anio), (v.Lluvia_JJA,v.Cambio_empleo_interanual*100),fontsize=8)
 plt.xlabel('Lluvia JJA de Chimbarongo (mm)');plt.ylabel('Cambio empleo regional verano siguiente (%)');plt.axhline(0,c='grey',lw=.6);fig('lag')

def main():
 ag,n=cargar_agricultura();emp,year=cargar_empresas();climate=cargar_clima();market=cargar_mercado();e=cargar_empleo()
 r,cluster=priorizar(ag,emp,market);f,metrics,fc=forecast(e);pairs,cors=desfase(climate,e)
 save('DimComuna',pd.DataFrame({'CUT':list(CUT.values()),'Comuna':list(CUT.keys()),'Provincia':'Colchagua','Region':'O’Higgins'}))
 sectors=pd.read_csv(DATA/'FactSector.csv').Sector.unique();save('DimSector',pd.DataFrame({'Sector':sectors}))
 years=pd.DataFrame({'Anio':range(2005,2028)});save('DimAnio',years)
 cal=pd.DataFrame({'Fecha':pd.date_range('2013-01-01','2027-12-01',freq='MS')});cal['Anio']=cal.Fecha.dt.year;cal['Mes']=cal.Fecha.dt.month;cal['AnioMes']=cal.Fecha.dt.strftime('%Y-%m');save('DimFecha',cal)
 plots(r,climate,market,e,f,pairs)
 db=sqlite3.connect(ROOT/'datos/colchagua.sqlite')
 for path in DATA.glob('*.csv'):pd.read_csv(path).to_sql(path.stem,db,if_exists='replace',index=False)
 db.close()
 summary={'fecha_revision':'2026-10-03','hectareas':float(r.Ha_frutales.sum()),'bloques_catastro':n,'anio_sii':year,'prioridad':r.to_dict('records'),'cluster':cluster,'forecast':fc,'mercado_cereza':market[market.Producto.eq('Cereza')].to_dict('records'),'correlaciones':cors.to_dict('records'),'metricas':metrics.to_dict('records')}
 summary=json.loads(json.dumps(summary,ensure_ascii=False),parse_constant=lambda _:None)
 (ROOT/'resultados.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
 checks={'comunas':len(r),'hectareas_conciliadas':bool(np.isclose(r.Ha_frutales.sum(),33883.03)),'llaves_prioridad_unicas':not r.CUT.duplicated().any(),'meses_empleo_continuos':len(e),'clima_observado':int(pd.read_csv(DATA/'FactClima.csv').Lluvia_mm.notna().sum()),'faltantes_clima_preservados':int(pd.read_csv(DATA/'FactClima.csv').Lluvia_mm.isna().sum()),'PYME_no_imputada_por_sector':True,'archivos_datamart':len(list(DATA.glob('*.csv')))}
 (ROOT/'VERIFICACION_DATOS.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
 print(json.dumps({'checks':checks,'forecast':fc,'cluster':cluster,'top3':r.Comuna.head(3).tolist()},ensure_ascii=False,indent=2))
if __name__=='__main__':main()

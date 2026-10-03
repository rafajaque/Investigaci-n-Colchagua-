"""Genera consultas Power Query portables y configuración del modelo Power BI."""
from pathlib import Path
import json,base64
import pandas as pd
ROOT=Path(__file__).resolve().parent;DATA=ROOT/'datos/datamart';OUT=ROOT/'powerbi';OUT.mkdir(exist_ok=True)
e=pd.read_csv(DATA/'FactEmpleo.csv')[['Fecha','Ocupados_agro']].rename(columns={'Ocupados_agro':'Real'})
f=pd.read_csv(DATA/'FactForecast.csv');series=e.merge(f,on='Fecha',how='outer').sort_values('Fecha');series.to_csv(DATA/'SerieForecast.csv',index=False,encoding='utf-8-sig')
tables=[]
for p in sorted(DATA.glob('*.csv')):
 df=pd.read_csv(p,dtype={'CUT':str,'Codigo':str})
 cols=[];casts=[]
 for c in df:
  if c=='Fecha':dtype='DateTime';mtype='type datetime';fmt='MMM yyyy'
  elif pd.api.types.is_integer_dtype(df[c]):dtype='Int64';mtype='Int64.Type';fmt='#,0'
  elif pd.api.types.is_numeric_dtype(df[c]):dtype='Double';mtype='type number';fmt='#,0.00'
  else:dtype='String';mtype='type text';fmt=''
  if c in ['CUT','Codigo','AnioMes']:dtype='String';mtype='type text';fmt=''
  if c=='Anio':fmt='0'
  if c.startswith('Cuota_') or c in ['Dependencia_agro','Cambio_empleo_interanual','Cambio_valor_unitario','Cobertura95','Anomalia_lluvia']:fmt='0.0%'
  if c in ['HHI_cultivos','Silhouette','ARI','Pearson','Spearman','LOO_min','LOO_max','r_sin_2019_2021']:fmt='0.000'
  if c in ['Pronostico','Ocupados_agro','Real','Predicho','LI95','LS95','MAE','RMSE','Empleo_verano_OHiggins']:fmt='#,0'
  cols.append({'name':c,'dataType':dtype,'format':fmt})
  casts.append('{"'+c+'", '+mtype+'}')
 encoded=base64.b64encode(p.read_bytes()).decode()
 m='let\n    Binario = if RutaDatos = "" then Binary.FromText("'+encoded+'", BinaryEncoding.Base64) else File.Contents(RutaDatos & "\\'+p.name+'"),\n    Csv = Csv.Document(Binario,[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n    Encabezados = Table.PromoteHeaders(Csv,[PromoteAllScalars=true]),\n    Tipos = Table.TransformColumnTypes(Encabezados, {'+', '.join(casts)+'}, "en-US")\nin Tipos'
 (OUT/(p.stem+'.pq')).write_text(m,encoding='utf-8')
 tables.append({'name':p.stem,'columns':cols,'m':m})
relations=[]
names={t['name']:{c['name'] for c in t['columns']} for t in tables}
for t,cols in names.items():
 if t.startswith('Dim'):continue
 for c,dim in [('CUT','DimComuna'),('Sector','DimSector'),('Fecha','DimFecha'),('Anio','DimAnio')]:
  if c in cols:relations.append({'fact':t,'column':c,'dim':dim,'dimColumn':c})
measures=[
 ('FactPrioridad','Índice de prioridad','AVERAGE(FactPrioridad[Indice_prioridad])','0.0'),
 ('FactPrioridad','Empresas agro','SUM(FactPrioridad[Empresas_agro])','#,0'),
 ('FactPrioridad','Red potencial','SUM(FactPrioridad[Empresas_red_potencial])','#,0'),
 ('FactPrioridad','PYME de la comuna','SUM(FactPrioridad[PYME_total_comuna])','#,0'),
 ('FactPrioridad','Microempresas','SUM(FactPrioridad[Micro_total_comuna])','#,0'),
 ('FactPrioridad','Dependencia agro','DIVIDE(SUM(FactPrioridad[Empresas_agro]),SUM(FactPrioridad[Empresas_total]))','0.0%'),
 ('FactPrioridad','HHI promedio','AVERAGE(FactPrioridad[HHI_cultivos])','0.000'),
 ('FactPrioridad','Presencia top 3','MAX(FactPrioridad[Top3_escenarios])','0'),
 ('FactPrioridad','Riego por gravedad','DIVIDE(SUMX(FactPrioridad,FactPrioridad[Ha_frutales]*FactPrioridad[Cuota_riego_gravedad]),SUM(FactPrioridad[Ha_frutales]))','0.0%'),
 ('FactPrioridad','Exposición a cerezo','DIVIDE(SUMX(FactPrioridad,FactPrioridad[Ha_frutales]*FactPrioridad[Cuota_cerezo]),SUM(FactPrioridad[Ha_frutales]))','0.0%'),
 ('FactCultivo','Superficie frutícola','SUM(FactCultivo[Hectareas])','#,0.0'),
 ('FactSector','Empresas último año','VAR Ultimo = CALCULATE(MAX(FactSector[Anio]), ALL(DimAnio)) RETURN CALCULATE(SUM(FactSector[Empresas]), FILTER(ALL(DimAnio), DimAnio[Anio]=Ultimo))','#,0'),
 ('FactEmpleo','Empleo regional promedio','AVERAGE(FactEmpleo[Ocupados_agro])','#,0'),
 ('FactForecast','Pronóstico promedio','AVERAGE(FactForecast[Pronostico])','#,0'),
 ('FactInvierno','Lluvia de invierno','AVERAGE(FactInvierno[Lluvia_JJA])','0.0'),
 ('FactMercado','Valor unitario FOB','DIVIDE(SUM(FactMercado[USD_FOB]), SUM(FactMercado[Toneladas])*1000)','0.00'),
 ('FactMercado','Cambio unitario','AVERAGE(FactMercado[Cambio_valor_unitario])','0.0%'),
 ('FactMercado','Dependencia China','AVERAGE(FactMercado[Cuota_China_valor])','0.0%'),
 ('SerieForecast','Observado','AVERAGE(SerieForecast[Real])','#,0'),
 ('SerieForecast','Proyección','AVERAGE(SerieForecast[Pronostico])','#,0'),
 ('SerieForecast','Inferior 95','AVERAGE(SerieForecast[LI95])','#,0'),
 ('SerieForecast','Superior 95','AVERAGE(SerieForecast[LS95])','#,0'),
]
payload={'tables':tables,'relationships':relations,'measures':[dict(table=t,name=n,expression=e,format=f) for t,n,e,f in measures]}
(OUT/'modelo.json').write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8')
(OUT/'Medidas.dax').write_text('\n\n'.join(f'// Tabla: {t}\n{n} = {e}' for t,n,e,f in measures),encoding='utf-8')
print(f'{len(tables)} tablas, {len(relations)} relaciones y {len(measures)} medidas')

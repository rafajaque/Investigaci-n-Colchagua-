"""Escribe páginas PBIR en una copia del PBIX con el modelo ya guardado.
Uso: python crear_dashboard.py ruta/modelo_base.pbix ruta/Colchagua_Resiliencia.pbix
"""
import sys,json,zipfile,uuid
from pathlib import Path
source,target=map(Path,sys.argv[1:3])
with zipfile.ZipFile(source) as z:raw={n:z.read(n) for n in z.namelist()}
prefix='Report/definition/pages/'
schema='https://developer.microsoft.com/json-schemas/fabric/item/report/definition/'
docs={};order=[]
def uid():return uuid.uuid4().hex[:20]
def lit(v):return {'expr':{'Literal':{'Value':str(v)}}}
def text(v):return lit("'"+v.replace("'","''")+"'")
def col(t,c):return {'Column':{'Expression':{'SourceRef':{'Entity':t}},'Property':c}}
def meas(t,c):return {'Measure':{'Expression':{'SourceRef':{'Entity':t}},'Property':c}}
def proj(t,c,label=None,avg=False,measure=False):
 f=meas(t,c) if measure else col(t,c)
 if avg:f={'Aggregation':{'Expression':f,'Function':1}}
 return {'field':f,'queryRef':('Avg('+t+'.'+c+')') if avg else t+'.'+c,'nativeQueryRef':label or c}
def role(*p):return {'projections':list(p)}
def page(name,title,sub):
 p=uid();order.append(p)
 docs[prefix+p+'/page.json']={'$schema':schema+'page/2.3.1/schema.json','name':p,'displayName':name,'displayOption':'FitToPage','height':800,'width':1280,'objects':{'background':[{'properties':{'color':{'solid':{'color':text('#F3F7F8')}},'transparency':lit('0D')}}]}}
 note(p,title,sub,25,15,1230,78,25)
 return p
def note(p,title,body,x=25,y=708,w=1230,h=75,size=13):
 body_size=min(15,max(11,size-6))
 n=uid();docs[prefix+p+'/visuals/'+n+'/visual.json']={'$schema':schema+'visualContainer/2.13.0/schema.json','name':n,'position':{'x':x,'y':y,'z':30,'width':w,'height':h,'tabOrder':30},'visual':{'visualType':'textbox','objects':{'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':title,'textStyle':{'fontSize':str(size)+'pt','fontWeight':'bold','color':'#173C4C'}}]},{'textRuns':[{'value':body,'textStyle':{'fontSize':str(body_size)+'pt','color':'#58616A'}}]}]}}]}}}
def visual(p,typ,q,title,x,y,w,h):
 n=uid();v={'$schema':schema+'visualContainer/2.13.0/schema.json','name':n,'position':{'x':x,'y':y,'z':1,'width':w,'height':h,'tabOrder':1},'visual':{'visualType':typ,'query':{'queryState':q},'visualContainerObjects':{'title':[{'properties':{'show':lit('true'),'text':text(title),'fontSize':lit('14D'),'fontColor':{'solid':{'color':text('#173C4C')}}}}],'background':[{'properties':{'show':lit('true'),'color':{'solid':{'color':text('#FFFFFF')}},'transparency':lit('0D')}}]},'drillFilterOtherVisuals':True}}
 docs[prefix+p+'/visuals/'+n+'/visual.json']=v;return v
def filt(v,t,c,value):
 v['filterConfig']={'filters':[{'name':uid(),'expression':col(t,c),'type':'Categorical','filter':{'Version':2,'From':[{'Name':'s','Entity':t,'Type':0}],'Where':[{'Condition':{'In':{'Expressions':[{'Column':{'Expression':{'SourceRef':{'Source':'s'}},'Property':c}}],'Values':[[{'Literal':{'Value':"'"+value+"'"}}]]}}}]}}]}
def sort(v,t,c,desc=False,measure=False):v['visual']['query']['sortDefinition']={'sort':[{'field':meas(t,c) if measure else col(t,c),'direction':'Descending' if desc else 'Ascending'}],'isDefaultSort':True}
def table(p,t,columns,title,x,y,w,h):
 return visual(p,'tableEx',{'Values':role(*[proj(t,c,l,avg=ag,measure=m) for c,l,ag,m in columns])},title,x,y,w,h)
def slicer(p,t,c,title,x=1050,y=108,w=205,h=576):
 v=visual(p,'listSlicer',{'Values':role(proj(t,c))},title,x,y,w,h);v['visual']['query']['queryState']['Values']['projections'][0]['active']=True;return v
def line(p,t,date,fields,title,x,y,w,h):
 v=visual(p,'lineChart',{'Category':role(proj(t,date)),'Y':role(*[proj(t,c,l,avg=not m,measure=m) for c,l,m in fields])},title,x,y,w,h);sort(v,t,date);return v

p=page('1. Priorizar','COLCHAGUA | Dónde comenzar','Prioridad para diagnóstico de continuidad productiva · Catastro y empresas 2024 · Diez comunas')
for i,c in enumerate(['Empresas agro','Red potencial','PYME de la comuna','Microempresas']):
 visual(p,'card',{'Values':role(proj('FactPrioridad',c,measure=True))},c,25+i*253,108,246,146)
v=visual(p,'clusteredBarChart',{'Category':role(proj('DimComuna','Comuna')),'Y':role(proj('FactPrioridad','Índice de prioridad',measure=True))},'Prioridad relativa por comuna (0-100)',25,273,555,410);sort(v,'FactPrioridad','Índice de prioridad',True,True)
table(p,'FactPrioridad',[(c,l,False,False) for c,l in [('Comuna','Comuna'),('Puesto','Puesto'),('Top3_escenarios','Top 3 / 5')]],'Robustez: apariciones en top 3 de 5 escenarios',597,273,433,410)
slicer(p,'DimComuna','Comuna','Filtrar comuna')
note(p,'Chimbarongo y Placilla: prioridades robustas en cinco escenarios','El índice expresa una preferencia de diagnóstico. No es probabilidad ni pérdida estimada. PYMEs: pequeñas y medianas de todos los sectores. Red potencial: empresas de todos los tamaños.')

p=page('2. Agro y empresas','EXPOSICIÓN | Agricultura y proveedores','Comuna seleccionada: cultivos, riego y sectores empresariales · No se atribuye tamaño PYME a una actividad sin datos')
for i,c in enumerate(['Dependencia agro','Exposición a cerezo','Riego por gravedad','HHI promedio']):
 visual(p,'card',{'Values':role(proj('FactPrioridad',c,measure=True))},c,25+i*253,108,246,146)
v=visual(p,'clusteredBarChart',{'Category':role(proj('FactCultivo','Especie')),'Y':role(proj('FactCultivo','Superficie frutícola',measure=True))},'Hectáreas frutícolas por especie',25,273,505,410);sort(v,'FactCultivo','Superficie frutícola',True,True)
table(p,'FactSector',[('Sector','Sector',False,False),('Empresas último año','Empresas 2024',False,True)],'Empresas por vínculo potencial al agro',547,273,483,410)
slicer(p,'DimComuna','Comuna','Filtrar comuna')
note(p,'Fuentes: ODEPA-CIREN 2024 y SII 2024','HHI mide concentración de hectáreas; el riego por gravedad es un proxy, no una medición de eficiencia. Transporte, almacenamiento y comercio pueden tener clientes no agrícolas.')

p=page('3. Amenazas','AMENAZAS | Evidencia climática y comercial','Comparar mecanismos distintos sin confundir presencia de amenazas con daños económicos observados')
v=line(p,'FactInvierno','Anio',[('Lluvia_JJA','Lluvia JJA (mm)',False)],'Invierno: precipitación local',25,110,600,250);v['visual']['query']['queryState']['Series']=role(proj('FactInvierno','Comuna'))
v=line(p,'FactInvierno','Anio',[('Max24h_JJA','Máximo 24 h (mm)',False)],'Episodios intensos durante JJA',650,110,605,250);v['visual']['query']['queryState']['Series']=role(proj('FactInvierno','Comuna'))
v=line(p,'FactMercado','Temporada',[('Valor unitario FOB','USD FOB / kg',True)],'Cereza fresca nacional: temporadas completas',25,378,740,285);filt(v,'FactMercado','Producto','Cereza')
note(p,'-38,2%','Cambio de valor unitario de cereza entre 2023-24 y 2024-25.\n4,55 USD FOB/kg; 90,5% del valor enviado a China.\n\nEs una señal nacional; no el precio recibido por cada productor.',795,385,455,268,29)
note(p,'DMC 2017-2025 y ODEPA, boletín enero 2026','San Fernando agosto 2023 está faltante. Menor lluvia no prueba sequía agrícola; máximo diario no prueba inundación. No hay medición comparable de heladas, frío, incendios ni granizo.')

p=page('4. Desfase','DESFASE | Invierno y verano siguiente','JJA del año t → promedio de empleo diciembre t-febrero t+1 · Resultado laboral de toda la Región de O’Higgins')
v=visual(p,'scatterChart',{'Series':role(proj('ParesClimaEmpleo','Temporada')),'X':role(proj('ParesClimaEmpleo','Lluvia_JJA','Precipitación JJA (mm)',avg=True)),'Y':role(proj('ParesClimaEmpleo','Cambio_empleo_interanual','Cambio empleo interanual',avg=True))},'Chimbarongo: 9 pares de temporadas',25,115,705,550);filt(v,'ParesClimaEmpleo','Comuna','Chimbarongo')
v=table(p,'ParesClimaEmpleo',[(c,l,False,False) for c,l in [('Temporada','Temporada'),('Lluvia_JJA','JJA mm'),('Cambio_empleo_interanual','Cambio empleo')]],'Pares que sustentan el análisis',750,115,505,360);filt(v,'ParesClimaEmpleo','Comuna','Chimbarongo')
note(p,'r = 0,085 | n = 9','Pearson en cambios interanuales.\nSpearman = 0,067.\nRetirar una temporada: r entre -0,326 y 0,408.\nEl signo de la asociación no es estable.',755,493,485,179,23)
note(p,'Correlación no demuestra causalidad','Se comparan niveles, cambios, retiro de temporadas y exclusión de pandemia. Dos estaciones no se agrupan como observaciones laborales independientes. El clima no calibra pérdidas ni ajusta el forecast.')

p=page('5. Forecast','FORECAST | Escenario laboral de referencia','Empleo regional de la rama agricultura, ganadería, silvicultura y pesca · Mes central del trimestre móvil · Personas')
v=line(p,'SerieForecast','Fecha',[(c,c,True) for c in ['Observado','Proyección','Inferior 95','Superior 95']],'Historia, pronóstico y límites predictivos nominales 95%',25,112,1230,440)
note(p,'Verano 2026-27: 83.508 personas en promedio','Rango empírico del promedio: 71.425 a 93.549. Modelo: regresión temporal con dos armónicos anuales.\n162 observaciones históricas; corte julio 2026. Proyección agosto 2026-febrero 2027.',30,571,1210,112,23)
note(p,'El escenario normal no anticipa shocks nuevos','5.000 simulaciones en bloques de tres errores; semilla 802 y variación de parámetros. No sumar trimestres como puestos únicos. Banda aproximada, cobertura futura no garantizada. No es empleo comunal.')

p=page('6. Evaluar','EVALUACIÓN | Comprobar antes de proyectar','Selección en 2024 y prueba posterior en 2025 · Dos meses centrales de purga antes de cada bloque para evitar solapamiento ENE')
table(p,'MetricasForecast',[(c,l,False,False) for c,l in [('Etapa','Etapa'),('Modelo','Modelo'),('MAE','MAE personas'),('RMSE','RMSE personas'),('Cobertura95','Cobertura'),('N','n')]],'Comparación temporal fuera de entrenamiento',25,113,1230,265)
table(p,'Evaluacion_clusters',[(c,c,False,False) for c in ['k','Silhouette']],'K-means: comparar cantidad de grupos',25,395,430,280)
note(p,'Modelo seleccionado: regresión estacional','Gana por poco en 2024, pero el ingenuo estacional logra menor MAE en 2025.\n\nSe conserva la selección previa para no reutilizar la prueba como selección. Resultado provisional: requiere seguimiento con nuevos datos.\n\nK-means: k=2, silhouette 0,379; ARI medio 0,949 y mínimo 0,493 al retirar una comuna.',480,400,768,272,22)
note(p,'Evaluar no significa ocultar un modelo simple que funciona mejor','Las 12 observaciones de prueba son trimestres solapados. Cobertura 12/12 con bandas amplias no certifica 95%. Los clústeres son perfiles exploratorios de diez comunas, sin etiquetas de daños.')

p=page('7. Decidir','DECISIÓN | Plan de diagnóstico y seguimiento','Propuesta de 30 días para un equipo provincial de fomento · Metas propuestas, intervención aún no ejecutada')
note(p,'1 · Chimbarongo y Placilla','Validar contrapartes municipales. Contactar productores y proveedores potenciales. Revisar exposición a clientes agrícolas, contratos, riego y continuidad ante eventos intensos.',25,115,600,177,21)
note(p,'2 · Tercer cupo condicionado','Palmilla en escenario base. San Fernando si prima exposición a cereza; Nancagua si prima adaptación hídrica. Documentar criterio y verificar datos antes de decidir.',650,115,605,177,21)
note(p,'3 · Levantar el eslabón que falta','Piloto propuesto: 10 organizaciones por cada comuna robusta. Verificar tamaño, proporción real de ventas al agro, liquidez y dependencia de clientes. No asignar subsidios usando solo el índice.',25,310,600,183,21)
note(p,'4 · Medir la ejecución','Meta propuesta: 20 fichas completas, 2 contrapartes municipales, fuente y fecha en el 100% de fichas y una acción de continuidad por organización. Medir resultados posteriormente.',650,310,605,183,21)
note(p,'Alcance y transparencia','No hay datos empresariales identificables ni red observada de clientes. Clima local: dos estaciones; empleo regional; mercado nacional. Heladas, horas de frío, incendios, granizo y daños siguen como brechas.\n\nIA: ChatGPT/Codex apoyó extracción, código y redacción. El equipo debe revisar y defender decisiones. Fuentes, código, informe, matriz de requisitos y guía de defensa se incluyen en el ZIP.',25,525,1230,157,18)
note(p,'Actualizar con trazabilidad','Reejecutar analisis.py y generar_modelo.py. En Power Query, RutaDatos vacía usa la instantánea integrada; con ruta al directorio datos/datamart actualiza desde CSV. No descarga automáticamente nuevas fuentes.')

docs[prefix+'pages.json']={'$schema':schema+'pagesMetadata/1.1.0/schema.json','pageOrder':order,'activePageName':order[0]}
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in raw.items():
  if n.startswith(prefix) or n=='SecurityBindings':continue
  if n=='[Content_Types].xml':b=b.replace(b'<Override PartName="/SecurityBindings" ContentType="" />',b'')
  if n=='DiagramLayout':continue
  z.writestr(n,b)
 for n,d in docs.items():z.writestr(n,json.dumps(d,ensure_ascii=False).encode())
with zipfile.ZipFile(target) as z:assert z.testzip() is None;assert z.read('DataModel')==raw['DataModel']
print(f'Creado: {target}; 7 páginas, {len(docs)-8} visuales')

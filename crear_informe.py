from pathlib import Path
import json,hashlib,csv,io,contextlib,base64,datetime,shutil
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
ROOT=Path(__file__).resolve().parent;DATA=ROOT/'datos/datamart';OUT=ROOT/'informe';OUT.mkdir(exist_ok=True)
S=json.loads((ROOT/'resultados.json').read_text(encoding='utf-8'))
F=S['forecast'];R=pd.read_csv(DATA/'FactPrioridad.csv');M=pd.read_csv(DATA/'MetricasForecast.csv');C=pd.read_csv(DATA/'Correlaciones.csv');market=pd.read_csv(DATA/'FactMercado.csv')
def es(x,n=0):return f'{x:,.{n}f}'.replace(',','@').replace('.',',').replace('@','.')
FONT=Path('C:/Windows/Fonts')
if FONT.exists():normal=FONT/'arial.ttf';bold=FONT/'arialbd.ttf'
else:
 import reportlab
 FONT=Path(reportlab.__file__).parent/'fonts';normal=FONT/'Vera.ttf';bold=FONT/'VeraBd.ttf'
pdfmetrics.registerFont(TTFont('Body',str(normal)));pdfmetrics.registerFont(TTFont('Bold',str(bold)))
W,H=595.28,841.89;L=43;RW=W-2*L
pdf=canvas.Canvas(str(OUT/'Informe_Colchagua.pdf'),pagesize=(W,H));pdf.setTitle('Colchagua: priorización para la resiliencia agrícola');pdf.setAuthor('Proyecto ISI802')
navy=colors.HexColor('#173C4C');teal=colors.HexColor('#177E89');grey=colors.HexColor('#58616A')
style=ParagraphStyle('body',fontName='Body',fontSize=10.2,leading=14.3,textColor=navy,spaceAfter=8)
small=ParagraphStyle('small',parent=style,fontSize=8.2,leading=11)
head=ParagraphStyle('head',parent=style,fontName='Bold',fontSize=13,leading=17,textColor=teal)
y=0
def page(n,title,subtitle):
 global y
 if n>1:pdf.showPage()
 pdf.setFillColor(teal);pdf.rect(0,H-12,W,12,fill=1,stroke=0)
 pdf.setFont('Bold',9);pdf.setFillColor(grey);pdf.drawString(L,H-37,'ISI802  /  BUSINESS INTELLIGENCE  /  03 OCT 2026')
 p=Paragraph(title,ParagraphStyle('title',parent=head,fontSize=24,leading=28,textColor=navy));_,h=p.wrap(RW,100);p.drawOn(pdf,L,H-60-h)
 y=H-68-h;p=Paragraph(subtitle,small);_,h=p.wrap(RW,80);p.drawOn(pdf,L,y-h);y-=h+20
 pdf.setStrokeColor(colors.HexColor('#D8E1E3'));pdf.line(L,34,W-L,34);pdf.setFont('Body',8);pdf.setFillColor(grey);pdf.drawString(L,22,'Colchagua | Diagnóstico y priorización, no estimación causal de pérdidas');pdf.drawRightString(W-L,22,str(n)+' / 8')
def p(text,kind=None):
 global y
 item=Paragraph(text,kind or style);_,h=item.wrap(RW,700);assert y-h>44,(text[:70],y,h);item.drawOn(pdf,L,y-h);y-=h+9
def h(text):p(text,head)
def table(headers,rows,widths=None):
 global y
 cells=[[Paragraph(str(x),ParagraphStyle('th',parent=small,fontName='Bold',textColor=colors.white)) for x in headers]]+[[Paragraph(str(x),small) for x in row] for row in rows]
 t=Table(cells,colWidths=widths or [RW/len(headers)]*len(headers),hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),navy),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F0F5F5')]),('LINEBELOW',(0,-1),(-1,-1),.5,colors.HexColor('#D8E1E3'))]))
 _,height=t.wrap(RW,700);assert y-height>44,('table',y,height);t.drawOn(pdf,L,y-height);y-=height+12
def picture(name,height):
 global y
 img=ImageReader(str(OUT/'figuras'/f'{name}.png'));iw,ih=img.getSize();width=min(RW,height*iw/ih);hh=width*ih/iw
 assert y-hh>44;pdf.drawImage(img,L+(RW-width)/2,y-hh,width,hh);y-=hh+10

page(1,'¿Dónde priorizar apoyo al agro y su red de proveedores?','Problema abierto, datos observados y una decisión territorial concreta.')
p('<b>Pregunta central.</b> ¿Qué comunas y sectores de Colchagua presentan mayor exposición y dependencia frente a distintos shocks agrícolas, qué amenazas cuentan con evidencia suficiente y dónde conviene iniciar un diagnóstico de continuidad productiva para productores y PYMEs?')
p('<b>Problema operativo.</b> Un equipo provincial de fomento dispone de capacidad limitada para visitar empresas. Necesita ordenar las comunas y los grupos de actividad a contactar antes de la temporada 2026-27. Este trabajo entrega una priorización auditable; no asigna subsidios ni identifica empresas individuales sin antecedentes propios.')
h('Respuesta que permite actuar')
p('<b>Chimbarongo y Placilla son el núcleo más robusto de la prioridad:</b> ambas permanecen en el top 3 de los cinco escenarios de ponderación. Palmilla ocupa el tercer lugar del escenario base, pero oscila entre los puestos 3 y 6. El tercer cupo debe resolverse según el objetivo de la visita y una verificación municipal.')
table(['Evidencia incorporada','Cobertura y uso'],[
 ['33.883,03 ha frutícolas','Catastro ODEPA-CIREN 2024; las 10 comunas. Especies y riego.'],
 ['23.603 empresas; 5.660 del agro','SII 2024. La red potencial de proveedores suma 2.832 empresas de cualquier tamaño.'],
 ['4.229 PYMEs y 14.289 microempresas','Totales comunales de todos los sectores. No es posible cruzar tamaño × actividad con estas tablas.'],
 ['9 inviernos, 2 estaciones','DMC 2017-2025: precipitación y máximo de 24 horas. Un mes faltante se conserva.'],
 ['162 observaciones de empleo','INE: rama agro en O’Higgins, feb. 2013-jul. 2026; trimestres móviles.']],[175,RW-175])
h('Objetivo y alcance')
p('Integrar fuentes, construir un datamart, segmentar comunas, evaluar un forecast y convertir resultados en un plan de levantamiento de información. Se exploran amenazas climáticas y de mercado antes de priorizar. El alcance territorial del ranking es Colchagua; el empleo y las exportaciones mantienen sus niveles regional y nacional.',small)

page(2,'Fuentes y modelo de datos','Se respetan los distintos territorios, unidades y períodos de observación.')
table(['Fuente / versión','Grano y justificación','Control principal'],[
 ['ODEPA-CIREN, catastro 2024','Bloques de plantación; se agregan por comuna, especie y riego. Mide exposición productiva.','11.479 registros locales; conciliación de hectáreas.'],
 ['SII, ACT_V2 2021-24','Comuna-año-actividad. Mide dependencia empresarial y oferta potencial de servicios.','Miles con punto; * es secreto tributario.'],
 ['SII, TRAM5_COMU 2005-24','Comuna-año-tamaño por ventas. Delimita PYMEs sin inventar su sector.','Totales 2024 coinciden con actividad.'],
 ['DMC, anuarios 2017-25','Estación-mes: JJA. Presencia de menor lluvia y episodios intensos.','Página y URL por observación; 53/54 datos válidos.'],
 ['ODEPA, boletín enero 2026','Exportaciones por temporada, especie y destino; agregación nacional.','Solo temporadas completas 2016-17 a 2024-25.'],
 ['INE, rama.xlsx, hoja LI','Región-trimestre móvil. Contexto laboral y forecast con historia larga.','Miles a personas; mes central, sin duplicación comunal.']],[122,218,RW-340])
h('Datamart dimensional')
p('<b>DimComuna (CUT)</b> filtra hechos de cultivo, actividad, sector, tamaño, prioridad y clima. <b>DimAnio</b> filtra hechos anuales. <b>DimFecha</b> filtra empleo, clima mensual y forecast. <b>DimSector</b> filtra actividad y agregados sectoriales. Relaciones 1 a muchos, con filtro en una dirección.')
p('El conjunto es una <b>constelación de estrellas</b>: no se mezclan todos los granos en una tabla. El empleo regional y el mercado nacional no tienen relación por comuna. Seleccionar una comuna no los convierte en datos locales. Las tablas de evaluación y sensibilidad se conservan como resultados analíticos separados.')
p('Se entregan originales, 22 CSV, SQLite, consultas Power Query y 22 medidas DAX. El PBIX lleva copias de datos integradas para abrir y actualizar la instantánea sin rutas del equipo original; RutaDatos permite usar los CSV regenerados.',small)

page(3,'Prioridad territorial y sus límites','Ranking base con datos agrícolas y empresariales de 2024.')
table(['Puesto / comuna','Índice','Agro / empresas','Cerezo / ha','Top 3*'],[[f'{int(v.Puesto)}. {v.Comuna}',es(v.Indice_prioridad,1),es(v.Dependencia_agro*100,1)+'%',es(v.Cuota_cerezo*100,1)+'%',f'{int(v.Top3_escenarios)}/5'] for _,v in R.iterrows()],[147,57,108,100,RW-412])
p('*Frecuencia entre los tres primeros en cinco escenarios de pesos. No representa probabilidad. El índice está normalizado dentro de estas diez comunas; un valor bajo no equivale a ausencia de vulnerabilidad.',small)
h('Cómo se construyó')
p('Índice = 100 × [0,35 × dependencia agro + 0,25 × HHI de especies + 0,20 × riego por gravedad + 0,20 × exposición a cerezo], luego de normalizar cada componente mediante (x - mínimo)/(máximo - mínimo). La dependencia es empresas de producción agropecuaria y servicios agrícolas sobre todas las empresas. HHI = suma de las cuotas de superficie al cuadrado.')
p('Los pesos son una <b>preferencia de decisión declarada</b>, no parámetros aprendidos ni efectos causales. La cereza se incorpora por su importancia local y la caída observada del valor unitario; la concentración y la cuota de cerezo pueden compartir información, por lo que se revisan pesos alternativos. El riego por gravedad es un proxy de adaptación; no mide consumo de agua ni disponibilidad efectiva.')
h('Qué aporta la segmentación')
p(f'K-means compara k=2, 3 y 4 con variables estandarizadas. Se elige k={S["cluster"]["k"]}, silhouette {es(S["cluster"]["silhouette"],3)}. La estabilidad al retirar una comuna tiene ARI medio {es(S["cluster"]["ARI_medio"],3)} y mínimo {es(S["cluster"]["ARI_min"],3)}. Los grupos son perfiles exploratorios; no se etiquetan como riesgo real validado. El índice explícito guía la prioridad y los clústeres ayudan a entenderla.',small)

page(4,'Amenazas: qué muestran los datos','La magnitud de un indicador no demuestra cuánto daño económico provocó.')
picture('clima',175)
p('<b>Déficit relativo de lluvia.</b> En Chimbarongo, JJA 2019 sumó 102,4 mm y JJA 2025, 228,7 mm. La comparación se realiza contra el promedio 2017-2022 de la misma estación, una referencia corta que <b>no es una normal climática de 30 años</b>. San Fernando aporta una segunda estación; agosto 2023 está ausente y su invierno no se suma como completo.')
p('<b>Episodios intensos.</b> El máximo de 24 horas de JJA en Chimbarongo llega a 82,5 mm en 2024. El mismo territorio requiere preparación para baja lluvia y para episodios intensos. Estos registros no prueban inundación, pérdidas de cultivos ni daños en empresas.')
picture('mercado',151)
p('<b>Mercado de cereza fresca.</b> Entre las temporadas completas 2023-24 y 2024-25, el valor unitario nacional pasó de 7,36 a 4,55 USD FOB/kg (-38,2%), mientras el volumen aumentó 51,2%. China concentró 90,5% del valor en 2024-25. El valor unitario no es el precio recibido por cada productor ni controla calidad o mezcla de destinos.',small)
p('<b>Conclusión comparativa.</b> Hay señales verificables de presión comercial y variabilidad de lluvia. Su interacción con la especialización local justifica prevención. No se puede ordenar su efecto causal sobre PYMEs. Heladas, horas de frío, incendios y granizo quedan como brechas de medición, no como amenazas descartadas.',small)

page(5,'Alinear invierno y temporada siguiente','Un desfase correcto es necesario, pero no basta para atribuir causalidad.')
table(['Indicador adelantado','Resultado posterior','N observado'],[
 ['Junio-agosto del año t, estación DMC','Promedio del empleo regional en diciembre t-febrero t+1','9 pares Chimbarongo; 8 San Fernando'],
 ['Lluvia y máximo de 24 h','Cambio de ese empleo respecto del verano previo','Se controla parcialmente tendencia con variación interanual']],[163,244,RW-407])
picture('lag',220)
p('<b>Resultado central:</b> lluvia JJA de Chimbarongo frente al cambio del empleo del verano siguiente: Pearson r = 0,085 y Spearman = 0,067, con 9 temporadas. Al retirar una temporada, Pearson varía entre -0,326 y 0,408. Sin los inviernos 2019-2021 (temporadas afectadas por pandemia), r = -0,448. El signo no es estable.')
p('La relación en niveles es distinta (r = -0,282), lo que confirma que la transformación importa. En San Fernando, r = 0,395 en cambios, pero Spearman = 0,024 y solo hay 8 pares. Los resultados de ambas estaciones se calculan por separado: no se cuentan como 17 observaciones económicas independientes.')
h('Interpretación defendible')
p('No hay evidencia robusta para convertir milímetros de lluvia en empleos perdidos. Hay desajuste espacial entre dos estaciones locales y empleo de toda la región, una muestra corta y factores omitidos: precios, superficie, tecnología, pandemia y oferta laboral. Por ello el clima <b>no ajusta numéricamente el forecast</b>. Se utiliza como señal de seguimiento y como motivación para ampliar el diagnóstico.')

page(6,'Forecast con prueba temporal','Ocupación de la rama agro en O’Higgins; no empleo comunal ni solo temporeros.')
picture('forecast',215)
table(['Etapa','Modelo','MAE personas','RMSE personas'],[[v.Etapa,v.Modelo,es(v.MAE),es(v.RMSE)] for _,v in M.iterrows()],[150,155,100,RW-405])
p('<b>Sin fuga entre trimestres:</b> se purgan dos meses centrales antes de cada bloque. Para seleccionar se entrena hasta octubre 2023 y se evalúa enero-diciembre 2024; para la prueba posterior, hasta octubre 2024 y se evalúa enero-diciembre 2025. La regresión usa tendencia y dos armónicos anuales. Se compara con repetir el mismo mes del año anterior.')
p(f'La regresión se elige por el MAE de 2024; en 2025 el ingenuo logra menor error. Se mantiene la regla de selección para no reutilizar la prueba como selección. Tras reajustar hasta julio 2026, se proyecta agosto 2026-febrero 2027. Para diciembre-febrero: <b>promedio {es(F["media_verano"])} personas</b>, intervalo predictivo empírico nominal 95% de <b>{es(F["LI_verano"])} a {es(F["LS_verano"])}</b>.')
p('Bandas: 5.000 simulaciones, semilla 802, bloques de tres residuos y variación de parámetros de la regresión. El promedio estival se obtiene por trayectoria; no se suman empleos ni límites mensuales. La cobertura de prueba fue 12/12 para ambos modelos: muestra pequeña y bandas amplias, no certificación de 95%. Las bandas no garantizan ensancharse de forma monótona con el horizonte.',small)
p('Escenario normal condicionado a patrones históricos. Una baja hipotética del 10% daría aproximadamente 75.157 personas: es sensibilidad, no efecto estimado de sequía o precio. Se requiere actualizar el modelo cuando lleguen nuevas publicaciones.',small)

page(7,'De los resultados a una intervención','Propuesta operativa para un equipo provincial de fomento; no ejecutada.')
table(['Prioridad','Acción y destinatarios','Verificación'],[
 ['1. Chimbarongo','Contactar productores, servicios agrícolas y proveedores. Revisar exposición a cerezo y contratos; diagnóstico de riego y continuidad ante lluvia intensa.','Lista municipal depurada; participación de clientes agrícolas y calendario de pagos.'],
 ['2. Placilla','Diagnóstico de riego y continuidad: 32,0% de superficie con métodos por gravedad y 41,6% de empresas en agro.','Método y disponibilidad efectiva de agua; protocolos de operación y transporte.'],
 ['3. Cupo condicionado','Palmilla en escenario base; revisar San Fernando si el foco es cereza, o Nancagua si prima adaptación hídrica.','Documentar objetivo, pesos y motivo de elección; no decidir por una centésima del índice.'],
 ['Red de proveedores','1.193 empresas de servicios agrícolas, 1.371 de transporte/almacenamiento, 255 de comercio agroalimentario y 13 de procesamiento.','Son grupos potencialmente vinculados, no clientes observados ni PYMEs acreditadas.']],[97,255,RW-352])
h('Plan de 30 días propuesto')
p('<b>Días 1-5:</b> contraparte provincial valida las dos comunas robustas, responsable municipal y cobertura de fuentes. <b>Días 6-15:</b> muestra piloto propuesta de 10 organizaciones por comuna prioritaria; consentimiento, tamaño SII y dependencia real de ventas agrícolas. <b>Días 16-25:</b> matriz de continuidad, riego, diversificación comercial y liquidez para cada organización que responda. <b>Días 26-30:</b> revisar el ranking con nuevos datos y acordar seguimiento.')
p('<b>Indicadores de ejecución propuestos:</b> 2 comunas priorizadas con contraparte, 20 fichas completas, 100% de fichas con fuente y fecha, y al menos una acción acordada por organización participante. Son metas de la intervención, no logros de esta investigación. Medir después ventas, atrasos y días de interrupción; un cambio no se atribuye al programa sin diseño de evaluación.')
h('Mecanismo que debe contrastarse')
p('Shock climático o comercial → producción o margen agrícola → demanda de servicios, logística y procesamiento → caja y empleo local. El eslabón empresa-cliente no está en los datos públicos usados. Debe levantarse antes de afirmar un efecto dominó cuantificado. El producto resuelve la primera decisión: dónde iniciar ese levantamiento con criterios trazables.',small)

page(8,'Reproducibilidad, defensa y fuentes','Entrega auditable y preparada para repositorio; evaluación académica a cargo del docente.')
h('Reproducir y comprobar')
p('Crear un entorno Python, instalar requirements.txt y ejecutar analisis.py, generar_modelo.py y crear_informe.py. El notebook ejecutado documenta cada etapa. Los datos originales se conservan con SHA-256 y el ETL no requiere conexión. SQLite y CSV permiten reconstruir las tablas. Para reflejar nuevos resultados en Power BI, establecer RutaDatos al directorio datos/datamart y actualizar.')
h('Brechas que no deben ocultarse')
p('No hay microdatos de empresas identificables, cruce comunal tamaño × actividad, red real de clientes/proveedores, daños observados ni horas de frío. Dos estaciones no representan las diez comunas. Superficie frutícola no cubre toda la agricultura ni la vid vinífera. SII registra domicilio tributario y una actividad principal; las celdas suprimidas no permiten sumar ventas completas. Las exportaciones son nacionales y revisables por IVV. El clima termina en 2025; no se atribuye una amenaza al invierno 2026 sin datos.')
h('Uso de IA y criterio humano')
p('Se utilizó ChatGPT/Codex para auditoría de archivos, búsqueda y extracción de fuentes, programación del ETL y modelos, documentación y elaboración de artefactos. No se inventaron observaciones faltantes. El equipo debe revisar los supuestos, entender el alcance y defender la priorización. La defensa oral y la calificación no pueden acreditarse con un archivo.')
h('Referencias principales')
p('ODEPA-CIREN. (2024). <i>Catastro frutícola 2024</i>, dataset de bloques. datos.odepa.gob.cl/dataset/catastro-fruticola.<br/>Servicio de Impuestos Internos. <i>Estadísticas de empresas</i>, PUB_COMU_ACT_V2 y PUB_TRAM5_COMU, datos hasta 2024. sii.cl/sobre_el_sii/estadisticas_de_empresas.html.<br/>Dirección Meteorológica de Chile. (2017-2025). <i>Anuarios climatológicos</i>, tablas de precipitación. climatologia.meteochile.gob.cl/publicaciones/anuario/.<br/>ODEPA. (14 enero 2026). <i>Boletín de fruta</i>, archivo Exportaciones-por-temporada0126.xlsx. odepa.gob.cl/publicaciones/boletines/boletin-de-fruta-enero-2026.<br/>INE. <i>Encuesta Nacional de Empleo, serie por rama de actividad</i>, hoja LI del archivo rama.xlsx proporcionado. ine.gob.cl/estadisticas/sociales/mercado-laboral/ocupacion-y-desocupacion.',small)
p('URLs exactas, páginas DMC, fecha de consulta, procedencia y hashes están en FUENTES.csv y MANIFIESTO_SHA256.csv. Algunas bases SII e INE se recuperaron del material existente: la fecha de descarga original no está acreditada y se distingue de la revisión del 03-10-2026.',small)
p('<b>Correspondencia de evaluación:</b> fuentes (p. 2 y 8), problema abierto (p. 1 y 4), ETL/datamart (p. 2 y código), dashboard (PBIX), ML/forecast (p. 3, 5 y 6), hallazgos/defensa (p. 3-8). MATRIZ_CUMPLIMIENTO.csv detalla la evidencia. Solo se recibió una rúbrica puntuada; la guía de Forecast se auditó como segunda lista de requisitos.',small)
pdf.save()

# Documentación completa y matriz de evidencia: no autoasignar una nota.
readme='''# Colchagua: resiliencia agrícola y priorización de apoyo

Entrega reconstruida el 03-10-2026. Abrir `Colchagua_Resiliencia.pbix` y `informe/Informe_Colchagua.pdf`.

## Problema y decisión
¿Qué comunas, sectores y grupos de PYMEs de Colchagua deben priorizarse para diagnosticar y reducir exposición a shocks agrícolas, considerando amenazas climáticas, comerciales y dependencia productiva?

Se prioriza el levantamiento de información y planes de continuidad. No se afirma haber reducido pérdidas ni identificado empresas individuales. Chimbarongo y Placilla son robustas al cambio de pesos. El tercer cupo depende de la orientación del programa.

## Contenido
- Notebook `Colchagua_Resiliencia.ipynb`, ejecutado, y `analisis.py`: ETL, modelo dimensional, índice, K-means, sensibilidad, lag, forecast y verificaciones.
- `Colchagua_Resiliencia.pbix`: dashboard y datamart nuevo, medidas DAX y consultas Power Query.
- `informe/Informe_Colchagua.pdf`: informe de ocho páginas.
- `datos/originales`: originales inalterados utilizados; los TXT SII se extrajeron byte a byte del ZIP oficial disponible.
- `datos/datamart`: resultados CSV; `datos/colchagua.sqlite`: copia consultable.
- `powerbi/`: consultas .pq, medidas, configuración del modelo y script opcional para reconstrucción mediante motor local de Desktop.
- `FUENTES.csv`, `MANIFIESTO_SHA256.csv`, `DICCIONARIO_DATOS.csv`, `MATRIZ_CUMPLIMIENTO.csv`, `VERIFICACION_DATOS.json` y `CAMBIOS_REALIZADOS.txt`.
- `DEFENSA.md`: preguntas y respuestas para preparar la exposición.

## Ejecutar
Python 3.11 o 3.12 recomendado. En una terminal situada en esta carpeta:
```
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python analisis.py
python generar_modelo.py
python crear_informe.py
```
El código usa rutas relativas a sus propios archivos. El notebook se ejecuta desde esta carpeta con Jupyter. Puede revisarse en GitHub sin instalar nada. En Colab, subir y descomprimir el ZIP y cambiar el directorio de trabajo a su carpeta antes de ejecutar; instalar requirements.txt. El informe utiliza Arial cuando está disponible en Windows y, en otros sistemas, la fuente Vera incluida con ReportLab.

`analisis.py` reconstruye CSV, SQLite, gráficos y resultados; `generar_modelo.py` añade SerieForecast y genera consultas portables; `crear_informe.py` regenera el PDF, documentación, notebook ejecutado y manifiesto. El PBIX no se reescribe al ejecutar Python: para actualizarlo abrir Power Query > Administrar parámetros > RutaDatos y establecer el directorio absoluto `datos/datamart`, luego Actualizar. Si RutaDatos es una cadena vacía, se usa la instantánea integrada y se actualiza sin rutas externas; esto no descarga fuentes nuevas. Para volver a integrar una instantánea nueva, regenerar las consultas o usar el script documentado.

## Criterios de datos
Los CUT se mantienen como texto de cinco dígitos. El empleo regional no se replica por comuna. Los trimestres móviles se etiquetan por mes central, sin tratarlos como observaciones independientes. Las empresas no se suman entre años. Ventas SII suprimidas quedan vacías: `Ventas_UF_observadas` es un subtotal observado, no venta total. El tamaño empresarial es por ventas; PYMEs = pequeñas + medianas, microempresas separadas. No existe el cruce tamaño-actividad usado para atribuir PYMEs al agro.

Catastro: sumar área de bloques; no eliminar registros idénticos sin llave única porque pueden representar bloques diferentes. No incluye todas las actividades agrícolas ni necesariamente toda la viticultura. HHI usa cuotas de hectáreas. Surco, tendido y platabanda se agrupan como riego por gravedad; esto no certifica eficiencia. No se usan RUT, nombres personales ni domicilios.

Clima: dos estaciones, nueve inviernos. Se transcriben lluvia y máximo de 24 h para cada mes JJA, con referencias de página. Un punto en DMC significa faltante; S/P significa sin precipitación (DMC 2024, p. PDF 273), distinto de falta de dato. Solo se utilizan números explícitos en las filas JJA elegidas. San Fernando agosto 2023 queda faltante. El promedio 2017-2022 es referencia corta, no normal climática. El forecast es regional y no usa lluvia como predictor.

Mercado: valor unitario FOB = USD/toneladas/1000, nacional, fruta fresca, temporadas septiembre-agosto. Se excluye 2025-26 por ser parcial en el boletín de enero 2026. Las cifras pueden ser revisadas por IVV; no equivalen a precios netos del productor.

## Modelos y evaluación
Índice relativo con pesos explícitos 35/25/20/20 y normalización min-max. Sensibilidad: pesos iguales, mayor peso agro, agua y mercado. No es probabilidad ni pérdida económica. K-means de Lloyd implementado con NumPy, 50 inicializaciones, semilla 802; seleccionar k=2..4 por silhouette. La estabilidad ARI al retirar comunas es exploratoria; no sustituye validación de riesgo observado.

Forecast: regresión temporal con dos armónicos anuales frente al ingenuo estacional. Selección 2024, prueba 2025, purga de dos meses centrales antes de cada bloque por solapamiento ENE. La regla elige regresión en 2024, aunque el ingenuo gana en 2025. Se informa esta debilidad, sin cambiar de modelo con la misma prueba. 5.000 simulaciones en bloques de tres errores, más incertidumbre de parámetros de OLS. Bandas predictivas nominales 95%, cobertura no garantizada. La prueba tiene solo 12 trimestres solapados. El pronóstico llega a febrero 2027 desde el corte julio 2026 y no incorpora los meses posteriores como observados.

## Publicación y rúbricas
Preparado para repositorio, sin .git ni credenciales. No se publicó en GitHub ni en Power BI Service. Publicar corresponde a una decisión posterior. Se entregó una rúbrica de 100 puntos en ISI802_Trabajo_Colchagua.pdf; ISI802_Guia_Forecast.pdf es guía, no segunda rúbrica puntuada. La matriz cubre ambas referencias conocidas. No puede certificarse una pauta no proporcionada ni la defensa oral. No se promete 100/100.
'''
(ROOT/'README.md').write_text(readme,encoding='utf-8')
(ROOT/'requirements.txt').write_text('numpy>=1.26\npandas>=2.2\nmatplotlib>=3.8\nopenpyxl>=3.1\nreportlab>=4\njupyter>=1\n',encoding='utf-8')
matrix=[
 ('Trabajo','Fuentes reales justificadas',20,'Implementado','FUENTES.csv; informe p.2 y 8; originales y hashes','Fecha original INE/SII no acreditada; se declara recepción/revisión.'),
 ('Trabajo','Planteamiento abierto',15,'Implementado','Informe p.1 y 4; comparación de lluvia, episodios intensos y mercado','No se puede estimar qué amenaza causó mayores pérdidas.'),
 ('Trabajo','ETL y datamart',20,'Implementado','Notebook, analisis.py, SQLite, CSV, Power Query y relaciones PBIX','Constelación de estrellas; fuentes con granos distintos.'),
 ('Trabajo','Dashboard Power BI',15,'Implementado; ver VERIFICACION_POWERBI.txt','Colchagua_Resiliencia.pbix; powerbi/Medidas.dax','Actualización de nuevas fuentes requiere regenerar el ETL y definir RutaDatos.'),
 ('Trabajo','ML / Forecast',15,'Implementado y evaluado','K-means silhouette/ARI; sensibilidad; holdout temporal; informe p.3 y 6','Muestra 10 comunas; modelo elegido no gana en prueba.'),
 ('Trabajo','Hallazgos y defensa',15,'Documentado; defensa oral pendiente','Informe p.3-8 y DEFENSA.md','La capacidad del equipo y nota docente no se verifican con archivos.'),
 ('Forecast','Historia real y ciclos completos',None,'Implementado','FactEmpleo.csv: 162 meses centrales, rama regional','Son trimestres móviles, no meses independientes.'),
 ('Forecast','Tendencia y estacionalidad',None,'Implementado','Regresión con tendencia y armónicos anuales','Se compara contra ingenuo; los patrones pueden cambiar.'),
 ('Forecast','Intervalo e interpretación',None,'Implementado','FactForecast.csv y PDF p.6','Intervalo predictivo nominal; cobertura futura no certificada.'),
 ('Forecast','Desfase invierno-verano',None,'Implementado','ParesClimaEmpleo.csv; informe p.5','Dos estaciones locales frente a empleo regional.'),
 ('Forecast','Scatter y correlación no causal',None,'Implementado','Correlaciones.csv, sensibilidad LOO y exclusión pandemia','8 o 9 temporadas; no efecto causal.'),
 ('Forecast','Train/test, MAE y RMSE',None,'Implementado','MetricasForecast.csv, ValidacionForecast.csv','Purga 2 meses; modelo elegido antes de test; test peor que baseline.'),
 ('Forecast','Amenazas sobre escenario normal',None,'Implementado','Informe p.4,6,7; sensibilidad -10% declarada hipotética','No convertir lluvia o precio en pérdidas sin estimación válida.'),
 ('Entregables','Notebook, PBIX, PDF y fuentes',None,'Incluidos','Archivos en raíz, informe/ y datos/','Preparado para publicar; no publicado.'),
 ('Segunda rúbrica','Pauta distinta no aportada',None,'No verificable','Solo una rúbrica puntuada en los PDF recibidos','Si existe otra pauta, se necesita para auditarla.')]
pd.DataFrame(matrix,columns=['Referencia','Criterio','Puntos','Estado','Evidencia','Limite']).to_csv(ROOT/'MATRIZ_CUMPLIMIENTO.csv',index=False,encoding='utf-8-sig')
sources=[
 ('catastro.csv','ODEPA-CIREN','Catastro 2024','https://datos.odepa.gob.cl/dataset/ea82304e-917f-4cdb-abf6-555782483dc1/resource/e5d0481f-bd99-4e38-b86e-e1030b40997a/download/catastro_fruticola_2024.csv','Descargado 2026-10-03','Comuna / bloque'),
 ('exportaciones_temporada.xlsx','ODEPA','Boletín enero 2026','https://www.odepa.gob.cl/wp-content/uploads/2026/01/Exportaciones-por-temporada0126.xlsx','Descargado 2026-10-03','Nacional / temporadas completas 2016-17 a 2024-25'),
 ('exportaciones_anuales.xlsx','ODEPA','Boletín enero 2026, complemento conservado no usado en modelos','https://www.odepa.gob.cl/wp-content/uploads/2026/01/Exportaciones0126_v2.xlsx','Descargado 2026-10-03','Mensual 2024-2025; fuente auxiliar'),
 ('PUB_COMU_ACT_V2.txt','SII','Estadísticas empresas comuna actividad','https://www.sii.cl/sobre_el_sii/empresas/EMPRESAS.zip','Extraído del ZIP oficial existente; revisión 2026-10-03; descarga original desconocida','Comuna / actividad 2021-2024'),
 ('PUB_TRAM5_COMU.txt','SII','Estadísticas empresas comuna tamaño','https://www.sii.cl/sobre_el_sii/empresas/EMPRESAS.zip','Extraído del ZIP oficial existente; revisión 2026-10-03; descarga original desconocida','Comuna / tamaño 2005-2024'),
 ('INE_rama.xlsx','INE','Serie por rama de actividad, hoja LI','https://www.ine.gob.cl/estadisticas/sociales/mercado-laboral/ocupacion-y-desocupacion','Copia sin cambios de rama.xlsx del ZIP del usuario; revisión 2026-10-03; descarga original desconocida','Regional / trimestres móviles feb.2013-jul.2026')]
for year in range(2017,2026):sources.append((f'anuario-{year}.pdf','DMC',f'Anuario {year}',f'https://climatologia.meteochile.gob.cl/publicaciones/anuario/anuario-{year}.pdf','Descargado 2026-10-03' if year<2023 else 'Copia de fuente DMC disponible; verificación visual 2026-10-03','San Fernando Ex-Sendos y San Benito de Chimbarongo; JJA'))
sources.append(('DimComuna.csv','BCN / normativa territorial','Códigos territoriales de Colchagua','https://www.bcn.cl/leychile/navegar?i=220924','Consulta 2026-10-03; correspondencia de nombres y códigos','Diez comunas, CUT 06301 a 06310; referencia de la dimensión'))
pd.DataFrame(sources,columns=['Archivo','Institucion','Dataset','URL','Procedencia_fecha','Cobertura']).to_csv(ROOT/'FUENTES.csv',index=False,encoding='utf-8-sig')
dictionary=[]
for path in DATA.glob('*.csv'):
 df=pd.read_csv(path)
 for c in df:dictionary.append({'Tabla':path.stem,'Campo':c,'Tipo_CSV':str(df[c].dtype),'No_nulos':int(df[c].notna().sum()),'Filas':len(df),'Ejemplo':str(df[c].dropna().iloc[0]) if df[c].notna().any() else 'Faltante'})
pd.DataFrame(dictionary).to_csv(ROOT/'DICCIONARIO_DATOS.csv',index=False,encoding='utf-8-sig')
defensa='''# Defensa del proyecto

1. **¿Qué problema resuelven?** Ordenar dónde iniciar diagnósticos de continuidad productiva con recursos limitados. Resultado: dos comunas robustas y un tercer cupo condicionado. No resolvemos físicamente sequía, precios ni liquidez solo con BI.
2. **¿Por qué cambiaron la pregunta?** Ahorro versus consumo no respondía al encargo sobre shocks agrícolas y PYMEs. Se sustituyó por vulnerabilidad, dependencia, amenazas y decisiones.
3. **¿Por qué no solo sequía?** Se comparan menor lluvia, episodios intensos y mercado, más concentración y riego. Otras amenazas no se descartan; faltan datos comparables.
4. **¿Cómo prueban que los datos son reales?** Originales, URLs exactas, hash, página DMC, ETL y conciliaciones. Fechas de descarga desconocidas se reconocen.
5. **¿Son PYMEs las 2.832 empresas de la red?** No. Son empresas de todos los tamaños en actividades potencialmente relacionadas. Las 4.229 PYMEs corresponden a pequeñas y medianas de todos los sectores. No cruzamos tablas marginales para inventar una intersección.
6. **¿Por qué no dan nombres de empresas vulnerables?** No hay una red de clientes, márgenes ni daños por empresa. Se propone diagnóstico municipal antes de identificar beneficiarios.
7. **¿Por qué Chimbarongo y Placilla?** Exposición agrícola y dependencia altas; ambas entran al top 3 en cinco escenarios. Consultar tabla y pesos, no memorizar solo el orden.
8. **¿Los pesos son objetivos?** Son preferencias explícitas para priorizar. Se prueban alternativas. No son coeficientes causales ni una probabilidad de riesgo.
9. **¿Qué es el HHI?** Suma de cuotas de hectáreas por especie al cuadrado. Una sola especie da 1; diversidad reduce el índice. No mide diversificación del ingreso empresarial.
10. **¿Qué encontró el ML?** Dos perfiles, silhouette 0,379; estabilidad media alta pero retiro de una comuna puede cambiarlo. No hay etiquetas de pérdidas para validar riesgo supervisado. Se implementó Lloyd con NumPy, 50 inicios y semilla 802.
11. **¿Qué es el lag?** Invierno JJA del año t contra diciembre t-febrero t+1. Se evita correlacionar invierno con el empleo del mismo invierno cuando la hipótesis se refiere a cosecha posterior.
12. **¿La lluvia causó menos empleo?** No. En cambios interanuales, r de Chimbarongo es 0,085 y cambia de signo al retirar temporadas. Dos estaciones locales y empleo regional no prueban causalidad.
13. **¿Por qué eliminar meses entre train y test?** La ENE usa trimestres móviles: meses centrales adyacentes comparten meses reales. Se purgan dos meses centrales para impedir ese solapamiento entre los bloques.
14. **¿Por qué la regresión si el ingenuo gana en 2025?** La regla se fijó en selección 2024. No se usa la prueba para volver a elegir y llamarla independiente. El resultado advierte que el modelo es provisional; un nuevo despliegue requiere otro bloque de evaluación o una regla futura preregistrada.
15. **¿Qué significa la banda?** Intervalo predictivo empírico nominal; 5.000 simulaciones en bloques de tres y variación de coeficientes. No son límites seguros ni un intervalo para personas individuales. 12/12 en prueba no certifica la cobertura futura.
16. **¿Se suman los empleos del verano?** No. Se reporta promedio de tres trimestres móviles; no son trabajadores únicos. Tampoco se suman límites de intervalos.
17. **¿Qué falta?** Horas de frío, heladas, incendios, superficie inundada, daños, red proveedor-cliente y cruce tamaño-sector, además de datos del invierno 2026. No se rellenaron con datos inventados.
18. **¿Cómo usaron IA?** Auditoría, programación, extracción y redacción asistidas por ChatGPT/Codex. El equipo debe revisar datos y defender decisiones. Practicar la ejecución del notebook y el filtro de dos comunas en PBIX.
'''
(ROOT/'DEFENSA.md').write_text(defensa,encoding='utf-8')

# Notebook realmente ejecutado: se capturan stdout y resultados de las celdas.
cells=[];ns={'__name__':'notebook'};counter=0
def md(s):cells.append({'cell_type':'markdown','metadata':{},'source':s.splitlines(True)})
def code(s):
 global counter
 counter+=1;buff=io.StringIO()
 with contextlib.redirect_stdout(buff):exec(compile(s,'Colchagua_Resiliencia.ipynb','exec'),ns)
 cells.append({'cell_type':'code','execution_count':counter,'metadata':{},'source':s.splitlines(True),'outputs':[{'output_type':'stream','name':'stdout','text':buff.getvalue().splitlines(True)}] if buff.getvalue() else []})
md('# Colchagua: resiliencia agrícola y priorización\nNotebook reproducible, ejecutado el 03-10-2026. Leer README y ejecutar desde la carpeta del proyecto. Datos reales: ODEPA-CIREN, SII, DMC e INE. No hay identificación de empresas ni efectos causales demostrados.')
code("from pathlib import Path\nimport sys, json\nimport pandas as pd\nimport analisis as a\nprint('Proyecto:', a.ROOT.name)\nprint('Fuentes originales:', len(list(a.RAW.iterdir())))")
md('## 1. Problema abierto y ETL agrícola\nLa decisión es dónde iniciar diagnósticos de continuidad. Se comparan amenazas climáticas y comerciales antes de priorizar. Los CUT se mantienen como texto; la superficie se agrega sin eliminar registros que podrían ser bloques distintos.')
code("agro, n = a.cargar_agricultura()\nprint('Registros locales:', n)\nprint(agro.to_string(index=False))")
md('## 2. Empresas y PYMEs\nSe separan tablas por actividad y tamaño. Las PYMEs son pequeñas y medianas de todos los sectores; no se imputa la intersección tamaño-sector. Ventas suprimidas se conservan como nulos.')
code("empresas, anio = a.cargar_empresas()\nprint('Año de corte:', anio)\nprint(empresas.to_string(index=False))")
md('## 3. Amenazas y calidad\nClima: dos estaciones y JJA 2017-2025, con páginas fuente. Agosto 2023 de San Fernando está ausente. Mercado: valor unitario nacional de fruta fresca; no precio del productor. Se excluye temporada parcial 2025-26.')
code("clima=a.cargar_clima()\nmercado=a.cargar_mercado()\nprint(clima.to_string(index=False))\nprint(mercado[mercado.Producto=='Cereza'].to_string(index=False))")
md('## 4. Prioridad y ML\nÍndice min-max con pesos 35/25/20/20: dependencia, HHI, riego por gravedad y cuota cerezo. Pesos normativos, no probabilidad. K-means compara k=2..4 con silhouette y estabilidad al retirar una comuna.')
code("ranking, clusters = a.priorizar(agro,empresas,mercado)\nprint(ranking[['Comuna','Indice_prioridad','Puesto','Mejor_puesto','Peor_puesto','Top3_escenarios','Cluster']].to_string(index=False))\nprint(clusters)")
md('## 5. Forecast temporal\nSerie regional en personas, con mes central del trimestre móvil. Purga de dos meses centrales antes de validación 2024 y prueba 2025. Comparación contra ingenuo estacional. Bandas bootstrap en bloques; cobertura nominal, no garantizada.')
code("empleo=a.cargar_empleo()\npronostico, metricas, resumen=a.forecast(empleo)\nprint(metricas.to_string(index=False))\nprint(json.dumps(resumen,ensure_ascii=False,indent=2))\nprint(pronostico.to_string(index=False))")
md('## 6. Desfase, correlación y sensibilidad\nInvierno t contra promedio diciembre t-febrero t+1. Comparar niveles y cambio interanual; reportar n, Pearson, Spearman y sensibilidad. No se agrupan estaciones como observaciones económicas independientes.')
code("pares, correlaciones=a.desfase(clima,empleo)\nprint(correlaciones.to_string(index=False))")
md('## 7. Gráficos y conclusión\nSe priorizan Chimbarongo y Placilla de forma robusta. Palmilla depende de pesos. La asociación clima-empleo en cambios es inestable y no ajusta causalmente el forecast. La regresión elegida en 2024 pierde frente al ingenuo en 2025; la limitación se conserva.')
code("a.plots(ranking,clima,mercado,empleo,pronostico,pares)\nprint('Gráficos generados en informe/figuras. Revisar el PDF y el dashboard.')")
for name in ['prioridad','clima','mercado','lag','forecast']:
 b=base64.b64encode((OUT/'figuras'/f'{name}.png').read_bytes()).decode()
 cells.append({'cell_type':'markdown','metadata':{},'source':[f'![{name}](attachment:{name}.png)'],'attachments':{f'{name}.png':{'image/png':b}}})
md('## 8. Construcción completa y pruebas\nLa siguiente celda regenera el datamart y ejecuta controles de llave, cobertura, continuidad temporal y conciliación. No necesita Internet. El PBIX se actualiza por separado; ver README.')
code("a.main()")
md('## Declaración de IA\nChatGPT/Codex asistió auditoría, extracción, programación y redacción. El equipo debe comprender y defender decisiones. Los faltantes no se inventan; no se garantiza una nota ni causalidad.')
for i, cell in enumerate(cells): cell['id']=f'colchagua-{i:03d}'
(ROOT/'Colchagua_Resiliencia.ipynb').write_text(json.dumps({'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'}},'cells':cells},ensure_ascii=False,indent=1),encoding='utf-8')
manifest=[]
for path in sorted((ROOT/'datos/originales').glob('*')):
 manifest.append({'Archivo':str(path.relative_to(ROOT)).replace('\\','/'),'Bytes':path.stat().st_size,'SHA256':hashlib.sha256(path.read_bytes()).hexdigest()})
pd.DataFrame(manifest).to_csv(ROOT/'MANIFIESTO_SHA256.csv',index=False,encoding='utf-8-sig')
print('Informe PDF, documentación y notebook ejecutado generados.')

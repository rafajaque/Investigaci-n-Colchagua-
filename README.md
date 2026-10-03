# Colchagua: resiliencia agrícola y priorización de apoyo

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
# Windows: .venv\Scripts\activate
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

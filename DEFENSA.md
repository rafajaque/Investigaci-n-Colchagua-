# Defensa del proyecto

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

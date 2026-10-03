let
    Binario = if RutaDatos = "" then Binary.FromText("77u/ayxTaWxob3VldHRlDQoyLDAuMzc5MzU2ODY3NTAzNDg1NjMNCjMsMC4yNzc0OTgwODkyMzU4Njg4DQo0LDAuMjI5MjIxMTI5NzU1NDgwNTYNCg==", BinaryEncoding.Base64) else File.Contents(RutaDatos & "\Evaluacion_clusters.csv"),
    Csv = Csv.Document(Binario,[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Encabezados = Table.PromoteHeaders(Csv,[PromoteAllScalars=true]),
    Tipos = Table.TransformColumnTypes(Encabezados, {{"k", Int64.Type}, {"Silhouette", type number}}, "en-US")
in Tipos
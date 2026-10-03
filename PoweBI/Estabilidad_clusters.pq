let
    Binario = if RutaDatos = "" then Binary.FromText("77u/Q29tdW5hX3JldGlyYWRhLEFSSQ0KQ2hpbWJhcm9uZ28sMS4wDQpDaMOpcGljYSwxLjANCkxvbG9sLDEuMA0KTmFuY2FndWEsMS4wDQpQYWxtaWxsYSwxLjANClBlcmFsaWxsbywxLjANClBsYWNpbGxhLDEuMA0KUHVtYW5xdWUsMS4wDQpTYW4gRmVybmFuZG8sMC40OTI5NTc3NDY0Nzg4NzMyNQ0KU2FudGEgQ3J1eiwxLjANCg==", BinaryEncoding.Base64) else File.Contents(RutaDatos & "\Estabilidad_clusters.csv"),
    Csv = Csv.Document(Binario,[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Encabezados = Table.PromoteHeaders(Csv,[PromoteAllScalars=true]),
    Tipos = Table.TransformColumnTypes(Encabezados, {{"Comuna_retirada", type text}, {"ARI", type number}}, "en-US")
in Tipos
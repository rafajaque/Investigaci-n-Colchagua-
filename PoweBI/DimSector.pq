let
    Binario = if RutaDatos = "" then Binary.FromText("77u/U2VjdG9yDQpDb21lcmNpbyBhZ3JvYWxpbWVudGFyaW8gcG90ZW5jaWFsDQpPdHJvcyBzZWN0b3Jlcw0KUHJvY2VzYW1pZW50byBmcnV0YXMgeSBob3J0YWxpemFzDQpQcm9kdWNjacOzbiBhZ3JvcGVjdWFyaWENClNlcnZpY2lvcyBhZ3LDrWNvbGFzDQpUcmFuc3BvcnRlIHkgYWxtYWNlbmFtaWVudG8gcG90ZW5jaWFsDQo=", BinaryEncoding.Base64) else File.Contents(RutaDatos & "\DimSector.csv"),
    Csv = Csv.Document(Binario,[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Encabezados = Table.PromoteHeaders(Csv,[PromoteAllScalars=true]),
    Tipos = Table.TransformColumnTypes(Encabezados, {{"Sector", type text}}, "en-US")
in Tipos
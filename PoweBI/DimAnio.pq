let
    Binario = if RutaDatos = "" then Binary.FromText("77u/QW5pbw0KMjAwNQ0KMjAwNg0KMjAwNw0KMjAwOA0KMjAwOQ0KMjAxMA0KMjAxMQ0KMjAxMg0KMjAxMw0KMjAxNA0KMjAxNQ0KMjAxNg0KMjAxNw0KMjAxOA0KMjAxOQ0KMjAyMA0KMjAyMQ0KMjAyMg0KMjAyMw0KMjAyNA0KMjAyNQ0KMjAyNg0KMjAyNw0K", BinaryEncoding.Base64) else File.Contents(RutaDatos & "\DimAnio.csv"),
    Csv = Csv.Document(Binario,[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Encabezados = Table.PromoteHeaders(Csv,[PromoteAllScalars=true]),
    Tipos = Table.TransformColumnTypes(Encabezados, {{"Anio", Int64.Type}}, "en-US")
in Tipos
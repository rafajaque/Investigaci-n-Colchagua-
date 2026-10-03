param([Parameter(Mandatory=$true)][int]$Port,[Parameter(Mandatory=$true)][string]$DllDirectory,[switch]$ReemplazarCopiaOriginal)
# Ejecutar SOLO sobre un informe vacío o una copia de Colchagua_Resiliencia.
$ErrorActionPreference='Stop'
[Reflection.Assembly]::LoadFrom((Join-Path $DllDirectory 'Microsoft.AnalysisServices.Server.Core.dll'))|Out-Null
[Reflection.Assembly]::LoadFrom((Join-Path $DllDirectory 'Microsoft.AnalysisServices.Server.Tabular.dll'))|Out-Null
$config=Get-Content (Join-Path $PSScriptRoot 'modelo.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$server=[Microsoft.AnalysisServices.Tabular.Server]::new();$server.Connect("Data Source=localhost:$Port")
$db=$server.Databases[0]
if($db.Model.Tables.Count -gt 1 -and -not $db.Model.Tables.Contains('FactPrioridad') -and -not ($ReemplazarCopiaOriginal -and $db.Model.Tables.Contains('FactMensual'))){throw 'No es el informe esperado. No se modificó.'}
$db.Model.Relationships.Clear();$db.Model.Tables.Clear();$db.Model.Expressions.Clear()
$param=[Microsoft.AnalysisServices.Tabular.NamedExpression]::new();$param.Name='RutaDatos';$param.Kind='M'
$param.Expression='"" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=false]'
$db.Model.Expressions.Add($param)
foreach($spec in $config.tables){
 $t=[Microsoft.AnalysisServices.Tabular.Table]::new();$t.Name=$spec.name
 $t.Description='Datamart ISI802. Origen reproducible CSV. RutaDatos vacía utiliza copia integrada portable.'
 $p=[Microsoft.AnalysisServices.Tabular.Partition]::new();$p.Name=$spec.name;$p.Mode='Import'
 $p.Source=[Microsoft.AnalysisServices.Tabular.MPartitionSource]::new();$p.Source.Expression=$spec.m;$t.Partitions.Add($p)
 foreach($cs in $spec.columns){$c=[Microsoft.AnalysisServices.Tabular.DataColumn]::new();$c.Name=$cs.name;$c.SourceColumn=$cs.name;$c.DataType=$cs.dataType
  if($cs.format){$c.FormatString=$cs.format};$c.SummarizeBy='None';$t.Columns.Add($c)}
 $db.Model.Tables.Add($t)
}
foreach($rs in $config.relationships){
 $r=[Microsoft.AnalysisServices.Tabular.SingleColumnRelationship]::new();$r.Name="$($rs.dim)_$($rs.fact)_$($rs.column)"
 $r.FromColumn=$db.Model.Tables[$rs.fact].Columns[$rs.column];$r.ToColumn=$db.Model.Tables[$rs.dim].Columns[$rs.dimColumn]
 $r.FromCardinality='Many';$r.ToCardinality='One';$r.CrossFilteringBehavior='OneDirection';$r.IsActive=$true
 $db.Model.Relationships.Add($r)
}
foreach($ms in $config.measures){$m=[Microsoft.AnalysisServices.Tabular.Measure]::new();$m.Name=$ms.name;$m.Expression=$ms.expression;$m.FormatString=$ms.format;$db.Model.Tables[$ms.table].Measures.Add($m)}
$db.Model.SaveChanges()|Out-Null
$db.Model.RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full);$db.Model.SaveChanges()|Out-Null
Write-Output "Cargadas $($db.Model.Tables.Count) tablas, $($db.Model.Relationships.Count) relaciones. Guardar PBIX en Desktop."
$server.Disconnect()

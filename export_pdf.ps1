param(
    [string]$DocxPath,
    [string]$PdfPath
)

$Word = New-Object -ComObject Word.Application
$Word.Visible = $false
try {
    $Doc = $Word.Documents.Open($DocxPath)
    $Doc.SaveAs([ref]$PdfPath, [ref]17)
    $Doc.Close([ref]$false)
    Write-Host "PDF Exported: $PdfPath"
} catch {
    Write-Error $_.Exception.Message
} finally {
    $Word.Quit([ref]$false)
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($Word) | Out-Null
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}

[CmdletBinding()]
param(
    [int]$MaxSecondsPerFolder = 8,
    [int]$MaxSecondsForFileTypes = 60
)

# Read-only Windows C drive inspection helper.
# This script only reads metadata and prints summary tables. It never deletes,
# moves, renames, writes, or changes files.

$ErrorActionPreference = "SilentlyContinue"

function Convert-ToGB {
    param([Nullable[double]]$Bytes)
    if ($null -eq $Bytes) { return 0 }
    return [math]::Round(($Bytes / 1GB), 2)
}

function Get-FolderSize {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }

    $fileCount = 0
    $totalBytes = 0
    $partial = $false
    $watch = [System.Diagnostics.Stopwatch]::StartNew()
    $stack = [System.Collections.Generic.Stack[string]]::new()
    $stack.Push($Path)

    while ($stack.Count -gt 0) {
        if ($watch.Elapsed.TotalSeconds -ge $MaxSecondsPerFolder) {
            $partial = $true
            break
        }

        $currentPath = $stack.Pop()

        try {
            $directory = [System.IO.DirectoryInfo]::new($currentPath)

            foreach ($file in $directory.EnumerateFiles()) {
                $fileCount += 1
                $totalBytes += $file.Length
            }

            foreach ($childDirectory in $directory.EnumerateDirectories()) {
                if (($childDirectory.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -eq 0) {
                    $stack.Push($childDirectory.FullName)
                }
            }
        }
        catch {
            continue
        }
    }

    [pscustomobject]@{
        Path    = $Path
        Files   = $fileCount
        GB      = Convert-ToGB $totalBytes
        Partial = $partial
    }
}

function Get-DriveSummary {
    $drive = Get-PSDrive -Name C
    [pscustomobject]@{
        Drive   = "C:"
        UsedGB  = Convert-ToGB $drive.Used
        FreeGB  = Convert-ToGB $drive.Free
        TotalGB = Convert-ToGB ($drive.Used + $drive.Free)
    }
}

function Get-ExistingFolderSummaries {
    $userProfile = $env:USERPROFILE
    $paths = @(
        "C:\Windows",
        "C:\Program Files",
        "C:\Program Files (x86)",
        "C:\ProgramData",
        (Join-Path $userProfile "Desktop"),
        (Join-Path $userProfile "Documents"),
        (Join-Path $userProfile "Downloads"),
        (Join-Path $userProfile "Pictures"),
        (Join-Path $userProfile "Videos"),
        (Join-Path $userProfile "Music"),
        "C:\Autodesk",
        "C:\Drivers",
        "C:\Temp",
        "C:\Intel",
        "C:\CloudMusic",
        "C:\AITEMP",
        "C:\FFOutput",
        "C:\common_attachment",
        "C:\backup",
        "C:\Apps"
    )

    foreach ($path in ($paths | Select-Object -Unique)) {
        $summary = Get-FolderSize -Path $path
        if ($null -ne $summary) {
            $summary
        }
    }
}

function Get-UserFileTypeSummary {
    $extensions = @(
        ".doc", ".docx", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".csv",
        ".zip", ".rar", ".7z",
        ".jpg", ".jpeg", ".png",
        ".mp4", ".mov", ".mp3", ".wav"
    )

    $stats = @{}
    $watch = [System.Diagnostics.Stopwatch]::StartNew()
    $partial = $false
    $stack = [System.Collections.Generic.Stack[string]]::new()
    $stack.Push($env:USERPROFILE)

    while ($stack.Count -gt 0) {
        if ($watch.Elapsed.TotalSeconds -ge $MaxSecondsForFileTypes) {
            $partial = $true
            break
        }

        $currentPath = $stack.Pop()

        try {
            $directory = [System.IO.DirectoryInfo]::new($currentPath)

            foreach ($file in $directory.EnumerateFiles()) {
                $extension = $file.Extension.ToLowerInvariant()
                if ($extensions -contains $extension) {
                    if (-not $stats.ContainsKey($extension)) {
                        $stats[$extension] = [pscustomobject]@{
                            Extension = $extension
                            Count     = 0
                            Bytes     = 0
                        }
                    }

                    $stats[$extension].Count += 1
                    $stats[$extension].Bytes += $file.Length
                }
            }

            foreach ($childDirectory in $directory.EnumerateDirectories()) {
                if (($childDirectory.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -eq 0) {
                    $stack.Push($childDirectory.FullName)
                }
            }
        }
        catch {
            continue
        }
    }

    $stats.Values |
        ForEach-Object {
            [pscustomobject]@{
                Extension = $_.Extension
                Count     = $_.Count
                GB        = Convert-ToGB $_.Bytes
                Partial   = $partial
            }
        } |
        Sort-Object GB -Descending
}

Write-Host ""
Write-Host "=== C drive summary ==="
Get-DriveSummary | Format-Table -AutoSize

Write-Host ""
Write-Host "=== Folder size summary ==="
Get-ExistingFolderSummaries | Sort-Object GB -Descending | Format-Table -AutoSize

Write-Host ""
Write-Host "=== User file type summary ==="
Get-UserFileTypeSummary | Format-Table -AutoSize

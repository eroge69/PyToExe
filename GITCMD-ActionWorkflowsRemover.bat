@echo off

REM Set repositori
set REPO=eroge69/PyToExe

REM Login ke GitHub CLI (jika belum login)
echo TOKEN_CODE_HERE | gh auth login --with-token	

REM Ambil nama workflow yang ada di repositori
for /f "delims=" %%I in ('gh workflow list --repo %REPO% --json name -q ".[].name"') do (
    REM Menampilkan nama workflow yang ditemukan
    echo Found workflow: %%I
    
    REM Mengambil ID dari workflow dan menghapus semua workflow run-nya
    for /f "delims=" %%J in ('gh run list --repo %REPO% --workflow "%%I" --json databaseId -q ".[].databaseId" --limit 100') do (
        echo Deleting workflow run ID %%J
        gh api -X DELETE "/repos/%REPO%/actions/runs/%%J"
    )
)

echo All workflow runs deleted.

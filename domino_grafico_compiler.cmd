@echo off
REM ===============================
REM Script para compilar con Nuitka
REM ===============================

echo.
echo ==================
echo Limpiando Cache...
echo ==================
echo.
REM Limpiar carpeta dist si existe
if exist dist (
    echo Limpiando carpeta dist...
    rmdir /s /q dist
    echo.
)
echo.

echo =============================
echo Renombrando constantes_exe.py
echo =============================
ren constantes.py constantes_vsc.py
ren constantes_exe.py constantes.py
echo.

echo ========================
echo Compilando con Nuitka...
echo ========================
REM Compilar con Nuitka
python -m nuitka ^
    --standalone ^
    --onefile ^
    --windows-console-mode=disable ^
    --enable-plugin=tk-inter ^
    --include-data-dir=imagenes=imagenes ^
    --windows-icon-from-ico=imagenes/icono.ico ^
    --output-dir=dist ^
    --output-filename=domino.exe ^
    --assume-yes-for-downloads ^
    domino_grafico.py
echo.

if %ERRORLEVEL% EQU 0 (
    echo ====================
    echo Compilado con exito!
    echo ====================
    echo.
    echo El ejecutable esta en: dist\domino.exe
    echo.
    dir dist\domino.exe
) else (
    echo =======================
    echo Error en la compilacion
    echo =======================
)
echo.

echo =========================
echo Renombrando constantes.py
echo =========================
ren constantes.py constantes_exe.py
ren constantes_vsc.py constantes.py
echo.
pause

@echo off
set DOCKER="C:\Program Files\Docker\Docker\resources\bin\docker.exe"

echo ================================================
echo E-Commerce RAG - Quickstart
echo ================================================
echo.

echo [1] Starting Docker services...
echo NOTE: Use 'docker compose down -v' to clear data and force re-ingest
%DOCKER% compose -f "C:\Users\vpkam\Desktop\yes\docker-compose.yml" up -d
echo.

echo [2] Waiting for services to be ready...
timeout /t 10 /nobreak >nul
echo.

echo [3] Testing backend health...
curl -s http://localhost:8000/health
echo.
echo.

echo [4] Running ingest (loading 280 products - takes ~30-40 seconds)...
echo Waiting for ingest to complete...

:INGEST_WAIT
curl -s -X POST http://localhost:8000/ingest > %TEMP%\ingest_result.txt 2>nul
findstr /C:"success" %TEMP%\ingest_result.txt >nul 2>&1
if errorlevel 1 (
    echo Retrying...
    timeout /t 3 /nobreak >nul
    goto INGEST_WAIT
)

type %TEMP%\ingest_result.txt
echo.
echo Ingest complete. Waiting for index to initialize...
timeout /t 3 /nobreak >nul
echo.

echo [5] Verifying search works...
curl -s "http://localhost:8000/search?q=phone&top_k=3" > %TEMP%\search_result.txt
findstr /C:"products" %TEMP%\search_result.txt >nul 2>&1
if errorlevel 1 (
    echo WARNING: Search returned empty. Retrying...
    timeout /t 3 /nobreak >nul
    curl -s "http://localhost:8000/search?q=phone&top_k=3" > %TEMP%\search_result.txt
)
type %TEMP%\search_result.txt
echo.
echo.

echo [6] Graph stats...
curl -s http://localhost:8000/graph/stats
echo.
echo.

echo [7] Recommendations test...
curl -s "http://localhost:8000/recommendations/P001?limit=3"
echo.
echo.

echo [8] Frontend test...
curl -s http://localhost:3000 | findstr "E-Commerce RAG"
echo.
echo.

echo ================================================
echo System Ready!
echo.
echo Access Points:
echo   Frontend:   http://localhost:3000
echo   Backend:    http://localhost:8000
echo   Neo4j:      http://localhost:7474 (neo4j/password)
echo.
echo API Docs:    http://localhost:8000/docs
echo.
echo ================================================
echo Quickstart Complete!
echo.
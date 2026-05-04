@echo off
set DOCKER="C:\Program Files\Docker\Docker\resources\bin\docker.exe"

echo ================================================
echo E-Commerce RAG - Quickstart
echo ================================================
echo.

echo [1] Starting Docker services...
%DOCKER% compose -f "C:\Users\vpkam\Desktop\yes\docker-compose.yml" up -d
echo.

echo [2] Waiting for services to be ready...
timeout /t 10 /nobreak >nul
echo.

echo [3] Testing backend health...
curl -s http://localhost:8000/health
echo.
echo.

echo [4] Running ingest (loading 280 products)...
curl -s -X POST http://localhost:8000/ingest
echo.
echo.

echo [5] Testing search (phones)...
curl -s "http://localhost:8000/search?q=phone&top_k=3"
echo.
echo.

echo [6] Testing graph stats...
curl -s http://localhost:8000/graph/stats
echo.
echo.

echo [7] Testing recommendations...
curl -s "http://localhost:8000/recommendations/P001?limit=3"
echo.
echo.

echo [8] Testing frontend...
curl -s http://localhost:3000 | findstr "E-Commerce RAG"
echo.
echo.

echo ================================================
echo System Ready!
echo ================================================
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
echo ================================================
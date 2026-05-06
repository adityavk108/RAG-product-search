@echo off
REM ================================================================================
REM E-Commerce RAG - Full Rebuild Script
REM ================================================================================
REM This script:
REM   1. Stops all containers
REM   2. Removes ALL containers, volumes, networks, and images
REM   3. Prunes Docker system
REM   4. Rebuilds images from scratch
REM   5. Starts services
REM ================================================================================
REM BEFORE RUNNING:
REM   - Ensure you have backed up any important data
REM   - This will delete ALL Docker data (not just this project's)
REM ================================================================================

set DOCKER="C:\Program Files\Docker\Docker\resources\bin\docker.exe"

echo ================================================
echo E-Commerce RAG - Full Rebuild
echo ================================================
echo WARNING: This will remove ALL Docker data
echo Press Ctrl+C to cancel, or Enter to continue...
echo.

pause

echo [1] Stopping all containers...
%DOCKER% compose down

echo [2] Removing containers, volumes, and networks...
%DOCKER% compose down -v

echo [3] Removing all project images...
%DOCKER% rmi yes-backend yes-frontend yes-neo4j

echo [4] Pruning Docker system (this may take a while)...
%DOCKER% system prune -a --volumes -f

echo [5] Building images (this will take several minutes)...
%DOCKER% compose build --no-cache

echo [6] Starting services...
%DOCKER% compose up -d

echo [7] Waiting for Neo4j to be ready...
timeout /t 15 /nobreak >nul

echo [8] Running ingest...
curl -s -X POST http://localhost:8000/ingest

echo Waiting 35 seconds for embeddings to be generated...
timeout /t 35 /nobreak >nul

echo.
echo ================================================
echo Rebuild Complete!
echo ================================================
echo.
echo Access Points:
echo   Frontend:   http://localhost:3000
echo   Backend:    http://localhost:8000
echo   Neo4j:      http://localhost:7474 (neo4j/password)
echo.
echo ================================================

pause
@echo off
setlocal enabledelayedexpansion

REM 部署脚本 - Time Series Analyzer API (Windows)

set IMAGE_NAME=time-series-analyzer
set CONTAINER_NAME=time-series-analyzer-api
set PORT=8000

if "%1"=="" goto :help
if "%1"=="help" goto :help
if "%1"=="build" goto :build
if "%1"=="run" goto :run
if "%1"=="stop" goto :stop
if "%1"=="restart" goto :restart
if "%1"=="logs" goto :logs
if "%1"=="clean" goto :clean
goto :help

:help
echo Usage: %0 [OPTION]
echo Deploy Time Series Analyzer API
echo.
echo Options:
echo   build     Build Docker image
echo   run       Run container
echo   stop      Stop container
echo   restart   Restart container
echo   logs      Show container logs
echo   clean     Remove container and image
echo   help      Show this help
goto :end

:build
echo [INFO] Building Docker image...
docker build -t %IMAGE_NAME% .
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to build image
    goto :end
)
echo [INFO] Image built successfully!
goto :end

:run
echo [INFO] Stopping existing container if running...
docker stop %CONTAINER_NAME% >nul 2>&1
docker rm %CONTAINER_NAME% >nul 2>&1

echo [INFO] Starting new container...
docker run -d --name %CONTAINER_NAME% -p %PORT%:8000 --restart unless-stopped %IMAGE_NAME%
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to start container
    goto :end
)

echo [INFO] Container started successfully!
echo [INFO] API is available at: http://localhost:%PORT%
echo [INFO] API documentation: http://localhost:%PORT%/docs
goto :end

:stop
echo [INFO] Stopping container...
docker stop %CONTAINER_NAME%
echo [INFO] Container stopped!
goto :end

:restart
echo [INFO] Stopping container...
docker stop %CONTAINER_NAME%
echo [INFO] Starting container...
docker start %CONTAINER_NAME%
echo [INFO] Container restarted!
goto :end

:logs
echo [INFO] Showing container logs...
docker logs -f %CONTAINER_NAME%
goto :end

:clean
set /p confirm="This will remove the container and image. Continue? (y/N): "
if /i "!confirm!"=="y" (
    echo [INFO] Stopping and removing container...
    docker stop %CONTAINER_NAME% >nul 2>&1
    docker rm %CONTAINER_NAME% >nul 2>&1
    
    echo [INFO] Removing image...
    docker rmi %IMAGE_NAME% >nul 2>&1
    
    echo [INFO] Cleanup completed!
) else (
    echo [INFO] Cleanup cancelled.
)
goto :end

:end
endlocal

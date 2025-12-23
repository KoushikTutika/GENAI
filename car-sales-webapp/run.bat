@echo off
cd /d "%~dp0"
if exist "%JAVA_HOME%\bin\java.exe" (
    "%JAVA_HOME%\bin\java.exe" -cp "src/main/java;lib/*" com.tata.CarSalesApplication
) else (
    java -cp "src/main/java;lib/*" com.tata.CarSalesApplication
)
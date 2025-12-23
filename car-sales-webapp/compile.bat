@echo off
cd /d "%~dp0"
if exist "%JAVA_HOME%\bin\javac.exe" (
    "%JAVA_HOME%\bin\javac.exe" -d bin -cp "lib/*" src/main/java/com/tata/CarSalesApplication.java
) else (
    javac -d bin -cp "lib/*" src/main/java/com/tata/CarSalesApplication.java
)
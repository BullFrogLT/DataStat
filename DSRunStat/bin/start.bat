@echo off

set "CURRENT_DIR=%cd%"

set "JAVA_HOME=%JAVA_HOME%"

set "java=%JAVA_HOME%\bin\java.exe"

cd %CURRENT_DIR%\..\

"%java%" -jar bin\DSRunStat-1.0.3.jar ins  2016-12-01 00:00:00 2016-12-02 00:00:00

cd %CURRENT_DIR%


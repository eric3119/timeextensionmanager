cd %HOMEPATH%
mkdir timeextensionmanager
del /q timeextensionmanager\*
cd timeextensionmanager
curl https://codeload.github.com/eric3119/timeextensionmanager/tar.gz/main -o timeextensionmanager.tar.gz
tar -xvf timeextensionmanager.tar.gz

:: create scheduled task run on logon
schtasks /create /tn "TimeExtensionManager" /tr "%HOMEPATH%\timeextensionmanager\timeextensionmanager-main\run-command check \"%*\"" /sc onlogon /ru "%*" /F

:: create scheduled task run every 60 minutes replace the old one
schtasks /create /tn "TimeExtensionManager60min" /tr "%HOMEPATH%\timeextensionmanager\timeextensionmanager-main\run-command fetch \"%*\"" /sc minute /mo 60 /ru "%*" /F

"%HOMEPATH%\timeextensionmanager\timeextensionmanager-main\run-command check \"%*\""
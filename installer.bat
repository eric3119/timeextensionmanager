cd %HOMEPATH%
mkdir timeextensionmanager
del /q timeextensionmanager\*
cd timeextensionmanager
curl https://codeload.github.com/eric3119/timeextensionmanager/tar.gz/main -o timeextensionmanager.tar.gz
tar -xvf timeextensionmanager.tar.gz

:: create scheduled task run on logon
schtasks /create /tn "TimeExtensionManager" /tr "cd %HOMEPATH%\timeextensionmanager\timeextensionmanager-main\bundle && python timeextension_check.py check" /sc onlogon /ru %USERNAME% /F

:: create scheduled task run every 60 minutes replace the old one
schtasks /create /tn "TimeExtensionManager60min" /tr "cd %HOMEPATH%\timeextensionmanager\timeextensionmanager-main\bundle && python timeextension_check.py fetch" /sc minute /mo 60 /ru %USERNAME% /F

cd timeextensionmanager\bundle && python timeextension_check.py check
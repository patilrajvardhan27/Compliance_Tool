echo OFF
set doedir=%5
::..\..\doe22\exent
goto :checkinp

:nogood
echo *ERROR: First parameter MUST specify an available version to run 

:nogood1
echo *
echo *      Correct useage of command as follows:
echo *       
echo *run22 input weather 
echo *       
echo *              input is the name of the BDL input file WITHOUT the required
echo *                    .inp extension
echo *       
echo *              weather is the packed DOE-2 weather file WITHOUT the 
echo *                    required .bin extension; these files must be located
echo *                    in the \doe22\weather directory
echo *       
goto :end

:checkinp
if exist %1\%2.inp goto :checkwth
echo *ERROR: Input file (%2.inp) does not exist.
echo *       Input files to use include (leave off .inp extension):
goto :nogood1

:checkwth
if exist %3\%4.bin goto :start
echo *ERROR: Weather file (%4) not in library.
echo *       Weather files to use include (leave off .bin extension):
goto :nogood1

:start
echo ===== doe2.2: input file : %1\%2,  weather : %3\%4
echo ===== DOE-2.2 version: %doedir% =====
mkdir  %1\%2.tmp 
cd %1\%2.tmp

copy  %1\%2.inp INPUT2.TMP
copy  %doedir%\BDLKEY.BIN     BDLKEY.BIN >nul
copy  %doedir%\BDLLIB.dat     BDLLIB.dat >nul
copy  %doedir%\BDLDFT.dat     BDLDFT.dat >nul
copy  %doedir%\USRLIB.dat     USRLIB.dat >nul

%doedir%\doebdl

del BDLKEY.BIN >nul
del BDLLIB.dat >nul
del BDLDFT.dat >nul
del INPUT2.TMP >nul
copy DOEBDL.OUT ..\%2.BDL >nul

if errorlevel 1 goto :error

copy  %3\%4.bin  WEATHER.BIN >nul
copy  %doedir%\HDRFIL.BIN  HDRFIL.BIN >nul
copy  %doedir%\TDVCTZ.BIN  TDVCTZ.BIN >nul
%doedir%\doesim

copy DOESIM.OUT ..\%2.SIM >nul

:error
:: copy  DOEBDL.LOG + DOESIM.LOG ..\%2.log >nul
del *.dat >nul
del *.bin >nul
del *.tmp >nul
del DOE*.* >nul

:: del *.out >nul
:: del for??? >nul
del for??? >nul

cd ..
rmdir %2.tmp >nul

echo ===== doe22 %1.inp %2.bin completed =====

:end
echo ON

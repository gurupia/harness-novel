@echo off
chcp 65001 > nul
echo ==================================================
echo [Setup] 하네스 에이전트 가상환경 구축을 시작합니다.
echo ==================================================

echo [1/3] 파이썬 가상환경(venv)을 생성하고 있습니다...
python -m venv venv
if %errorlevel% neq 0 (
    echo [Error] 파이썬 가상환경 생성 실패. Python이 설치되어 있는지 확인하십시오.
    pause
    exit /b %errorlevel%
)

echo [2/3] 가상환경 활성화 및 의존성 라이브러리 설치를 진행합니다...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [Error] 가상환경 활성화에 실패했습니다.
    pause
    exit /b %errorlevel%
)

echo [3/3] pip 라이브러리 순차 설치 중...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [Error] requirements.txt 패키지 설치 중 에러가 발생했습니다.
    pause
    exit /b %errorlevel%
)

echo ==================================================
echo [Complete] 모든 가상환경 세팅이 성공적으로 완료되었습니다!
echo ==================================================
pause

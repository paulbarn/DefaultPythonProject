REM upgrade pip & install wheel
python -m pip install --upgrade pip
pip install wheel
pip list

REM install application packages
pip install -r requirements.txt
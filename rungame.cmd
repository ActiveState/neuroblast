@ECHO OFF
IF EXIST data GOTO DATAEXIST
mkdir data
cd data
mkdir db
cd ..
:DATAEXIST
START "Mongo" "C:\Program Files\MongoDB\Server\3.4\bin\mongod" -dbpath data\db
python game.py -f -t
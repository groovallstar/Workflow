# !bin/bash

SCRIPT=$PYTHONPATH/make_data/insert_table.py

python $SCRIPT --data='{"database": "test", "collection": "iris.data", "start_date": "202501", "end_date": "202501"}' \
--table='{"database": "test", "collection": "iris.table"}'
python $SCRIPT --data='{"database": "test", "collection": "digits.data", "start_date": "202501", "end_date": "202501"}' \
--table='{"database": "test", "collection": "digits.table"}'
python $SCRIPT --data='{"database": "test", "collection": "wine.data", "start_date": "202501", "end_date": "202501"}' \
--table='{"database": "test", "collection": "wine.table"}'
python $SCRIPT --data='{"database": "test", "collection": "breast_cancer.data", "start_date": "202501", "end_date": "202501"}' \
--table='{"database": "test", "collection": "breast_cancer.table"}'

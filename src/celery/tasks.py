import os
import json
import subprocess

from celery import Celery
import redis

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
REDIS_HOST_IP = os.environ.get('REDIS_HOST_IP')

celery = Celery(
    'tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

strict_redis = redis.StrictRedis(
    host=REDIS_HOST_IP, port=6379, charset="utf-8", decode_responses=True)


def make_pipeline_parameters(append_string: list, **kwargs) -> None:
    """파이프라인 파라미터 생성.

    Args:
        append_string (list): python script 실행 파라미터 list
        kwargs: 입력한 설정 값
    """
    for key in kwargs:
        combine_string = ""
        # input으로 이뤄진 column들은 각 값을 json string으로 만들어야 함.
        if isinstance(kwargs[key], dict) is True:
            combine_string = f'--{key}={json.dumps(kwargs[key])}'
        elif ((isinstance(kwargs[key], bool) is True) and (kwargs[key] is True)):
            # checkbox는 체크한 값만 파라미터로 추가함.
            combine_string = f'--{key}'
        else:
            # 1개의 input은 값이 있을 경우만 파라미터로 추가함.
            if kwargs[key]:
                combine_string = f'--{key}={kwargs[key]}'

        if combine_string != "":
            append_string.append(combine_string)

def run_subprocess(script_name: str, kwargs) -> True:
    """python script를 subprocess를 이용하여 실행.

    Args:
        script_name (str): 스크립트 파일명.
        kwargs (**args): 웹 설정 dictionary.
    """
    if os.path.exists(script_name) is False:
        print('script file not Found.', script_name)
        return False

    append_string = []
    append_string.append('python')
    append_string.append(script_name)
    make_pipeline_parameters(append_string, **kwargs)

    proc = subprocess.Popen(append_string)
    (stdoutdata, stderrdata) = proc.communicate()
    #print(stdoutdata, stderrdata)
    return True

@celery.task(name='tasks.insertdata', bind=True, ignore_result=True)
def task_insert_data(self, **kwargs) -> None:
    """insert data 페이지 task 에 대한 celery 작업"""
    insert_data_script = os.path.join(
        os.environ.get('PYTHONPATH'), 'make_data/insert_data.py')
    run_subprocess(insert_data_script, kwargs=kwargs)

    strict_redis.publish(
        'background',
        json.dumps(['flask-event', self.request.id]))

@celery.task(name='tasks.inserttable', bind=True, ignore_result=True)
def task_insert_table(self, **kwargs) -> None:
    """insert table 페이지 task 에 대한 celery 작업."""
    insert_table_script = os.path.join(
        os.environ.get('PYTHONPATH'), 'make_data/insert_table.py')
    run_subprocess(insert_table_script, kwargs=kwargs)

    strict_redis.publish(
        'background',
        json.dumps(['flask-event', self.request.id]))

@celery.task(name='tasks.pipeline', bind=True, ignore_result=True)
def task_pipeline(self, **kwargs) -> None:
    """train/predict 페이지 task 에 대한 celery 작업.
    """
    pipeline_script = os.path.join(
        os.environ.get('PYTHONPATH'), 'learning/pipeline_mlflow.py')
    run_subprocess(pipeline_script, kwargs=kwargs)

    strict_redis.publish(
        'background',
        json.dumps(['flask-event', self.request.id]))

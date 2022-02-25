from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.filesystem import FileSensor
from airflow.models.baseoperator import chain, cross_downstream
from datetime import datetime, timedelta


# profile parameter (ทุก task จะ default parameter นี้ หากไม่ override)
default_args={
    'retry': 5,
    'retry_delay': timedelta(minutes=1),
    'email_on_retry': True,
    'email_on_failure': True,
    # you have to configure smtp server in order to send email from airflow instance
    'email':'admin@astro.io'
}

def _downloading_data(ti):
    print('just a test')
# How to ref to all of context of that dag or specific value eg. execution_date(ds)
# def _downloading_data(**kwargs):
#     print(kwargs) @all value
# def _downloading_data(ds):
#     print(ds) @only execution_date

# How to pass my own parameter into python fucntion
# def _downloading_data(my_param, ds):
#     print(my_param) @->42

# Create file at /tmp/my_file.txt
    with open('/tmp/my_file.txt', 'w') as f:
        f.write('my_data')

# XCOM data
    ti.xcom_push(key='my_key', value=43)

# read XCOM data
def _checking_data(ti):
    my_xcom = ti.xcom_pull(key='my_key', task_ids=['downloading_data'])
    print(my_xcom)

def _failure(context):
    print("On callback failure")
    print(context)

with DAG(dag_id='simple_dag', schedule_interval=timedelta(hours=4), start_date=datetime(2022, 2, 9)) as dag:
    task_1 = DummyOperator(
        task_id='task_1'
        # retry = 5 @default
        # retry_delay = timedelta(minutes=5) @default 
    ) 

    task_2 = DummyOperator(
        task_id='task_2'
        # retry = 3  @DummyOperator pass retry ไม่ได้
        # retry_delay = timedelta(minutes=3)
        # retry = 3 @override
        # retry_delay = 3 @override
    ) 

    task_3 = DummyOperator(
        task_id='task_3'
        # retry = 5 @bydefault
        # retry_delay = timedelta(minutes=5) @default
    ) 

    downloading_data = PythonOperator(
        task_id='downloading_data',
        python_callable=_downloading_data
        # How to pass my own parameter into python function
        # python_callable=_downloading_data,
        # op_kwargs={'my_param': 42}
    )

    checking_data = PythonOperator(
        task_id='checking_data',
        python_callable=_checking_data
    )

    # Check if file exist before continue to next task    
    waiting_for_data = FileSensor(
        task_id='waiting_for_data',
        fs_conn_id='fs_default',
        filepath='my_file.txt',
        # poke_interval = how often to check if file exist -> 30 = default
        poke_interval=30
    )

    processing_data = BashOperator(
        task_id='processing_data',
        bash_command='exit 0',
        # if task fail -> do _failure function
        on_failure_callback=_failure
    )

    # [task_1, task_2, task_3] >> downloading_data >> waiting_for_data >> processing_data
    # or use chain in dl_data,wt_data,pc_data 
    chain(downloading_data, checking_data, waiting_for_data, processing_data)
    # because cannot use [list] >> [list] if want to cross dependency must use cross_downstream
    # cross_downstream([downloading_data, checking_data], [waiting_for_data, processing_data])
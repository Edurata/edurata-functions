import json
import importlib
from airflow.executors.local_executor import LocalExecutor
from airflow.executors.kubernetes_executor import KubernetesExecutor
from airflow.models.dag import DAG
from airflow.models.taskinstance import TaskInstance
from airflow.utils.dates import days_ago


def handler(inputs):
    """
    Executes a task using a specified Airflow operator and executor.

    Args:
        inputs (dict): A dictionary with the following keys:
            - operator_path: The Python module path for the Airflow operator.
            - operator_params: Parameters for the operator as a JSON string.
            - executor_type: The executor to use ('LocalExecutor' or 'KubernetesExecutor').
            - execution_context: Context for task execution as a JSON string.

    Returns:
        dict: Result or status of the executed task.
    """
    operator_path = inputs.get('operator_path')
    operator_params = inputs.get('operator_params')
    executor_type = inputs.get('executor_type')
    execution_context = inputs.get('execution_context', '{}')

    # Validate executor type
    if executor_type not in ["LocalExecutor", "KubernetesExecutor"]:
        return {"error": "Invalid executor type. Supported values are 'LocalExecutor' and 'KubernetesExecutor'."}

    # Parse operator parameters and context
    try:
        operator_params = json.loads(operator_params)
        execution_context = json.loads(execution_context)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON input: {e}"}

    # Dynamically import the operator
    try:
        module_name, class_name = operator_path.rsplit('.', 1)
        operator_module = importlib.import_module(module_name)
        operator_class = getattr(operator_module, class_name)
    except (ImportError, AttributeError) as e:
        return {"error": f"Failed to import operator: {e}"}

    # Define a dummy DAG for execution context
    dag = DAG(dag_id="dynamic_task_dag", default_args={"start_date": days_ago(1)})

    # Instantiate the operator
    try:
        task = operator_class(task_id="dynamic_task", dag=dag, **operator_params)
    except TypeError as e:
        return {"error": f"Failed to instantiate operator: {e}"}

    # Create a TaskInstance
    task_instance = TaskInstance(task=task, execution_date=execution_context.get("execution_date"))

    # Execute the task using the specified executor
    executor = LocalExecutor() if executor_type == "LocalExecutor" else KubernetesExecutor()
    try:
        executor.start()
        task_instance.run(ignore_all_deps=True, executor=executor)
        executor.end()
        return {"result": f"Task {task.task_id} executed successfully."}
    except Exception as e:
        return {"error": f"Task execution failed: {e}"}


# Example function call:
# inputs = {
#     "operator_path": "airflow.operators.bash.BashOperator",
#     "operator_params": '{"bash_command": "echo Hello, World!"}',
#     "executor_type": "LocalExecutor",
#     "execution_context": '{}'
# }
# outputs = handler(inputs)
# print(outputs)

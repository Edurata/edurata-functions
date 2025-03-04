import json
import ansible_runner

def handler(inputs):
    """
    Executes an Ansible task dynamically based on inputs.

    Args:
        inputs (dict): A dictionary with the following keys:
            - module: The Ansible module to use (e.g., 'shell', 'copy', 'ping').
            - task: The task or command to execute using the specified module.
            - config: Configuration for the module as a JSON/YAML string.
            - inventory: Path to the Ansible inventory file.

    Returns:
        dict: The result of the Ansible task execution.
    """
    module = inputs.get('module')
    task = inputs.get('task')
    config = inputs.get('config')
    inventory = inputs.get('inventory')

    # Parse the config into a dictionary if it's a string
    try:
        config_dict = json.loads(config)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON/YAML config: {e}"}

    # Build Ansible task arguments
    task_args = {
        'module': module,
        'args': config_dict,
    }

    # Run the Ansible task using ansible-runner
    try:
        result = ansible_runner.run(
            private_data_dir='/tmp/ansible_runner',
            inventory=inventory,
            playbook=None,  # We're building the task dynamically
            module=module,
            module_args=config_dict,
            quiet=True
        )
        return {"result": result.stdout}
    except Exception as e:
        return {"error": str(e)}

# Example function call:
# inputs = {
#     "module": "ping",
#     "task": "Test connectivity",
#     "config": "{}",
#     "inventory": "/path/to/inventory"
# }
# outputs = handler(inputs)
# print(outputs)

import yaml
import subprocess

def modify_yaml(data, new_volume_name):
    # Modify the volume name property in the in-memory data
    for container in data['spec']['containers']:
        for volume in container.get('volumeMounts', []):
            if volume.get('name') == 'claim0':
                volume['name'] = new_volume_name

def apply_modified_yaml(data):
    # Apply the modified YAML data directly to the cluster using kubectl
    modified_yaml = yaml.dump(data, default_style='"', default_flow_style=False)
    subprocess.run(['kubectl', 'apply', '-f', '-'], input=modified_yaml, text=True)

if __name__ == '__main__':
    # Define the new volume name
    new_volume_name = 'claim1'

    # Load and parse the first YAML file
    with open('overleaf/kubernetes/contacts-pv.yaml', 'r') as file:
        yaml_data = yaml.safe_load(file)

    # Modify the in-memory data
    modify_yaml(yaml_data, new_volume_name)

    # Apply the modified YAML data directly to the cluster
    apply_modified_yaml(yaml_data)

    # Repeat the process for the second YAML file
    with open('file2.yaml', 'r') as file:
        yaml_data = yaml.safe_load(file)

    modify_yaml(yaml_data, new_volume_name)
    apply_modified_yaml(yaml_data)

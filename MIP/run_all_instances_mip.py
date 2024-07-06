import os
import subprocess

def get_instance_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.dat')]

def main():
    instances_dir = '/app/Instances'
    instance_files = get_instance_files(instances_dir)
    
    for instance_file in instance_files:
        instance_number = instance_file.split('.')[0].replace('inst', '')
        print(f"Processing instance {instance_number}")
        subprocess.run(['python', './MIP/solve_instance_mip.py', instance_number])

if __name__ == '__main__':
    main()

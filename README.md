# CMDO Project

## Instructions to run the project

### SAT/MIP

Example for SAT (for MIP replace ./SAT/solve_instance.py <instance_number> par ./MIP/ ...)

#### Build the image

```bash
docker build -t sat_mip -f Dockerfile.sat_mip .
```
#### One instance
```bash
docker run --rm -v ${PWD}/res:/app/res -v ${PWD}/Instances:/app/Instances sat_mip python ./SAT/solve_instance.py <instance_number>, (replace ${PWD} $(pwd) for mac)
```
Example :
```bash
docker run --rm -v ${PWD}/res:/app/res -v ${PWD}/Instances:/app/Instances sat_mip python ./SAT/solve_instance.py 01
```
#### All instances
```bash
docker run --rm -v ${PWD}/res:/app/res -v ${PWD}/Instances:/app/Instances sat_mip python ./SAT/run_all_instances.py
Check the solution :
docker run --rm -v ${PWD}/res:/app/res -v ${PWD}/Instances:/app/Instances sat_mip python solution_checker.py /app/Instances /app/res/
```
### CP
#### Build the image
```bash
docker build -t cp -f Dockerfile.cp .
```
#### One instance
```bash
docker run --rm -v ${PWD}/CP/results:/src/CP/results -v ${PWD}/result/CP:/src/result/CP -v ${PWD}/Instances_dzn:/src/Instances_dzn cp ./run_single_model.sh /src/CP/<model.mzn> /src/Instances_dzn/<instance_file_name> /src/CP/results/<model>/Gecode/<instance_file_name_output> Gecode
```
Example: 
```bash
docker run --rm -v ${PWD}/CP/results:/src/CP/results -v ${PWD}/result/CP:/src/result/CP -v ${PWD}/Instances_dzn:/src/Instances_dzn cp single /src/CP/nsb_dwd_im.mzn /src/Instances_dzn/inst01.dzn /src/CP/results/nsb_dwd_im/Gecode/inst01.json Gecode
```

#### All instance
```bash
docker run --rm -v ${PWD}/CP/results:/src/CP/results -v ${PWD}/result/CP:/src/result/CP cp all
```

## Repository structure 

cmdo_project/
├── SAT/
│   ├── solve_instance.py
│   ├── run_all_instances.py
│   ├── solver_module.py
│   ├── variables.py
│   ├── constraints.py
├── CP/
│   ├── process_files/
│   │    ├── post_processing.py
│   │    ├──pre_process_files.py
│   ├── results/
│   │   ├── nsb_dwd_im/
│   │   │   ├── Chuffed/
│   │   │   │   ├── inst01.json
│   │   │   │   ├── inst02.json
│   │   │   │   ├── ...
│   │   │   ├── Gecode/
│   │   │   │   ├── inst01.json
│   │   │   │   ├── inst02.json
│   │   │   │   ├── ...
│   │   ├── nsb_dwd_ir/
│   │   │   ├── Chuffed/
│   │   │   │   ├── inst01.json
│   │   │   │   ├── inst02.json
│   │   │   │   ├── ...
│   │   │   ├── Gecode/
│   │   │   │   ├── inst01.json
│   │   │   │   ├── inst02.json
│   │   │   │   ├── ...
│   │   ├── sb_dwd_im/
│   │   │   ├── Chuffed/
│   │   │   │   ├── inst01.json
│   │   │   │   ├── inst02.json
│   │   │   │   ├── ...
│   │   │   ├── Gecode/
│   │   │   │   ├── inst01.json
│   │   │   │   ├── inst02.json
│   │   │   │   ├── ...
│   │   ├── sb_dwd_im/
│   │   │   ├── Chuffed/
│   │   │   │   ├── inst01.json
│   │   │   │   ├── inst02.json
│   │   │   │   ├── ...
│   │   │   ├── Gecode/
│   │   │   │   ├── inst01.json
│   │   │   │   ├── inst02.json
│   │   │   │   ├── ...
│   ├── shell_scripts_docker
│   │   ├── entrypoint
│   │   ├── run_all_models.sh
│   │   ├── run_model.sh
│   │   ├── run_single_model
│   ├── nsb_dwd_im.mzn
│   ├── nsb_dwd_ir.mzn
│   ├── sb_dwd_im
│   ├── sb_dwd_ir
├── MIP/
│   ├── ...
│   ├── ...
│   ├── ...
│   ├── ...
│   ├── ...
├── result/
│   ├── SAT/
│   ├── CP/
│   └── MIP/
├── Instances/
│   ├── inst01.dat
│   ├── inst02.dat
│   ├──...
│   └── inst21.dat
├── Instances_dzn/
│   ├── inst01.dzn
│   ├── inst02.dzn
│   ├──...
│   └── inst21.dzn
├── Dockerfile.cp
├── Dockerfile.sat_mip
├── requirements.txt
├── requirements_cp.txt
├── solution_checker.py
├── run_all_models.sh
├── run_model.sh
└── README.md

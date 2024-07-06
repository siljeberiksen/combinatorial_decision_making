# CMDO Project

## Instructions to run the project

### Build the Docker image

```bash
docker build -t sat_mip -f Dockerfile.sat_mip .

SAT/MIP
Example for SAT (for MIP replace ./SAT/solve_instance.py <instance_number> par ./MIP/ ...)
One instance :
docker run --rm -v ${PWD}/result:/app/result -v ${PWD}/Instances:/app/Instances sat_mip python ./SAT/solve_instance.py <instance_number>, (replace ${PWD} $(pwd) for mac)
Example :
docker run --rm -v ${PWD}/result:/app/result -v ${PWD}/Instances:/app/Instances sat_mip python ./SAT/solve_instance.py 01
All Instances :
docker run --rm -v ${PWD}/result:/app/result -v ${PWD}/Instances:/app/Instances sat_mip python ./SAT/run_all_instances.py
Check the solution :
docker run --rm -v ${PWD}/result:/app/result -v ${PWD}/Instances:/app/Instances sat_mip python solution_checker.py /app/Instances /app/result/

Launch the docker with  CP : 
docker build -t cp -f Dockerfile.cp .


All instances of all models :
docker run --rm -v ${PWD}/CP/results:/src/CP/results cp ./run_all_models.sh
docker run --rm -v ${PWD}/CP/results:/src/CP/results -v ${PWD}/result/CP:/src/result/CP cp all
One instance of a model :
docker run --rm -v ${PWD}/CP/results:/src/CP/results -v ${PWD}/Instances_dzn:/src/Instances_dzn cp ./run_single_model.sh /src/CP/<model.mzn> /src/Instances_dzn/<instance_file_name> /src/CP/results/<model>/Gecode/<instance_file_name_output> Gecode

docker run --rm -v ${PWD}/CP/results:/src/CP/results -v ${PWD}/Instances_dzn:/src/Instances_dzn cp ./run_single_model.sh /src/CP/nsb_dwd_im.mzn /src/Instances_dzn/inst01.dzn /src/CP/results/nsb_dwd_im/Gecode/inst01.json Gecode


docker run --rm -v ${PWD}/CP/results:/src/CP/results -v ${PWD}/result/CP:/src/result/CP cp single /src/CP/nsb_dwd_im.mzn /src/Instances_dzn/inst01.dzn /src/CP/results/nsb_dwd_im/Gecode/inst01.json Gecode

docker run --rm -v ${PWD}/CP/results:/src/CP/results -v ${PWD}/result/CP:/src/result/CP cp single /src/CP/nsb_dwd_im.mzn /src/Instances_dzn/inst01.dzn /src/CP/results/nsb_dwd_im/Gecode/inst01.json Gecode

cmdo_project/
├── SAT/
│   ├── solve_instance.py
│   ├── run_all_instances.py
│   ├── solver_module.py
│   ├── variables.py
│   ├── constraints.py
├── CP/
│   ├── solve_instance.py
│   ├── run_all_instances.py
│   ├── solver_module.py
│   ├── variables.py
│   ├── constraints.py
├── MIP/
│   ├── ...
│   ├── ...
│   ├── ...
│   ├── ...
│   ├── ...
├── res/
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
├── solution_checker.py
├── run_all_models.sh
├── run_model.sh
└── README.md

FROM minizinc/minizinc:latest

WORKDIR /src

COPY . .

#RUN apt-get install python3

CMD minizinc --json-stream --solver Gecode CP/eksamen.mzn -d instances/inst01.dat

## %% python3 main.py
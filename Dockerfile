FROM minizinc/minizinc:latest

WORKDIR /src

COPY . .

#RUN apt-get install python3

CMD minizinc --solver Gecode CP/eksamen.mzn --json-stream 

## %% python3 main.py
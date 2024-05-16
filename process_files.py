def read_input_file(input_filename):
    with open(input_filename, 'r') as file:
        lines = file.readlines()
    
    # Process the input data
    m = int(lines[0].strip())
    n = int(lines[1].strip())
    li =  list(map(int, lines[2].strip().split()))
    sj = list(map(int, lines[3].strip().split()))
    D = [list(map(int, line.strip().split())) for line in lines[4:]]
    
    return m, n, li, sj, D

def write_dzn_file(output_filename, m, n, li, sj, D):
    with open(output_filename, 'w') as f:
        # Write the number of couriers
        f.write(f'm = {m};\n\n')
        
        # Write the number of items
        f.write(f'n = {n};\n\n')
        
        # Write the load limits for each courier
        f.write('li = [')
        f.write(', '.join(map(str, li)))
        f.write('];\n\n')
        
        # Write the size of each item
        f.write('sj = [')
        f.write(', '.join(map(str, sj)))
        f.write('];\n\n')
        
        # Write the distance matrix
        f.write('D = [|')
        for row in D:
            f.write(', '.join(map(str, row)))
            if row != D[-1]:
                f.write('\n     |')
        f.write('|];\n')


m, n, li, sj, D = read_input_file("instances/inst01.dat")
instances = [f"Instances/inst{i:02}.dat" for i in range(1, 22)]
instances_dzn = [f"Instances_dzn/inst{i:02}.dzn" for i in range(1, 22)]

for i in range(0,21):
    m, n, li, sj, D = read_input_file(instances[i])
    write_dzn_file(instances_dzn[i], m, n, li, sj, D)
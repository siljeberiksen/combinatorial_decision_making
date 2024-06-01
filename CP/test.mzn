include "alldifferent.mzn";
include "gecode.mzn";
include "lex_lesseq.mzn";
include "circuit.mzn";
include "lex_lesseq.mzn";
%simpler

int: m; % number of couriers
int: n; % number of items

set of int: COURIERS = 1..m; 
set of int: ITEMS = 1..n;  
set of int: LOCATIONS = 1..n+1; % Including the origin

array [COURIERS] of var int: li;
array [ITEMS] of var int: sj;
array[LOCATIONS, LOCATIONS] of var int: D;

% Look into triangle inacuality
% Array to store the next location in the route for each courier
array[COURIERS, LOCATIONS] of var 0..n+1: next_location;
array[COURRIERS, 1..n] of var bool: in_circuit; 



% Ensure in_circuit array reflects whether a node is in the circuit
constraint forall(c in COURRIERS, i in 1..n) (in_circuit[c, i] = (tour[i] != 0));

% Ensure each location is visited exactly once by some courier
constraint forall(i in ITEMS)(
    sum(c in COURIERS, j in LOCATIONS)(next_location[c, j] == i) == 1
);


% Circuit constraint for each courier
constraint forall(c in COURIERS)(
    circuit(next_location[c,..])
);



% Bounding max distance
% Determine realistic lower and upper bounds for max_distance

% Constraint to ensure max_distance is the maximum distance travelled by any courier
%Minimize the maximum distance traveled
% Calculate the distance traveled by each courier
array[COURIERS] of var int: distances = [
    sum(i in LOCATIONS) (D[i, next_location[c, i]]) | c in COURIERS
];


var int: max_distance = max(c in COURIERS) (distances[c]);

solve minimize max_distance;
    
output [
    "Routes: " ++ show([next_location[c,i] | c in COURIERS, i in ITEMS]) ++ "\n",
    "Distances: " ++ show(distances) ++ "\\n" ,
    "Max Distance: " ++ show(max_distance) ++ "\n",
    "Next Location: " ++ show(next_location) ++ "\\n",
];


%TODO:
% Bounds not included
% Triangle inaquality 
% Symmetry
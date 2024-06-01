include "alldifferent.mzn";
include "gecode.mzn";
include "lex_lesseq.mzn";
include "subcircuit.mzn";
include "lex_lesseq.mzn";

int: m; % number of couriers
int: n; % number of items

set of int: COURIERS = 1..m; 
set of int: ITEMS = 1..n;  
set of int: LOCATIONS = 1..n+1; % Including the origin

array [COURIERS] of var int: li;
array [ITEMS] of var int: sj;
array[LOCATIONS, LOCATIONS] of var int: D;

% Look into triangle inacuality
array [COURIERS, LOCATIONS, LOCATIONS] of var bool: routes;

% Number of inputs = number of outputs
%constraint forall(c in COURIERS, i in LOCATIONS) (
%    sum(j in LOCATIONS) (routes[c, i, j]) = sum(j in LOCATIONS) (routes[c, j, i])
%);

% Capacity constraint 
constraint forall (c in COURIERS) (
    sum(i in LOCATIONS, j in ITEMS) (routes[c,i,j] * sj[j]) <= li[c]
);
%Need to have LOCATIONS to have all 

% Ensure each item deliverd
constraint forall(i in ITEMS)(
    sum(c in COURIERS, j in LOCATIONS where i != j) (routes[c, i, j]) == 1
);

constraint forall(j in ITEMS)(
    sum(c in COURIERS, i in LOCATIONS where i != j) (routes[c, i, j]) == 1
);

% Circuit constraint for each courier
constraint forall(c in COURIERS)(
    subcircuit([ if sum(routes[c, i, ..]) == 0 then i else 
              sum(j in LOCATIONS where routes[c, i, j])(j) endif | i in LOCATIONS])
);


%Ensure routes start and end at the origin for each courier
constraint forall(c in COURIERS) (
    sum(i in ITEMS) (routes[c, n+1, i]) == 1
);
constraint forall(c in COURIERS) (
    sum(i in ITEMS) (routes[c, i, n+1]) == 1
);


% Minimize the maximum distance traveled
array [COURIERS] of var int: distances = [sum(i in LOCATIONS, j in LOCATIONS) (routes[c, i, j] * D[i, j]) | c in COURIERS];
var int: max_distance = max(c in COURIERS) (distances[c]);



% Bounding max distance
% Determine realistic lower and upper bounds for max_distance

% Constraint to ensure max_distance is the maximum distance travelled by any courier

solve minimize max_distance;
    
output [
    "Routes: " ++ show([routes[c,i,j] | c in COURIERS, i in LOCATIONS, j in  LOCATIONS]) ++ "\n",
    "Distances: " ++ show(distances) ++ "\\n" ,
    "Max Distance: " ++ show(max_distance) ++ "\n",
];

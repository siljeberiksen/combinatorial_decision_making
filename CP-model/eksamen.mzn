include "alldifferent.mzn";
include "gecode.mzn";
include "lex_lesseq.mzn";
include "circuit.mzn";
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

array [COURIERS, LOCATIONS, LOCATIONS] of var bool: routes;
%If tru

% Define the number of couriers
m = 3;

% Define the number of items
n = 5;

% Define load limits for each courier
li = [100, 150, 200];

% Define the size of each item
sj = [20, 30, 50, 30, 40];
 
% Define a 6x6 distance matrix (including the origin)
D = 
    [|0, 2, 3, 7, 6, 8
     |2, 0, 6, 5, 7, 9
     |3, 6, 0, 8, 5, 11
     |7, 5, 8, 0, 4, 3
     |6, 7, 5, 4, 0, 2
     |8, 9, 11, 3, 2, 0|];

% Capacity constraint 
constraint forall (c in COURIERS) (
    sum(i in ITEMS, j in ITEMS) (routes[c,i,j] * sj[i]) <= li[c]
);


% Ensure each item is picked up and delivered exactly once
constraint forall(i in ITEMS)(
    sum(c in COURIERS, j in LOCATIONS where i != j) (routes[c, i, j]) == 1
);

% Ensure routes start and end at the origin for each courier
constraint forall(c in COURIERS) (
    sum(i in ITEMS) (routes[c, n+1, i]) == 1 /\ % Route must start at the origin
    sum(i in ITEMS) (routes[c, i, n+1]) == 1    % Route must end at the origin
);

% Minimize the maximum distance traveled
array [COURIERS] of var int: distances = [sum(i in LOCATIONS, j in LOCATIONS) (routes[c, i, j] * D[i, j]) | c in COURIERS];
var int: max_distance = max(c in COURIERS) (distances[c]);
solve minimize max_distance;

output [
    "Routes: " ++ show([routes[c,i,j] | c in COURIERS, i in LOCATIONS, j in  LOCATIONS]) ++ "\n",
    "Max Distance: " ++ show(max_distance) ++ "\n"
];

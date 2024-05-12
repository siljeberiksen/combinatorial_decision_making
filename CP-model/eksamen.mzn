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

% Number of inputs = number of outputs
constraint forall(c in COURIERS, i in LOCATIONS) (
    sum(j in LOCATIONS) (routes[c, i, j]) = sum(j in LOCATIONS) (routes[c, j, i])
);

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
    sum(c in COURIERS, j in LOCATIONS where i != j) (routes[c, i, j]) >= 1
);


%Ensure routes start and end at the origin for each courier
constraint forall(c in COURIERS) (
    sum(i in ITEMS) (routes[c, n+1, i]) == 1
);
constraint forall(c in COURIERS) (
    sum(i in ITEMS) (routes[c, i, n+1]) == 1
);

%Check that same amount of in and out for the same node, making it a valid route
constraint forall(c in COURIERS, i in LOCATIONS) (
    sum(j in LOCATIONS) (routes[c, i, j]) = sum(j in LOCATIONS) (routes[c, j, i])
);

% Prohibit immediate return to the last location and no going to current position
constraint forall(c in COURIERS, i in LOCATIONS, j in LOCATIONS) (
    routes[c, i, j] -> not routes[c, j, i] /\
    routes[c,i,i] == 0
);

%Look into circuit

% Ensure each courier's route is a valid loop
%constraint forall(c in COURIERS) (
%    circuit([if j = n+1 then n+1 else sum(i in LOCATIONS) (i * routes[c, i, j]) endif | j in LOCATIONS])
%);
% Additional output function to trace the path

%constraint forall(c in COURIERS, i in LOCATIONS) (
    % The next location must correspond to a true route
%    next_location[c, i] = sum(j in LOCATIONS) (j * routes[c, i, j])
%);

%constraint forall (c in COURIERS) (
%    circuit([next_location[c, i] | i in 1..n] ++ [next_location[c, n+1]])
%

% Ensure every location is part of a loop by checking in-degree and out-degree
%constraint forall(c in COURIERS)(
%    forall(i in LOCATIONS) (
%       sum(j in LOCATIONS) (routes[c, j, i]) = sum(j in LOCATIONS) (routes[c, i, j])
%    )
%);
%To use circuit we will need an auciliritary 


% Minimize the maximum distance traveled
array [COURIERS] of var int: distances = [sum(i in LOCATIONS, j in LOCATIONS) (routes[c, i, j] * D[i, j]) | c in COURIERS];
var int: max_distance = max(c in COURIERS) (distances[c]);
solve minimize max_distance;
    
output [
    "Routes: " ++ show([routes[3,i,j] | i in LOCATIONS, j in  LOCATIONS]) ++ "\n",
    "Max Distance: " ++ show(max_distance) ++ "\n",
];


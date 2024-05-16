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

% Capacity constraint 
constraint forall (c in COURIERS) (
    sum(i in LOCATIONS, j in ITEMS) (routes[c,i,j] * sj[j]) <= li[c]
);
%Need to have LOCATIONS to have all 

% Ensure each item deliverd
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

%Check that same amount ofin in and out for the same node, making it a valid route
constraint forall(c in COURIERS, i in LOCATIONS) (
    sum(j in LOCATIONS) (routes[c, i, j]) = sum(j in LOCATIONS) (routes[c, j, i])
);

% Prohibit immediate return to the last location and no going to current position
constraint forall(c in COURIERS, i in LOCATIONS, j in LOCATIONS) (
    routes[c, i, j] -> not routes[c, j, i] /\
    routes[c,i,i] == 0
);

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

% Bounding max distance
    
output [
    "Routes: " ++ show([routes[c,i,j] | c in COURIERS, i in LOCATIONS, j in  LOCATIONS]) ++ "\n",
    "Max Distance: " ++ show(max_distance) ++ "\n",
];


%TODO:
% Bounds not included
% Triangle inaquality 
% Symmetry
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
array [COURIERS, LOCATIONS, LOCATIONS] of var bool: routes;


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


%Ensure routes start and end at the origin for each courier
constraint forall(c in COURIERS) (
    sum(i in ITEMS) (routes[c, n+1, i]) == 1
);
constraint forall(c in COURIERS) (
    sum(i in ITEMS) (routes[c, i, n+1]) == 1
);

%Check that same amount of in in and out for the same node, making it a valid route
constraint forall(c in COURIERS, i in LOCATIONS) (
   sum(j in LOCATIONS) (routes[c, i, j]) = sum(j in LOCATIONS) (routes[c, j, i])
);
% Prohibit self-loops
constraint forall(c in COURIERS, i in LOCATIONS) (
    routes[c, i, i] == 0
);
% Prohibit immediate return to the last location and no going to current position
% Only items to make it possible to couriers to collect only one item
constraint forall(c in COURIERS, i in ITEMS, j in ITEMS) (
    routes[c, i, j] -> not routes[c, j, i]
);

% Circuit constraint for each courier
constraint forall(c in COURIERS)(
    circuit([if next_location[c, i] != 0 then next_location[c, i] else i endif | i in LOCATIONS])
);

% Allow single item pickup but restrict direct travel from origin to multiple items
constraint forall(c in COURIERS) (
   sum(i in ITEMS, j in LOCATIONS) (routes[c, i, j]) > 1 ->(
    forall(i in ITEMS) (
        routes[c, n+1, i] -> not routes[c, i, n+1])
    )
);

%Triangle inaquality 
%D[i,k]≤D[i,j]+D[j,k] for each i,j,k

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

% Symmetry breaking: Impose lexicographic order on the items delivered by the couriers
array[COURIERS, ITEMS] of var int: delivered_items;
constraint forall(c in COURIERS, i in ITEMS)(
    delivered_items[c, i] = sum(j in LOCATIONS) (j * routes[c, j, i])
);

constraint forall(c in 1..m-1)(
    lex_lesseq([delivered_items[c, i] | i in ITEMS], [delivered_items[c+1, i] | i in ITEMS])
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


%TODO:
% Bounds not included
% Triangle inaquality 
% Symmetry
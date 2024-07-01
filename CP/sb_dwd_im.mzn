include "lex_lesseq.mzn";

int: m; % number of couriers
int: n; % number of items

set of int: COURIERS = 1..m; 
set of int: ITEMS = 1..n;  
set of int: LOCATIONS = 1..n+1; % Including the origin

array [COURIERS] of var int: li;
array [ITEMS] of var int: sj;
array[LOCATIONS, LOCATIONS] of var int: D;
array [COURIERS, LOCATIONS, LOCATIONS] of var bool: routes;

% Capacity constraint 
constraint forall (c in COURIERS) (
    sum(i in LOCATIONS, j in ITEMS) (routes[c,i,j] * sj[j]) <= li[c]
);

% Ensure each item is delivered exactly once by any courier to any location
constraint forall(i in ITEMS)(
    count_eq([routes[c, i, j] | c in COURIERS, j in LOCATIONS where i != j], 1,1)
);

% Ensure each item is picked up exactly once by any courier from any location
constraint forall(j in ITEMS)(
    count_eq([routes[c, i, j] | c in COURIERS, i in LOCATIONS where i != j], 1,1)
);

%Ensure routes start and end at the origin for each courier
constraint forall(c in COURIERS) (
    count_eq([routes[c, n+1, i]| i in ITEMS],1,1)
);
constraint forall(c in COURIERS) (
    count_eq([routes[c, i, n+1]| i in ITEMS],1,1)
);

%Check that same amount of in in and out for the same node, making it a valid route
constraint forall(c in COURIERS, i in LOCATIONS) (
   sum(j in LOCATIONS) (routes[c, i, j]) = sum(j in LOCATIONS) (routes[c, j, i])
);

% Prohibit self-loops
constraint forall(c in COURIERS, i in LOCATIONS) (
    routes[c, i, i] == 0
);
% Prohibit immediate return to the last location a
% Only items to make it possible to couriers to collect only one item
constraint forall(c in COURIERS, i in ITEMS, j in ITEMS) (
    routes[c, i, j] -> not routes[c, j, i]
);

% Allow single item pickup but restrict direct travel from origin to multiple items
constraint forall(c in COURIERS) (
   sum(i in ITEMS, j in LOCATIONS) (routes[c, i, j]) > 1 ->(
    forall(i in ITEMS) (
        routes[c, n+1, i] -> not routes[c, i, n+1])
    )
);

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

ann:search_ann;

%search_ann = int_search([routes[c, i, j] | c in COURIERS, i in LOCATIONS, j in LOCATIONS], input_order, indomain_min);
%search_ann = int_search([routes[c, i, j] | c in COURIERS, i in LOCATIONS, j in LOCATIONS], input_order, indomain_random);
%search_ann = int_search([routes[c, i, j] | c in COURIERS, i in LOCATIONS, j in LOCATIONS], first_fail, indomain_min);
%search_ann = int_search([routes[c, i, j] | c in COURIERS, i in LOCATIONS, j in LOCATIONS], first_fail, indomain_random);
search_ann = int_search([routes[c, i, j] | c in COURIERS, i in LOCATIONS, j in LOCATIONS], dom_w_deg, indomain_min);
%search_ann = int_search([routes[c, i, j] | c in COURIERS, i in LOCATIONS, j in LOCATIONS], dom_w_wdeg, indomain_random);
solve
::search_ann 
minimize max_distance;

    
output [
    "Routes: " ++ show([routes[c,i,j] | c in COURIERS, i in LOCATIONS, j in  LOCATIONS]) ++ "\n",
    "Distances: " ++ show(distances) ++ "\\n" ,
    "Max Distance: " ++ show(max_distance) ++ "\n",
];
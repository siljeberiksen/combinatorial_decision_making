% Parameters
int: m;  % number of couriers
int: n;  % number of items
int: o;  % origin
array[1..m] of int: f_l;  % first location of courier i starts with
array[1..m] of int: l_l;  % last location of courier i ends with
array[1..m] of int: l_i;  % max. load size of each courier
array[1..n] of int: s_j;  % size of each item
array[1..n, 1..n] of int: D;  % distance matrix

% Decision variables
array[1..m] of var 0..sum(s_j): load;  % load size of each courier
array[1..m] of var 0..sum([D[i,j] | i in 1..n, j in 1..n]): distance;  % distance traveled by each courier
array[1..m] of var 0..n: numberOfItems;  % number of items which are assigned to each courier
array[1..m, 1..n] of var 0..1: assigning;  % if item j is assigned to the courier i, array[i,j] (b_i_j) variable is 1, otherwise 0

% Constraints
constraint forall(i in 1..m) (
    f_l[i] = o /\ l_l[i] = o  % each courier starts and ends at the central location
);

constraint forall(j in 1..n) (
    sum(i in 1..m) (assigning[i,j]) = 1  % each item should be assigned to exactly one courier
);

constraint forall(i in 1..m) (
    sum(j in 1..n) (assigning[i,j] * s_j[j]) <= l_i[i]  % sum of item sizes cannot exceed max load
);

% Objective Function
var int: distanceMax = max([distance[i] | i in 1..m]);
solve minimize distanceMax;

% Distance calculation
constraint forall(i in 1..m) (
    let {
        var int: lastTraveledItem = 0;
    } in
    distance[i] = sum(j in 1..n) (
        if assigning[i,j] == 1 then
            if lastTraveledItem == 0 then
                D[o,j]
            else
                D[lastTraveledItem,j]
            endif
        else
            0
        endif
    ) 
);

% Calculate total number of items for each courier
constraint forall(i in 1..m) (
    numberOfItems[i] = sum(j in 1..n) (assigning[i,j])
);

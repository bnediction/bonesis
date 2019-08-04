#program diversity.
#heuristic clause(N,C,L,S) : avoidclause(N,C,L,S). [10,false]
#heuristic constant(N) : avoidconstant(N). [2,false]
#heuristic clause(N,C,L,S). [1,false] %subset
#external avoidclause(N,C,L,S) : clause(N,C,L,S).
#external avoidconstant(N) : constant(N).

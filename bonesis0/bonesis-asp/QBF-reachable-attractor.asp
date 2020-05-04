%%%%%%%%%%%%%
% CONSTRAINT:
% Each attractors reachable from S is compatible with (one of) the set of markers defined as X.
% Several states X can be precised.
%%%%%%%%%%%%%

% Disjunctive rule: (to explore all configurations)
cfg((_za_,S),N,-1) ; cfg((_za_,S),N,1) :- node(N), is_global_at(_,S), not clamped(S,N,_).

% Check properties:
%% Extension of perturbations for the evaluations below:
2 {clamped((fp,S),N,V); clamped((_za_,S),N,V)} 2 :- clamped(S,N,V); is_global_at(_,S).
%% Either the configuration _za_ is non reachable from S:
mcfg((fp,S),N,V) :- cfg(S,N,V), is_global_at(_,S).
mcfg((fp,S),N,V) :- eval((fp,S),N,V).
valid(_za_,S) :- not mcfg((fp,S),N,V), cfg((_za_,S),N,V), is_global_at(_,S).
%% Or markers defining the fate 'X' have to be in the maximal configuration of _za_:
mcfg((_za_,S),N,V) :- cfg((_za_,S),N,V).
mcfg((_za_,S),N,V) :- eval((_za_,S),N,V).
valid(_za_,S) :- mcfg((_za_,S),N,V):obs(X,N,V); is_global_at((obs,X),S).

% Saturation of the predicate under disjunctive rule:
%% (to benefit from the subset minimality semantics
%% to consider each subset - so each configuration)
cfg((_za_,S),N,-V) :- cfg((_za_,S),N,V) ; valid(_za_,S).

% A solution has to respect at least one of the above properties:
:- not valid(_za_,S); is_global_at(_,S).

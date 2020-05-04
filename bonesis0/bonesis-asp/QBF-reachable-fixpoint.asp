%%%%%%%%%%%%%
% CONSTRAINT:
% Each fixpoint reachable from S is compatible with (one of) the set of markers defined as X.
% Several states X can be precised.
%%%%%%%%%%%%%

% Disjunctive rule: (to explore all configurations)
cfg((_z_,S),N,-1) ; cfg((_z_,S),N,1) :- node(N), is_global_fp(_,S), not clamped(S,N,_).

% Check properties:
%% Extension of perturbations for the evaluations below:
4 { clamped((fp,S),N,V); cfg((fp,S),N,V);
    clamped((_z_,S),N,V); cfg((_z_,S),N,V) } 4 :- clamped(S,N,V); is_global_fp(_,S).

%% Either the configuration _z_ is non reachable from S:
mcfg((fp,S),N,V) :- cfg(S,N,V), is_global_fp(_,S).
mcfg((fp,S),N,V) :- eval((fp,S),N,V).
valid(_z_,S) :- not mcfg((fp,S),N,V), cfg((_z_,S),N,V), is_global_fp(_,S).
%% Or the configuration is not a fixpoint
mcfg((_z_,S),N,V) :- cfg((_z_,S),N,V).
valid(_z_,S) :- cfg((_z_,S),N,V) ; eval((_z_,S),N,-V).
%% Or the configuration has at least the same markers than X
valid(_z_,S) :- cfg((_z_,S),N,V):obs(X,N,V); is_global_fp((obs,X),S).

% Saturation of the predicate under disjunctive rule:
%% (to benefit from the subset minimality semantics
%% to consider each subset - so each configuration)
cfg((_z_,S),N,-V) :- cfg((_z_,S),N,V) ; valid(_z_,S).

% A solution has to respect at least one of the above properties:
:- not valid(_z_,S); is_global_fp(_,S).


import bonesis

def marker_reprogramming_fixpoints(f, M, k, at_least_one=True, **some_opts):
    bo = bonesis.BoNesis(f)
    control = bo.Some(max_size=k, **some_opts)
    with bo.mutant(control):
        if at_least_one:
            bo.fixed(~bo.obs(M))
        bo.all_fixpoints(bo.obs(M))
    return control.assignments()

def source_marker_reprogramming_fixpoints(f, z, M, k, at_least_one=True,
        **some_opts):
    bo = bonesis.BoNesis(f)
    control = bo.Some(max_size=k, **some_opts)
    with bo.mutant(control):
        if at_least_one:
            ~bo.obs(z) >= bo.fixed(~bo.obs(M))
        ~bo.obs(z) >> "fixpoints" ^ {bo.obs(M)}
    return control.assignments()

def marker_reprogramming(f, M, k, **some_opts):
    bo = bonesis.BoNesis(f)
    bad_control = bo.Some(max_size=k, **some_opts)
    with bo.mutant(bad_control):
        x = bo.cfg()
        bo.in_attractor(x) != bo.obs(M)
    return bad_control.complementary_assignments()

def source_marker_reprogramming(f, z, M, k, **some_opts):
    bo = bonesis.BoNesis(f)
    bad_control = bo.Some(max_size=k, **some_opts)
    with bo.mutant(bad_control):
        x = bo.cfg()
        ~bo.obs(z) >= bo.in_attractor(x) != bo.obs(M)
    return bad_control.complementary_assignments()

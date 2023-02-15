# Copyright or © or Copr. Loïc Paulevé (2023)
#
# loic.pauleve@cnrs.fr
#
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
#

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

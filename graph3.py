"""

flagmatic 2

Copyright (c) 2012, E. R. Vaughan. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1) Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2) Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
	

# TODO: implement a forbidden_induced_edge_numbers.
# TODO: turn some forbidden graphs into forbidden edge numbers.


def generate_flags(n, tg, forbidden_edge_numbers={}, forbidden_graphs = [], forbidden_induced_graphs=[]):
	"""
	For an integer n, and a type tg, returns a list of all tg-flags on n
	vertices, that satisfy certain constraints.
	
	forbidden_edge_numbers should be a dictionary whose keys and values are integers,
	where an item (k, v) specifies that k-sets are to span fewer than v edges.
		
	forbidden_graphs should be a list of graphs that are forbidden as subgraphs.
	
	forbidden_induced_subgraphs should be a list of graphs that are forbidden as
	_induced_ subgraphs.
	
	EXAMPLES:
	
		sage: tg = (1,())
		sage: generate_flags(4, tg, forbidden_edge_numbers={4:2})
		[(4, ()), (4, ((2, 3, 4),)), (4, ((1, 2, 3),))]
	
	"""

	if tg is None:
		s = 0
	else:
		s = tg.n
		if tg.t != 0:
			raise NotImplementedError("type must not contain labelled vertices.")

	if n < s:
		return []

	if n == s:
		if tg is None:
			return [Flag()]
		else:
			ntg = tg.copy()
			ntg.t = s
			return [ntg]

	max_ne = (n - 1) * (n - 2) / 2
	max_e = n * max_ne / 3
	
	new_graphs = []
	hashes = set()
	
	smaller_graphs = generate_flags(n - 1, tg, forbidden_edge_numbers=forbidden_edge_numbers,
		forbidden_graphs=forbidden_graphs, forbidden_induced_graphs=forbidden_induced_graphs)
	
	possible_nbrs = Combinations(range(1, n), 2)

	for sg in smaller_graphs:
	
		pe = sg.ne
		ds = sg.degrees()
		maxd = max(ds[s:] + (0,))
			
		for ne in range(maxd, max_ne + 1):
		
			for nb in Combinations(possible_nbrs, ne):
			
				ng = sg.copy()
				ng.n = n
				for v in nb:
					ng.add_edge((v[0], v[1], n))

				if ng.has_forbidden_edge_numbers(forbidden_edge_numbers, must_have_highest=True):
					continue

				if ng.has_forbidden_graphs(forbidden_graphs, must_have_highest=True):
					continue

				if ng.has_forbidden_graphs(forbidden_induced_graphs, must_have_highest=True, induced=True):
					continue

				ng.make_minimal_isomorph()
				ng_hash = hash(ng)
				if not ng_hash in hashes:
					new_graphs.append(ng)
					hashes.add(ng_hash)

	return new_graphs


def generate_graphs(n, forbidden_edge_numbers={}, forbidden_graphs = [], forbidden_induced_graphs=[]):
	"""
	For an integer n, return a list of all 3-graphs on n vertices that satisfy certain
	constraints.
	
	forbidden_edge_numbers should be a dictionary whose keys and values are integers,
	where an item (k, v) specifies that k-sets are to span fewer than v edges.
		
	forbidden_graphs should be a list of graphs that are forbidden as subgraphs.
	
	forbidden_induced_subgraphs should be a list of graphs that are forbidden as
	_induced_ subgraphs.
	
	EXAMPLES:
	
		sage: generate_graphs(4, forbidden_edge_numbers={4:3})
		[(4, ()), (4, ((1, 2, 3),)), (4, ((1, 2, 3), (1, 2, 4)))]
	
	"""
	return generate_flags(n, None, forbidden_edge_numbers=forbidden_edge_numbers,
		forbidden_graphs=forbidden_graphs, forbidden_induced_graphs=forbidden_induced_graphs)


def flag_orbits(tg, flags):
	"""
	flags should be a list of flags of the type tg. Returns a list of tuples.
	Each tuple contains the indices of the flags that are in the same orbit
	under the action of relabelling the vertices of tg.
	"""
	s = tg.n
	min_flags = []

	for fg in flags:
		mfgs = str(fg)
		for perm in Permutations(range(1, s + 1)):
			permplus = perm + range(s + 1, fg.n + 1)
			ntg = tg.copy()
			ntg.relabel(perm)
			nfg = fg.copy()
			nfg.relabel(permplus)
			nfg.make_minimal_isomorph()
			nfgs = str(nfg)
			if nfgs < mfgs:
				mfgs = nfgs
		min_flags.append(mfgs)

	orbs = []
	for mfgs in set(min_flags):
		orbs.append(tuple([i for i in range(len(min_flags)) if min_flags[i] == mfgs]))

	return sorted(orbs)


from sage.modules.misc import gram_schmidt

def flag_basis(tg, flags, orthogonalize=True):
	"""
	flags should be a list of flags of the type tg. Returns a basis for the flags
	that is a block matrix of two blocks. Uses flag orbits to create invariant-
	anti-invariant decomposition. If orthogonalize=True, perform Gram-Schmidt
	orthogonalization.
	"""
	
	orbs = flag_orbits(tg, flags)
	
	Inv = matrix(QQ, len(orbs), len(flags), sparse=True)
	row = 0
	for orb in orbs:
		for j in orb:
			Inv[row, j] = 1
		row += 1
	
	# There might be no anti-invariant part.
	if len(orbs) == len(flags):
		return Inv
	
	AntiInv = matrix(QQ, len(flags) - len(orbs), len(flags), sparse=True)
	row = 0
	for orb in orbs:
		for j in orb[1:]:
			AntiInv[row, orb[0]] = 1
			AntiInv[row, j] = -1
			row += 1

	sys.stdout.write("Invariant-anti-invariant split: %d + %d = %d\n" % (Inv.nrows(), AntiInv.nrows(),
		len(flags)))
	
	if orthogonalize:
	
		# Note: the following does not preserve sparsity
		#AntiInv, mu = AntiInv.gram_schmidt()
	
		AntiInvRows, mu = gram_schmidt(AntiInv.rows())
		AntiInv = matrix(QQ, AntiInvRows, sparse=True)

	return block_matrix([[Inv],[AntiInv]])

	
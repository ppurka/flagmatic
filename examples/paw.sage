problem = GraphProblem(5, density="4:12233114")
problem.set_inactive_types(4)
construction = GraphBlowupConstruction("4:1223344111223344")
problem.set_extremal_construction(construction)
problem.compute_flag_bases()
problem.add_zero_eigenvectors(0, matrix(QQ,[[1, 0, 0, 1/2, 31/70], [0, 1, 49/106, 7/108, -17/20]]), use_bases=True)
problem.add_zero_eigenvectors(1, matrix(QQ,[[1,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0]]), use_bases=True)
problem.add_zero_eigenvectors(2, matrix(QQ,[[0,0,-5,0,8,0,0],[0,0,10,8,0,0,0]]), use_bases=True)
problem.add_zero_eigenvectors(3, matrix(QQ,[[0,0,0,3,-1,0,0],[0,1,0,0,0,0,0]]), use_bases=True)
problem.change_problem_bases()
problem.add_sharp_graphs(0, 4, 11, 18, 19, 24, 27)
problem.solve_sdp()
problem.make_exact()
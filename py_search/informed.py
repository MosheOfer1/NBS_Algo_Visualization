from py_search.base import SolutionNode
from py_search.base import NbsDataStructure


def near_optimal_front_to_end_bidirectional_search(problem):
    """
        Performs a near-optimal bidirectional search (NBS) from front to end, using a
        heuristic node value to guide the search. Returns an iterator to the
        solutions, allowing for multiple solutions to be found.

        :param problem: The problem to solve.
        :type problem: :class:`Problem`
    """
    c = float("inf")
    current_solution = None
    ffringe = NbsDataStructure(node_value_waiting=problem.node_value, node_value_ready=lambda n: n.cost())
    bfringe = NbsDataStructure(node_value_waiting=problem.node_value, node_value_ready=lambda n: n.cost())
    fclosed = {}
    ffringe.push(problem.initial)
    fclosed[problem.initial] = problem.initial.cost()

    bclosed = {}

    bfringe.push(problem.goal)
    bclosed[problem.goal] = problem.goal.cost()

    while len(ffringe) > 0 and len(bfringe) > 0:
        succeed, msg = ffringe.prepare_best(bfringe)
        if not succeed:
            return

        yield msg

        u_min = ffringe.peek()
        v_min = bfringe.peek()
        lower_bound = max(problem.node_value(u_min), problem.node_value(v_min), u_min.cost() + v_min.cost())

        if lower_bound >= c:
            print(f"found: {current_solution}")
            yield current_solution

        u_min = ffringe.pop()
        # Forward Expand
        for s in problem.successors(u_min):
            for goal in bfringe:
                if problem.goal_test(u_min, goal):
                    if c > u_min.cost() + goal.cost():
                        c = u_min.cost() + goal.cost()
                        current_solution = SolutionNode(u_min, goal)
            if s not in fclosed or s.cost() < fclosed[s]:
                ffringe.push(s)
                fclosed[s] = s.cost()
        yield u_min

        v_min = bfringe.pop()

        # Backward Expand
        for p in problem.predecessors(v_min):
            for state in ffringe:
                if problem.goal_test(state, v_min):
                    if c > v_min.cost() + state.cost():
                        c = v_min.cost() + state.cost()
                        current_solution = SolutionNode(state, v_min)
            if p not in bclosed or p.cost() < bclosed[p]:
                bfringe.push(p)
                bclosed[p] = p.cost()

        yield v_min

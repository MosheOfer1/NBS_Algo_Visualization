"""
This module contains the data_structures used in py_search. In particular, it
contains the the :class:`Problem` class, which is used to represent the
different search problems, and the :class:`AnnotatedProblem` class, which wraps
around a specific problem and keeps track of the number of core method calls.

At a lower level this module also contains the :class:`Node` class, which is
used to represent a node in the search space.

Finally, the module contains the :class:`Fringe` class, and its instantiations
(:class:`FIFOQueue`, :class:`LIFOQueue`, and :class:`PrioritySet`). A Fringe is
used to structure the way a search space is explored.
"""
from random import choice
from bisect import insort


class Problem(object):
    """
    The basic problem to solve. The main functions that must be defined include
    successors and goal_test. Some search techniques also require the
    random_successor and predecessors methods to be implemented.
    """

    def __init__(self, initial, goal=None, initial_cost=0, extra=None):
        self.initial = Node(initial, None, None, initial_cost, extra=extra)
        self.goal = GoalNode(goal)

    def node_value(self, node):
        """
        Returns the the value of the current node. This is the value being
        minimized by the search. By default the cost is used, but this
        function can be overloaded to include a heuristic.
        """
        return node.cost()

    def predecessors(self, node):
        """
        An iterator that yields all of the predecessors of the current goal.
        """
        raise NotImplementedError("No predecessors function implemented")

    def successors(self, node):
        """
        An iterator that yields all of the successors of the current node.
        """
        raise NotImplementedError("No successors function implemented")

    def random_successor(self, node):
        """
        This method should return a single successor node. This is used
        by some of the search techniques. By default, this just computes all of
        the successors and randomly samples one. This default approach is not
        very efficient, but this funciton can be overridden to generate a
        single successor more efficiently.
        """
        return choice([s for s in self.successors(node)])

    def random_node(self):
        """
        This method returns a random node in the search space. This
        is used by some of the local search / optimization techniques to
        randomly restart search.
        """
        raise NotImplementedError("No random node implemented!")

    def goal_test(self, state_node, goal_node=None):
        """
        Returns true if a goal state is found. This is typically not used by
        the local search / optimization techniques, but some of them use the
        goal test to determine if the search should terminate early. By
        default, this checks if the state equals the goal.
        """
        if goal_node is None:
            goal_node = self.goal
        return state_node == goal_node


class Node(object):
    """
    A class to represent a node in the search. This node stores state
    information, path to the state, cost of the node, depth of the node, and
    any extra information.

    :param state: the state at this node
    :type state: object for tree search and hashable object for graph search
    :param parent: the node from which the current node was generated
    :type parent: :class:`Node`
    :param action: the action performed to transition from parent to current.
    :type action: typically a string, but can be any object
    :param cost: the cost of reaching the current node
    :type cost: float
    :param extra: extra information to store in this node, typically used to
                  store non-hashable information about the state.
    :type extra: object
    """

    def __init__(self, state, parent=None, action=None, node_cost=0,
                 extra=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.node_cost = node_cost
        self.extra = extra

        if parent is None:
            self.node_depth = 0
        else:
            self.node_depth = parent.depth() + 1

    def depth(self):
        """
        Returns the depth of the current node.
        """
        return self.node_depth

    def cost(self):
        """
        Returns the cost of the current node.
        """
        return self.node_cost

    def path(self):
        """
        Returns a path (tuple of actions) from the initial to current node.
        """
        actions = []
        current = self
        while current.parent:
            actions.append(current.action)
            current = current.parent
        actions.reverse()
        return tuple(actions)

    def __str__(self):
        return str(self.state)

    def __repr__(self):
        return " <- (%s) " % repr(self.state)

    def __hash__(self):
        return hash(self.state)

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.cost() < other.cost()


class GoalNode(Node):
    """
    Used to represent goals in the backwards portion of the search.
    """

    def path(self):
        """
        Returns a path (tuple of actions) from the initial to current node.

        Similar to Node's path function, but returns the path in the opposite
        order because the goal nodes branch out from the goal (not the start
        state).
        """
        actions = []
        current = self
        while current.parent:
            actions.append(current.action)
            current = current.parent
        return tuple(actions)


class SolutionNode(object):
    """
    A Node class that joins a state (:class:`Node`) and a goal
    (:class:`GoalNode`) in bidirectional search, so that it can be returned and
    the used like other :class:`Node`. In particular it provides an isomorphic
    interface for querying depth, cost, and path.

    The state, parent, action, node_cost, and extra attributes have been
    removed because they are not well defined for a join. The key issue here is
    that the state and goal nodes might not be specified in the same terms. For
    example, goals may be partial states and goal_test might return True when
    the state_node satisfies the goal_node (not when they are strictly equal).

    Thus, to generate the actual state represented by the solution node, the
    returned path needs to be executed from the initial state, which is outside
    the scope of this library since it has no knowledge of how to execute paths
    (it just generates them using the user specified successor/predecessor
    functions).
    """

    def __init__(self, state, goal):
        self.state_node = state
        self.goal_node = goal

    def depth(self):
        return self.state_node.depth() + self.goal_node.depth()

    def cost(self):
        return self.state_node.cost() + self.goal_node.cost()

    def path(self):
        return self.state_node.path() + self.goal_node.path()

    def __str__(self):
        return "StateNode={%s}, GoalNode={%s}" % (self.state_node,
                                                  self.goal_node)

    def __repr__(self):
        return "SolutionNode(%s, %s)" % (repr(self.state_node),
                                         repr(self.goal_node))

    def __hash__(self):
        return hash((self.state_node.state, self.goal_node.state))

    def __eq__(self, other):
        return (isinstance(other, SolutionNode) and
                self.state_node == other.state_node and
                self.goal_node == other.goal_node)

    def __ne__(self, other):
        return not self.__eq__(other)


class Fringe(object):
    """
    A template for a fringe class. Used to control the strategy of different
    search approaches.
    """

    def push(self, node):
        """
        Adds one node to the collection.
        """
        raise NotImplementedError("No push method")

    def extend(self, nodes):
        """
        Given an iterator (`nodes`) adds all the nodes to the collection.
        """
        for n in nodes:
            self.push(n)

    def pop(self):
        """
        Pops a node off the collection.
        """
        raise NotImplementedError("No pop method")

    def __len__(self):
        """
        Returns the length of the fringe.
        """
        raise NotImplementedError("No __len__ method")

    def __iter__(self):
        """
        Returns iterator that yields the elements in the order they would be
        popped.
        """
        raise NotImplementedError("No __iter__ method")


class PriorityQueue(Fringe):
    """
    A priority queue that sorts elements by their value. Always returns the
    minimum value item.  A :class:`PriorityQueue` accepts a node_value
    function, a cost_limit (nodes with a value greater than this limit will not
    be added) and a max_length parameter. If adding an item ever causes the
    size to exceed the max_length then the worst nodes are removed until the
    list is equal to max_length.

    >>> pq = PriorityQueue(node_value=lambda x: x, max_length=3)
    >>> pq.push(6)
    >>> pq.push(0)
    >>> pq.push(2)
    >>> pq.push(6)
    >>> pq.push(7)
    >>> len(pq)
    3
    >>> list(pq)
    [0, 2, 6]
    >>> pq.update_cost_limit(5)
    >>> len(pq)
    2
    >>> pq.peek()
    0
    >>> pq.peek_value()
    0
    >>> print(pq.pop())
    0
    >>> pq.peek()
    2
    >>> pq.peek_value()
    2
    >>> print(pq.pop())
    2
    >>> len(pq)
    0

    :param node_value: The node evaluation function (defaults to
        ``lambda x: x.cost()``)
    :type node_value: a function with one parameter for node
    :param cost_limit: the maximum value for elements in the set, if an item
        exceeds this limit then it will not be added (defaults to
        ``float('inf'))``
    :type cost_limit: float
    :param max_length: The maximum length of the list (defaults to
        ``float('inf')``
    :type max_length: int or ``float('inf')``
    """

    def __init__(self, node_value=lambda x: x, cost_limit=float('inf'),
                 max_length=float('inf')):
        self.nodes = []
        self.max_length = max_length
        self.cost_limit = cost_limit
        self.node_value = node_value

    def clear(self):
        """
        Empties the list.
        """
        self.nodes = []

    def peek(self):
        """
        Returns the best node.
        """
        return self.nodes[-1][1]

    def peek_value(self):
        """
        Returns the value of the best node.
        """
        return -self.nodes[-1][0]

    def update_cost_limit(self, cost_limit):
        """
        Updates the cost limit and removes any nodes that violate the new
        limit.
        """
        self.cost_limit = cost_limit
        for i in range(len(self.nodes)):
            if self.nodes[i][0] >= -self.cost_limit:
                self.nodes = self.nodes[i:]
                break

    def push(self, node):
        """
        Push a node into the priority queue. If the node exceeds the cost limit
        then it is not added. If the max_length is exceeded by
        adding the node, then the worst node is discarded from the set.
        """
        value = self.node_value(node)

        if value > self.cost_limit:
            return

        insort(self.nodes, (-value, node))

        if len(self.nodes) > self.max_length:
            val, node = self.nodes.pop(0)

    def pop(self):
        """
        Pop the best value from the priority queue.
        """
        val, node = self.nodes.pop()
        return node

    def __len__(self):
        return len(self.nodes)

    def __iter__(self):
        for v, n in reversed(self.nodes):
            yield n

    def __str__(self) -> str:
        return str([n for n in self])


class NbsDataStructure(Fringe):
    """
    A data structure for Near-Optimal Bidirectional Search (NBS) that manages
    nodes in two priority queues: one for nodes waiting to be explored and one
    for nodes ready to be explored. Nodes in the 'waiting' queue are sorted by
    their heuristic value, and nodes in the 'ready' queue are sorted by their
    cost.

    >>> nbs = NbsDataStructure(node_value_waiting=lambda x: x, node_value_ready=lambda x: x)
    >>> nbs.push(6)
    >>> nbs.push(2)
    >>> nbs.push(0)
    >>> len(nbs)
    3
    >>> nbs.peek_waiting_value()
    0
    >>> nbs.move_from_waiting_to_ready()
    >>> nbs.peek_ready()
    0
    >>> len(nbs)
    3
    >>> print(nbs.pop())
    0
    >>> len(nbs)
    2
    >>> nbs.prepare_best(nbs)
    True

    :param node_value_waiting: The node evaluation function for the waiting
        queue.
    :type node_value_waiting: a function with one parameter for node
    :param node_value_ready: The node evaluation function for the ready queue.
    :type node_value_ready: a function with one parameter for node
    """
    def __init__(self, node_value_waiting, node_value_ready):
        self.c_lb = 0
        # Sorted low to high by the f values
        self.waiting = PriorityQueue(node_value=node_value_waiting)
        # Sorted low to high by the cost values
        self.ready = PriorityQueue(node_value=node_value_ready)

    def push(self, node):
        self.waiting.push(node)

    def pop(self):
        return self.ready.pop()

    def peek(self):
        return self.ready.peek()

    def peek_waiting(self):
        return self.waiting.peek()

    def peek_waiting_value(self):
        try:
            return self.waiting.peek_value()
        except IndexError:
            return float("inf")

    def peek_ready(self):
        try:
            return self.ready.peek_value()
        except IndexError:
            return float("inf")

    def move_from_waiting_to_ready(self):
        node = self.waiting.pop()
        self.ready.push(node)

    def prepare_best(self, other_fringe):
        messages = []
        while self.peek_waiting_value() < self.c_lb:
            messages.append(
                f"  Entered: {self.peek_waiting()} to the front-ready with value: {self.peek_waiting_value()}"
            )
            self.move_from_waiting_to_ready()

        while other_fringe.peek_waiting_value() < other_fringe.c_lb:
            messages.append(
                f"  Entered: {other_fringe.peek_waiting()} to the back-ready with value: {other_fringe.peek_waiting_value()}"
            )
            other_fringe.move_from_waiting_to_ready()

        while True:
            if len(self) <= 0 or len(other_fringe) <= 0:
                return False, "Failed"

            if self.peek_ready() + other_fringe.peek_ready() <= self.c_lb:
                messages.append(f"\n  C-lb: {self.c_lb}")
                messages.append(f"`  Front Open - Waiting:\n    {self.waiting}")
                messages.append(f"`  Front Open - Ready:\n    {self.ready}")
                messages.append(f"`\n  Back Open - Waiting:\n    {other_fringe.waiting}")
                messages.append(f"`  Back Open - Ready:\n    {other_fringe.ready}\n")
                return True, messages

            moved = False
            if self.peek_waiting_value() <= self.c_lb:
                messages.append(f"Action: Moving {self.peek_waiting()} from the front waiting to the ready")
                self.move_from_waiting_to_ready()
                moved = True

            if other_fringe.peek_waiting_value() <= other_fringe.c_lb:
                messages.append(f"Action: Moving {other_fringe.peek_waiting()} from the back waiting to the ready")
                other_fringe.move_from_waiting_to_ready()
                moved = True

            if not moved:
                self.c_lb = other_fringe.c_lb = min(self.peek_waiting_value(),
                                                    other_fringe.peek_waiting_value(),
                                                    self.peek_ready() + other_fringe.peek_ready())
                messages.append(f"Action: Raising C-lb to: {self.c_lb}")
                if self.c_lb == float("inf"):
                    return False, "Failed"

    def __len__(self):
        return len(self.waiting) + len(self.ready)

    def __iter__(self):
        for node in self.ready:
            yield node
        for node in self.waiting:
            yield node

    def __str__(self) -> str:
        return str([n for n in self])

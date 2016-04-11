from .agents import *
from random import randint


class AgentXTypeTwoClass(Agent):
    def __init__(self, x=2, y=2):
        Agent.__init__(self)

        ##
        # Personalize the identifier of this class.
        # Will be used instead of the class name
        # in neighbours info
        self.name = 'AgentXTwo'

        # Actions of the agent
        self.actions = {
            0: "GoNorth",
            1: "GoWest",
            2: "GoSouth",
            3: "GoEast",
            4: "NoOp"
        }

        # Remember wall
        self.walls = []

        # Visited floor
        self.visited_floor = []

        # Search tree
        self.search_tree = [((0, 0), 4)]

        # Visited floor by an adversary
        self.visited_floor_adv = []

        # Current action
        self.current_action = 4

        # Current position
        self.position = (0, 0)

        # NoOp max execution
        self.no_op_max = 10

        def get_coord(action):
            """
                Retrieve the normal coordinates and the backtracked one

                Return:
                    - (tuple): The new position
            """
            if action == 0:
                return self.position[0], self.position[1] + 1
            elif action == 1:
                return self.position[0] - 1, self.position[1]
            elif action == 2:
                return self.position[0], self.position[1] - 1
            elif action == 3:
                return self.position[0] + 1, self.position[1]

        def define_action(neighbors, cloned_pos, near_agent_on_X, near_agent_on_y):
            """
                Retrieve the action to make. In first time the agent try to take open a new graph (or tree) branch,
                if this is not possible then it enter a previously visited branch

                Return:
                    (string): the action to make

            """

            for i in range(0, 5):
                if i < 4:
                    ##
                    # Control if a position is not a wall, an already visited floor
                    # and a visited position by an adversary

                    if (get_coord(i) not in self.walls \
                                and get_coord(i) not in self.visited_floor \
                                and get_coord(i) not in self.visited_floor_adv):
                        # New position
                        self.position = get_coord(i)

                        # New action
                        self.current_action = i

                        # Save in the history
                        self.visited_floor.insert(0, self.position)
                        self.search_tree.insert(0, (self.position, i))
                        return self.actions[i]
                # Backtracking
                else:
                    if self.search_tree:
                        (coord_x, coord_y), action = self.search_tree.pop(0)
                    else:
                        return 'NoOp'

                    # Calculate the backtrack action to make
                    action = (action + 2) % 4

                    # Backtrack position
                    self.position = get_coord(action)

                    # Backtrack action
                    self.current_action = action
                    return self.actions[action]

        def retrieve_most_near_agent(neighbors, on):
            """
                Retrieve the most near agent with the indication of the axis

                 Args:
                     neighbors (array)
                     on (string)

                 Return:
                     (tuple)
            """
            return min(
                [
                    (
                        (agent_id, agent_type), pos
                    )
                    for (agent_id, agent_type), pos in neighbors if agent_id != self.id and agent_type == self.name
                    ],
                # Select axis X if on is equal 'OnX', otherwise select axis Y
                key=lambda position: position[0] if on == 'OnX' else position[1]
            )

        def retrieve_clone(neighbors):
            """
                Retrieve the cloned agent

                Args:
                    neighbors (array)

                Return:
                    (tuple)
            """
            for (agent_id, agent_type), pos in neighbors:
                if agent_type == self.name and self.id != agent_id:
                    return (agent_id, agent_type), pos
            return None

        def retrieve_action(neighbors):
            """
                Retrieve an action to make

                Args:
                    neighbors (array)

                Return:
                    (string)
            """

            if neighbors:
                (near_agent_x_id, near_agent_x_type), near_agent_pos_x = retrieve_most_near_agent(neighbors, "OnX")
                (near_agent_y_id, near_agent_y_type), near_agent_pos_y = retrieve_most_near_agent(neighbors, "OnY")
                (cloned_id, cloned_type), cloned_pos = retrieve_clone(neighbors)
                return define_action(
                    neighbors,
                    cloned_pos,
                    near_agent_pos_x,
                    near_agent_pos_y
                )
            else:
                return 'NoOp'

        def make_action(status, bump, neighbors):
            """
                Select the action to execute

                Params:
                status (string): 'Dirty' or 'Clean'
                bump (string): 'Bump' or 'None'
                neighbors (list of tuples): [
                        ( (agent_id, agent_type), (r_x, r_y) ),
                        ...,
                        ...
                    ]

                Returns:
                     (string): one of these commands:
                                - 'Suck'
                                - 'GoNorth'
                                - 'GoSouth'
                                - 'GoWest'
                                - 'GoEast'
                                - 'NoOp' or 'Noop'
            """

            if self.position[0] == 0 and self.position[0] == 1 and self.search_tree:
                return 'NoOp'

            if bump == 'Bump':
                # Extract the position from the search tree 'cause it can't accessed anymore
                if self.search_tree:
                    self.search_tree.pop(0)

                self.walls.append(self.position)
                self.position = get_coord((self.current_action + 2) % 4)
                return retrieve_action(neighbors)
            else:
                # If the position is dirty, then suck
                if status == 'Dirty':
                    return 'Suck'
                else:
                    return retrieve_action(neighbors)

        def program(status, bump, neighbors):
            """Main function of the Agent.

            Params:
                status (string): 'Dirty' or 'Clean'
                bump (string): 'Bump' or 'None'
                neighbors (list of tuples): [
                        ( (agent_id, agent_type), (r_x, r_y) ),
                        ...,
                        ...
                    ]

            Returns:
                 (string): one of these commands:
                            - 'Suck'
                            - 'GoNorth'
                            - 'GoSouth'
                            - 'GoWest'
                            - 'GoEast'
                            - 'NoOp' or 'Noop'

            """

            # Save all the position visited by an other agent as personal visiting
            for (agent_id, agent_type), pos in neighbors:
                if agent_id != self.id:
                    self.visited_floor_adv.append((self.position[0] + pos[0], self.position[1] + pos[1]))

            return make_action(status, bump, neighbors)

        self.program = program

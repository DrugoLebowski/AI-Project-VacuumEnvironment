from .agents import *
import scipy.spatial.distance as ds

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

        def get_rel_coord(action):
            """
                Retrieve the relative coordinate of another agent

                Args:
                    action (int): The action to undertake

                Return:
                    tuple: Coordinate
            """
            if action == 0:
                return 0, 1
            elif action == 1:
                return -1, 0
            elif action == 2:
                return 0, -1
            elif action == 3:
                return 1, 0

        def negated_position(pos):
            """
                Retrieve the negated positions to undertake

                Args:
                    pos (tuple): Position of an agent

                Returns:
                    (list): The list of negated position
            """
            return [(pos[0] + 1, pos[1]), (pos[0], pos[1] + 1), (pos[0], pos[1] - 1), (pos[0] - 1, pos[1]), pos]

        def calculate_negated_position(neighbors):
            """
                Calculate the action to undertake in base of position of the other agent:
                in particular, the move is encouraged to the other agent (not the clone)
                Args:
                    neighbors (list): The list of all the neighbors
                Return:
                    (integer)
            """
            neg_pos = []
            for (agent_id, agent_type), pos in neighbors:
                if self.id != agent_id:
                    ##
                    # Calculate the negated position if and only if the agent type is different respect this agent type,
                    # and if and only if the agent position is different from the clone relative position
                    if self.name != agent_type or (self.name == agent_type and pos[0] != 0 and pos[1] != 0):
                        neg_pos += negated_position(pos)
            return neg_pos

        def distance_from_other_agents(neighbors):
            """
                Calculate the distance from other agents and return the list with the preferred action to make

                Args:
                    neighbors (list): The complete list of the agent

                Return:
                    (list): A list of tuple with a structure like [(distance, [action, ...]), ...]
            """
            distances = []
            for (agent_id, agent_type), pos in neighbors:
                if self.id != agent_id:
                    dis_from_other_agent = ds.euclidean(self.position, (self.position[0] + pos[0], self.position[1] + pos[1]))
                    actions = []
                    # If the type of the agent is not equal from this, then calculate the distance
                    if agent_type != self.name:
                        if pos[0] < 0:
                            actions.append(1)  # GoWest
                        elif pos[0] > 0:
                            actions.append(3)  # GoEast
                        elif pos[1] < 0:
                            actions.append(2)  # GoSouth
                        elif pos[1] > 0:
                            actions.append(0)  # GoNorth
                    # Otherwise, we are in the case when the agents are of the same type,
                    # but one is the clone of the other
                    else:
                        if pos[0] < 0:
                            actions.append(3)  # GoWest
                        elif pos[0] > 0:
                            actions.append(1)  # GoEast
                        elif pos[1] < 0:
                            actions.append(0)  # GoSouth
                        elif pos[1] > 0:
                            actions.append(2)  # GoNorth
                        # Enter this branch iff the agent and the clone are in the same position
                        else:
                            actions.append(random.randint(0, 3))
                    distances.append((dis_from_other_agent, actions))

            def sorter(dis1, dis2):
                if dis1[0] >= dis2[0]:
                    return -1
                else:
                    return 1

            distances.sort(sorter)
            return distances

        def define_action(neighbors):
            """
                Retrieve the action to make. In first time the agent try to take open a new graph (or tree) branch,
                if this is not possible then it enter a previously visited branch

                Args:
                    neighbors (list): The list of the neighbors

                Return:
                    (string): the action to make
            """

            def decide(action, neg_pos):
                """
                    Control if the action is possible

                    Args:
                        action (int): The action to undertake
                        neg_pos (list): The position in the map that an agent cannot undertake

                    Return:
                        (string) The action to make
                        (None) If is not possible
                """
                coord = get_coord(action)
                if coord not in self.walls and coord not in self.visited_floor \
                        and coord not in self.visited_floor_adv and get_rel_coord(action) not in neg_pos:
                    # New position
                    self.position = coord

                    # New action
                    self.current_action = action

                    # Save in the history
                    self.visited_floor.insert(0, self.position)
                    self.search_tree.insert(0, (self.position, action))
                    return self.actions[action]
                else:
                    return None

            neg_pos = calculate_negated_position(neighbors)
            dis_other_agents = distance_from_other_agents(neighbors)
            for dis, actions in dis_other_agents:
                # Firstly try the actions calculated with heuristic
                for i in actions:
                    action = decide(i, neg_pos)
                    if action:
                        return action

            # In this second step, the agent try to take one of the four action (if it's possible)
            for i in range(0, 4):
                action = decide(i, neg_pos)
                if action:
                    return action
            ##
            # ===========================
            #        Backtracking
            # ===========================
            if not self.search_tree:
                return 'NoOp'

            # Retrieve the position and action
            (coord_x, coord_y), action = self.search_tree[0]

            # Calculate the backtrack action to make
            action = (action + 2) % 4

            if get_coord(action) not in neg_pos:
                # Remove the first element of search tree
                self.search_tree.pop(0)

                # Backtrack position
                self.position = get_coord(action)

                # Backtrack action
                self.current_action = action
                return self.actions[action]
            # Stop backtracking
            else:
                return 'NoOp'

        def retrieve_action(neighbors):
            """
                Retrieve an action to make

                Args:
                    neighbors (array)

                Return:
                    (string)
            """

            if neighbors:
                return define_action(neighbors)
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

            if not self.search_tree:
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

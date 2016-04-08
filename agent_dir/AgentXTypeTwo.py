from .agents import *
from random import randint


class AgentXTypeTwoClass(Agent):
    def __init__(self, x=2, y=2):
        Agent.__init__(self)

        ##
        # Personalize the identifier of this class.
        # Will be used instead of the class name
        # in neighbours info
        self.name = 'AgentX'

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

        # Current action
        self.current_action = 4

        # Position
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
                return self.position[0] - 1, self.position[1]
            elif action == 1:
                return self.position[0], self.position[1] - 1
            elif action == 2:
                return self.position[0] + 1, self.position[1]
            elif action == 3:
                return self.position[0], self.position[1] + 1

        def define_action():
            """
                Retrieve the action to make. In first time the agent try to take open a new graph (or tree) branch,
                if this is not possible then it enter a previously visited branch

                Return:
                    (string): the action to make

            """

            temp_wrong_action = []
            for i in range(0, 8):
                if i < 4:
                    if get_coord(i) not in self.walls and get_coord(i) not in self.visited_floor:
                        self.position = get_coord(i)
                        self.current_action = i
                        return self.actions[i]
                    elif get_coord(i) in self.walls:
                        temp_wrong_action.append(i)
                # Random
                else:
                    # Calculate the random action to make
                    action = randint(0, 5) % 5
                    coord = get_coord(action)
                    if action != 4:
                        if coord not in self.walls and coord:
                            self.position = coord
                            self.current_action = action
                            return self.actions[action]
                        else:
                            temp_wrong_action.append(action)
                    else:
                        self.no_op_max = self.no_op_max - 1
                        return 'NoOp'

        def retrieve_most_near_agent(neighbors):
            """
                Retrieve the most near agent

                 Args:
                     neighbors

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
                key=lambda position: position[1]  # select position as filter
            )

        def retrieve_action(neighbors):
            """
                Retrieve an action to make

                Args:
                    neighbors (array)

                Return:
                    (string)
            """

            if neighbors:
                (agent_id, agent_type), pos = retrieve_most_near_agent(neighbors)
                return define_action(pos)
            else:
                return define_action()

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
            if self.no_op_max == 0:
                return 'NoOp'

            if bump == 'Bump':
                self.walls.append(self.position)
                self.position = get_coord((self.current_action + 2) % 4)
                return define_action()
            else:
                if status == 'Dirty':
                    return 'Suck'
                else:
                    return define_action()

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
                    self.visited_floor.append((self.position[0] + pos[0], self.position[1] + pos[1]))
                else:
                    self.visited_floor.append(self.position)

            return make_action(status, bump, neighbors)

        self.program = program

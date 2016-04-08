from .agents import *
from random import randint


# Agent with
class AgentXTypeOneClass(Agent):
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

        # Last <x> position
        self.history_positions = []

        # Current action
        self.current_action = 4

        # Last action
        self.last_action = -1

        # Current position in map
        self.position = (0, 0)

        # Last action
        self.last_position = (0, 0)

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
                key = lambda position: position[0] if on == 'OnX' else position[1]
            )

        def decide_action(near_agent_on_x=None, near_agent_on_y=None):
            """
                Retrieve the action to make. In first time the agent try to take open a new graph (or tree) branch,
                if this is not possible then it enter a previously visited branch

                Args:
                    near_agent_on_x (tuple): The most near agent in the map respect the X axis
                    near_agent_on_y (tuple): The most near agent in the map respect the Y axis

                Return:
                    (string): the action to make
            """

            # Default action if no alternative is retrieved
            for i in range(0, 4):
                coord = get_coord(i)
                if coord not in self.history_positions:
                    self.last_position, self.position = self.position, coord # Updating of position
                    self.last_action, self.current_action = self.current_action, i # Updating of action
                    return self.actions[i]

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
                (agent_id_on_x, agent_type_on_y), near_agent_on_x = retrieve_most_near_agent(neighbors, 'OnX')
                (agent_id_on_x, agent_type_on_y), near_agent_on_y = retrieve_most_near_agent(neighbors, 'OnY')
                return decide_action(near_agent_on_x, near_agent_on_y)
            else:
                return decide_action()

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
                self.history_positions.insert(0, self.position)
                self.current_action, self.last_action = self.last_action, -1
                print (self.current_action, self.last_action)
                self.position, self.last_position = self.last_position, self.position
                return retrieve_action(neighbors)
            else:
                del self.history_positions[:]
                self.history_positions.insert(0, self.last_position)
                print(self.history_positions, 'Moved')
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

            return make_action(status, bump, neighbors)

        self.program = program

from random import randint
from .agents import *

class AgentXTypeOneClass(Agent):
    def __init__(self, x=2, y=2):
        Agent.__init__(self)

        ##
        # Personalize the identifier of this class.
        # Will be used instead of the class name
        # in neighbours info
        self.name = 'AgentXTypeOne'

        # Actions of the agent
        self.actions = {
            0: "GoNorth",
            1: "GoWest",
            2: "GoSouth",
            3: "GoEast",
            4: "NoOp"
        }

        # Last 7 position
        self.history_positions = [(0, 0)]

        # Current action
        self.current_action = 4

        # Last action
        self.last_action = -1

        # Current position in map
        self.position = (0, 0)

        # Last action
        self.last_position = (0, 0)

        # NoOp max execution
        self.empty_position_max = 1

        # If the agent have sucked or not in the last iteration
        self.sucked = False

        def get_coord(action):
            """
                Retrieve the normal coordinates and the backtracked one

                Return:
                    - (tuple): The new position
            """
            if action == 0:    # GoNorth
                return self.position[0], self.position[1] + 1
            elif action == 1:  # GoWest
                return self.position[0] - 1, self.position[1]
            elif action == 2:  # GoSouth
                return self.position[0], self.position[1] - 1
            elif action == 3:  # GoEast
                return self.position[0] + 1, self.position[1]

        def get_rel_coord(action):
            """
                Retrieve the normal coordinates and the backtracked one

                Return:
                    - (tuple): The new position
            """
            if action == 0:    # GoNorth
                return 0, 1
            elif action == 1:  # GoWest
                return -1, 0
            elif action == 2:  # GoSouth
                return 0, -1
            elif action == 3:  # GoEast
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

        def decide_action(neighbors):
            """
                Retrieve the action to make. In first time the agent try to take open a new graph (or tree) branch,
                if this is not possible then it enter a previously visited branch

                Args:
                    neighbors (list): The list of the neighbors

                Return:
                    (string): the action to undertake
            """

            # Default action if no alternative is retrieved
            index = randint(0, 3)  # Action
            coord = get_coord(index)  # Coordinate of path
            rel_coord = get_rel_coord(index)  # Relative coord
            neg_pos = calculate_negated_position(neighbors)  # Negated positions
            if (coord not in self.history_positions and rel_coord not in neg_pos) \
                    or rel_coord not in neg_pos:

                # Updating the position
                self.last_position, self.position = self.position, coord

                # Insert the position in the history
                self.history_positions.insert(0, self.position)

                # Updating the action
                self.last_action, self.current_action = self.current_action, index

                # Set sucked as False because the agent have bumped on the wall, or entered in a position already
                # cleaned or have encountered another agent
                self.sucked = False
                return self.actions[index]

        def program(status, bump, neighbors):
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

            # If the agent have
            if self.empty_position_max == 0:
                return 'NoOp'

            # Limit the memory
            if len(self.history_positions) > 7:
                self.history_positions.pop()

            # If the position is Dirty, then suck
            if status == "Dirty":
                self.empty_position_max += 6
                self.sucked = True
                return 'Suck'

            # Otherwise is happened another thing to agent, like bump or the entering of a cleaned position
            self.empty_position_max -= 1
            if bump == 'Bump':

                # Restoring of the old action
                self.current_action, self.last_action = self.last_action, -1

                # Restoring of the old position
                self.position, self.last_position = self.last_position, self.position
                return decide_action(neighbors if neighbors else [])
            elif not self.sucked:
                return decide_action(neighbors if neighbors else [])

            # Moving on the direction
            self.sucked = False
            return self.actions[self.current_action]

        self.program = program

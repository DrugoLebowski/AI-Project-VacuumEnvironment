from random import randint

from .agents import *
import numpy as np
import math
import scipy.spatial.distance as ds


class AgentXTypeOneClass(Agent):
    def __init__(self, x=2, y=2):
        Agent.__init__(self)

        ##
        # Personalize the identifier of this class.
        # Will be used instead of the class name
        # in neighbours info
        self.name = 'AgentXOne'

        # Actions of the agent
        self.actions = {
            0: "GoNorth",
            1: "GoWest",
            2: "GoSouth",
            3: "GoEast",
            4: "NoOp"
        }

        # Last <x> position
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
                Retrieve the normal coordinates and the backtracked one

                Return:
                    - (tuple): The new position
            """
            if action == 0:
                return 0, 1
            elif action == 1:
                return -1, 0
            elif action == 2:
                return 0, -1
            elif action == 3:
                return 1, 0

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

        def negated_position(pos):
            """
                Retrieve the negated positions to undertake

                Args:
                    pos (tuple): Position of an agent

                Returns:
                    (list): The list of negated position
            """
            return [(pos[0] + 1, pos[1]), (pos[0], pos[1] + 1), (pos[0], pos[1] - 1), (pos[0] - 1, pos[1]), pos]

        def calculate_negated_position(cloned_agent_pos, agent_on_x_pos=None, agent_on_y_pos=None):
            """
                Calculate the action to undertake in base of position of the other agent:
                in particular, the move is encouraged to the other agent (not the clone)

                Args:
                    cloned_agent_pos (tuple)
                    agent_on_x_pos (tuple)
                    agent_on_y_pos (tuple)

                Return:
                    (integer)
            """
            neg_pos = []
            neg_pos += negated_position(cloned_agent_pos)
            if agent_on_x_pos:
                neg_pos += negated_position(agent_on_x_pos)
            if agent_on_y_pos:
                neg_pos += negated_position(agent_on_y_pos)

            return negated_position(cloned_agent_pos)

        def decide_action(near_agent_on_x=None, near_agent_on_y=None, cloned_pos=None):
            """
                Retrieve the action to make. In first time the agent try to take open a new graph (or tree) branch,
                if this is not possible then it enter a previously visited branch

                Args:
                    near_agent_on_x (tuple): The most near agent in the map respect the X axis
                    near_agent_on_y (tuple): The most near agent in the map respect the Y axis
                    cloned_pos (tuple): Position of the cloned agent

                Return:
                    (string): the action to undertake
            """

            # Default action if no alternative is retrieved
            index = randint(0, 3)  # Action
            coord = get_coord(index)  # Coordinate of path
            rel_coord = get_rel_coord(index)  # Relative coord
            neg_pos = calculate_negated_position(cloned_pos, near_agent_on_x, near_agent_on_y)  # Negated positions
            if (coord not in self.history_positions \
                    and rel_coord not in neg_pos) or rel_coord not in neg_pos:

                # Updating the position
                self.last_position, self.position = self.position, coord
                self.history_positions.insert(0, self.position)

                # Updating the action
                self.last_action, self.current_action = self.current_action, index
                return self.actions[index]
            return 'NoOp'

        def retrieve_clone(neighbors):
            """
                Retrieve the cloned agent

                Args:
                    neighbors (array)

                Return:
                    (tuple)
            """
            for (agent_id, agent_type), pos in neighbors:
                if agent_type == self.name and agent_id != self.id:
                    return (agent_id, agent_type), pos
            return None

        def retrieve_action(neighbors=None):
            """
                Retrieve an action to undertake

                Args:
                    neighbors (array)

                Return:
                    (string)
            """

            if not neighbors:
                return decide_action()
            else:
                # Retrieve of the most near agents
                (agent_id_on_x, agent_type_on_x), near_agent_on_x = retrieve_most_near_agent(neighbors, 'OnX')
                (agent_id_on_y, agent_type_on_y), near_agent_on_y = retrieve_most_near_agent(neighbors, 'OnY')

                # Retrieve the cloned agent
                (cloned_id, cloned_type), cloned_pos = retrieve_clone(neighbors)

                return decide_action(
                    near_agent_on_x if agent_type_on_x != cloned_type else None,
                    near_agent_on_y if agent_type_on_y != cloned_type else None,
                    cloned_pos
                )

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

            if len(self.history_positions) > 10:
                self.history_positions.pop()

            if bump == 'Bump':
                self.current_action, self.last_action = self.last_action, -1
                self.position, self.last_position = self.last_position, self.position
                return retrieve_action(neighbors)
            else:
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

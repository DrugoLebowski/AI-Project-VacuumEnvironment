from .agents import *
import numpy as np
import math


# Agent with
class AgentXTypeThreeClass(Agent):
    def __init__(self, x=2, y=2):
        Agent.__init__(self)

        ##
        # Personalize the identifier of this class.
        # Will be used instead of the class name
        # in neighbours info
        self.name = 'AgentXThree'

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
        self.current_action = 0

        # Last action
        self.last_action = -1

        # Base position for exploration
        self.base_position = (0, 0)

        # Old base position
        self.old_base_position = None

        # Current position in map
        self.position = (0, 0)

        # The maximum rebase that can fail (Fail means that the agent rebase in a field already cleaned)
        self.empty_base_max = 50

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
                key=lambda position: position[0] if on == 'OnX' else position[1]
            )

        def calculate_boost(cloned_agent_pos, agent_on_x_pos=None, agent_on_y_pos=None):
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


            '''
            boost = math.sqrt((self.position[0] - cloned_agent_pos[0]) ** 2 +
                              (self.position[1] - cloned_agent_pos[1]) ** 2)



            print(boost)
            if agent_on_x_pos:
                boost += math.sqrt((self.position[0] - agent_on_x_pos[0]) ** 2 +
                                   (self.position[1] - agent_on_x_pos[1]) ** 2) * 0.8

            if agent_on_y_pos:
                boost += math.sqrt((self.position[0] - agent_on_y_pos[0]) ** 2 +
                                   (self.position[1] - agent_on_y_pos[1]) ** 2) * 0.8
            '''
            return math.floor(boost)

        def rebase_agent(near_agent_on_x=None, near_agent_on_y=None, cloned_pos=None):
            """
                Calculate a new base position of the agent when it has explored all the near position

                Args:
                    near_agent_on_x (tuple): The most near agent in the map respect the X axis
                    near_agent_on_y (tuple): The most near agent in the map respect the Y axis
                    cloned_pos (tuple): Position of the cloned agent

                Return:
                    (string): the action to undertake
            """

            # Delete the history for the new rebase
            del self.history_positions[:]

            for i in range(0, 4):
                action = calculate_boost(cloned_pos, near_agent_on_x, near_agent_on_y)
                coord = get_coord(action)
                print(coord)
                if coord not in self.history_positions:
                    # Updating the position
                    self.base_position, self.old_base_position = coord, self.base_position
                    self.position = coord

                    # Updating the action
                    self.current_action = action

                    self.history_positions.insert(0, self.old_base_position)
                    print(self.base_position, self.old_base_position, self.history_positions)
                    return self.actions[int(action)]

            return 'NoOp'

        def move_agent():
            """
                Try to explore the near field of the current base

                Return:
                    (string): The action to undertake
            """

            # Means that agent is exploring a near position respect the base
            if self.position[0] != self.base_position[0] or self.position[1] != self.base_position[1]:
                self.current_action = (self.current_action + 2) % 4
                self.position = get_coord(self.current_action)
                return self.actions[self.current_action]
            # Otherwise the agent is currently positioned in the base
            else:
                for i in range(0, 4):
                    coord = get_coord(i)
                    if coord not in self.history_positions:
                        self.position = coord
                        self.current_action = i
                        self.history_positions.insert(0, self.position)
                        return self.actions[self.current_action]

        def retrieve_clone(neighbors):
            """
                Retrieve the cloned agent

                Args:
                    neighbors (array)

                Return:
                    (tuple)
            """
            for (agent_id, agent_type), pos in neighbors:
                if agent_type == self.name:
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
                return move_agent()
            else:
                # Retrieve of the most near agents
                (agent_id_on_x, agent_type_on_x), near_agent_on_x = retrieve_most_near_agent(neighbors, 'OnX')
                (agent_id_on_y, agent_type_on_y), near_agent_on_y = retrieve_most_near_agent(neighbors, 'OnY')

                # Retrieve the cloned agent
                (cloned_id, cloned_type), cloned_pos = retrieve_clone(neighbors)

                return rebase_agent(
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

            if self.empty_base_max == 0:
                return 'NoOp'

            if status == 'Bump':
                self.current_action = (self.current_action + 2) % 4
                self.position = get_coord(self.current_action)

                # If the exploration of the near field is complete, then rebase the agent to new position
                if len(self.history_positions) == 4:
                    if self.position == self.base_position:
                        return retrieve_action(neighbors)
                    else:
                        return retrieve_action()
                else:
                    # Otherwise continue the exploration of the near fields
                    return retrieve_action()
            else:
                if status == 'Dirty':
                    return 'Suck'
                else:
                    # If the exploration of the near field is complete, then rebase the agent to new position
                    if len(self.history_positions) == 4:
                        if self.position == self.base_position:
                            return retrieve_action(neighbors)
                        else:
                            return retrieve_action()
                    else:
                        # Otherwise continue the exploration of the near fields
                        return retrieve_action()

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
            action = make_action(status, bump, neighbors)
            return action

        self.program = program

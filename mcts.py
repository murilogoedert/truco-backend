import numpy as np
from collections import defaultdict
from abc import ABC, abstractmethod
import session

class MonteCarloTreeSearchNode(ABC):

    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []

    @property
    @abstractmethod
    def untried_actions(self):
        pass

    @property
    @abstractmethod
    def q(self):
        pass

    @property
    @abstractmethod
    def n(self):
        pass

    @abstractmethod
    def expand(self):
        pass

    @abstractmethod
    def is_terminal_node(self):
        pass

    @abstractmethod
    def rollout(self):
        pass

    @abstractmethod
    def backpropagate(self, reward):
        pass

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def best_child(self, c_param=1.4):
        choices_weights = [
            (c.q / c.n) + c_param * np.sqrt((2 * np.log(self.n) / c.n))
            for c in self.children
        ]
        return self.children[np.argmax(choices_weights)]

    def rollout_policy(self, possible_moves):
        return possible_moves[np.random.randint(len(possible_moves))]



class MonteCarloTreeSearchNode(MonteCarloTreeSearchNode):
    def __init__(self, state, parent=None):
        super().__init__(state, parent)
        self._number_of_visits = 0.
        self._results = defaultdict(int)
        self._untried_actions = None

    @property
    def untried_actions(self):
        if self._untried_actions is None:
            self._untried_actions = self.state.getLegalActions()
        return self._untried_actions

    @property
    def q(self):
        wins = self._results[self.state.matchPlayer]
        loses = self._results[-1 * self.state.matchPlayer]
        return wins - loses

    @property
    def n(self):
        return self._number_of_visits

    def expand(self):
        action = self.untried_actions.pop()
        next_state = self.state.doAction(action)
        child_node = MonteCarloTreeSearchNode(
            next_state, parent=self
        )
        self.children.append(child_node)
        return child_node

    def is_terminal_node(self):
        return self.state.isGameOver()

    def rollout(self):
        current_rollout_state = self.state
        while not current_rollout_state.isGameOver():
            possible_moves = current_rollout_state.getLegalActions()
            action = self.rollout_policy(possible_moves)
            current_rollout_state = current_rollout_state.doAction(action)
        return current_rollout_state.game_result

    def backpropagate(self, result):
        self._number_of_visits += 1.
        self._results[result] += session.match_points
        if self.parent:
            self.parent.backpropagate(result)
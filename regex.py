from __future__ import annotations

import argparse
from abc import ABC, abstractmethod


class State(ABC):
    @abstractmethod
    def __init__(self) -> None:
        self.next_states: list[State] = []

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):
    def __init__(self):
        super().__init__()

    def check_self(self, char: str):
        return super().check_self(char)


class TerminationState(State):
    def __init__(self):
        super().__init__()

    def check_self(self, char: str) -> bool:
        return char == ""


class DotState(State):
    """
    state for . character (any character accepted)
    """

    def __init__(self):
        super().__init__()

    def check_self(self, char: str) -> bool:
        return len(char) == 1


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """

    curr_sym: str = ""

    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.curr_sym = symbol

    def check_self(self, char: str) -> bool:
        return self.curr_sym == char


class StarState(State):
    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state

    def check_self(self, char: str) -> bool:
        if self.checking_state.check_self(char):
            return True
        for state in self.next_states:
            if state.check_self(char):
                return True

        return False


class PlusState(State):
    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state: State = checking_state

    def check_self(self, char: str) -> bool:
        if self.checking_state.check_self(char):
            return True
        return False


class RegexFSM:
    def __init__(self, regex_expr: str) -> None:
        self.curr_state: StartState = StartState()
        prev_state = self.curr_state
        tmp_next_state = None

        for char in regex_expr:
            new_state = self.__init_next_state(char, prev_state, tmp_next_state)

            if char in ("*", "+"):
                _ = prev_state.next_states.pop()
                prev_state.next_states.append(new_state)
                tmp_next_state = new_state
            else:
                if tmp_next_state is not None:
                    prev_state = tmp_next_state
                prev_state.next_states.append(new_state)
                tmp_next_state = new_state

        if tmp_next_state is not None:
            tmp_next_state.next_states.append(TerminationState())
        else:
            self.curr_state.next_states.append(TerminationState())

    def __init_next_state(
        self, next_token: str, prev_state: State, tmp_next_state: State
    ) -> State:
        new_state = None

        match next_token:
            case next_token if next_token == ".":
                new_state = DotState()
            case next_token if next_token == "*":
                new_state = StarState(tmp_next_state)
                # here you have to think, how to do it.

            case next_token if next_token == "+":
                new_state = PlusState(tmp_next_state)

            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)

            case _:
                raise AttributeError("Character is not supported")

        return new_state

    def check_string(self, string: str) -> bool:
        def dfs(current_idx: int, current_state: State) -> bool:
            if current_idx == len(string):
                if isinstance(current_state, TerminationState):
                    return True
                for next_s in current_state.next_states:
                    if isinstance(next_s, TerminationState) or getattr(
                        next_s, "check_self", lambda x: False
                    )(""):
                        return True
                    if isinstance(next_s, StarState) and dfs(current_idx, next_s):
                        return True
                return False

            char = string[current_idx]
            if isinstance(current_state, (StarState, PlusState)):
                if current_state.checking_state.check_self(char):
                    if dfs(current_idx + 1, current_state):
                        return True

            for next_s in current_state.next_states:
                if next_s.check_self(char):
                    if dfs(current_idx + 1, next_s):
                        return True
                if isinstance(next_s, StarState):
                    if dfs(current_idx, next_s):
                        return True

            return False

        return dfs(0, self.curr_state)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check a string against a regex pattern using FSM."
    )
    parser.add_argument("pattern", type=str, help="The regex pattern")
    parser.add_argument("input", type=str, help="Input string")
    args = parser.parse_args()

    print(RegexFSM(args.pattern).check_string(args.input))

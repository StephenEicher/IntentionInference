import cvxpy as cp
import numpy as np
import random
import warnings
import time
from abc import ABC, abstractmethod
from typing import Any, Callable
from multiprocessing import Pool, Array, Manager
import pickle
import threading
from typing import Any

warnings.simplefilter(action='ignore', category=FutureWarning)


class MDP():
    """
    Data structure for a Markov Decision Process. In mathematical terms,
    MDPs are sometimes defined in terms of a tuple consisting of the various
    components of the MDP, written (S, A, T, R, gamma):

    gamma: discount factor
    S: state space
    A: action space
    T: transition function
    R: reward function
    TR: sample transition and reward. We will us `TR` later to sample the next
        state and reward given the current state and action: s_prime, r = TR(s, a)
    """
    def __init__(self,
                 gamma: float,
                 S: list[Any],
                 A: list[Any],
                 T: Callable[[Any, Any, Any], float] | np.ndarray,
                 R: Callable[[Any, Any], float] | np.ndarray,
                 TR: Callable[[Any, Any], tuple[Any, float]] = None):
        self.gamma = gamma  # discount factor
        self.S = S          # state space
        self.A = A          # action space

        # reward function R(s, a)
        if type(R) == np.ndarray:
            self.R = lambda s, a: R[s, a]
        else:
            self.R = R

        # transition function T(s, a, s')
        # sample next state and reward given current state and action: s', r = TR(s, a)
        if type(T) == np.ndarray:
            self.T = lambda s, a, s_prime: T[s, a, s_prime]
            self.TR = lambda s, a: (np.random.choice(len(self.S), p=T[s, a]), self.R(s, a)) if not np.all(T[s, a] == 0) else (np.random.choice(len(self.S)), self.R(s, a))
        else:
            self.T = T
            self.TR = TR

    def lookahead(self, U: Callable[[Any], float] | np.ndarray, s: Any, a: Any) -> float:
        if callable(U):
            return self.R(s, a) + self.gamma * np.sum([self.T(s, a, s_prime) * U(s_prime) for s_prime in self.S])
        return self.R(s, a) + self.gamma * np.sum([self.T(s, a, s_prime) * U[i] for i, s_prime in enumerate(self.S)])

    def iterative_policy_evaluation(self, policy: Callable[[Any], Any], k_max: int) -> np.ndarray:
        U = np.zeros(len(self.S))
        for _ in range(k_max):
            U = np.array([self.lookahead(U, s, policy(s)) for s in self.S])
        return U

    def policy_evaluation(self, policy: Callable[[Any], Any]) -> np.ndarray:
        R_prime = np.array([self.R(s, policy(s)) for s in self.S])
        T_prime = np.array([[self.T(s, policy(s), s_prime) for s_prime in self.S] for s in self.S])
        I = np.eye(len(self.S))
        return np.linalg.solve(I - self.gamma * T_prime, R_prime)

    def greedy(self, U: Callable[[Any], float] | np.ndarray, s: Any) -> tuple[float, Any]:
        expected_rewards = [self.lookahead(U, s, a) for a in self.A]
        idx = np.argmax(expected_rewards)
        return self.A[idx], expected_rewards[idx]

    def backup(self, U: Callable[[Any], float] | np.ndarray, s: Any) -> float:
        return np.max([self.lookahead(U, s, a) for a in self.A])

    def randstep(self, s: Any, a: Any) -> tuple[Any, float]:
        return self.TR(s, a)

    def simulate(self, s: Any, policy: Callable[[Any], Any], d: int) -> list[tuple[Any, Any, float]]:  # TODO - Create test
        trajectory = []
        for _ in range(d):
            a = policy(s)
            s_prime, r = self.TR(s, a)
            trajectory.append((s, a, r))
            s = s_prime
        return trajectory
    
    def random_policy(self):
        return lambda s, A=self.A: random.choices(A)[0]
    
class MDPSolutionMethod(ABC):
    pass

class OnlinePlanningMethod(MDPSolutionMethod):
    @abstractmethod
    def __call__(self, s: Any) -> Any:
        pass



class MonteCarloTreeSearch(OnlinePlanningMethod):

    def __init__(self,
                 P: MDP,
                 N: dict[tuple[Any, Any], int],
                 Q: dict[tuple[Any, Any], float],
                 d: int,
                 m: int,
                 c: float,
                 U: Callable[[Any], float]):
        self.P = P  # problem
        self.N = N  # visit counts
        self.Q = Q  # action value estimates
        self.d = d  # depth
        self.m = m  # number of simulations
        self.c = c  # exploration constant
        self.U = U  # value function estimate

    # def __call__(self, s: Any) -> Any:
    #     for _ in range(self.m):
    #         self.simulate(s, d=self.d)
    #         A = self.P.A(s)
    #     return A[np.argmax([self.Q[(s, a)] for a in A])]
    def simulate_wrapper(self, s: Any):
        return self.simulate(s, self.d)
    # def __call__(self, s: Any) -> Any:
    #     max_workers = min(self.m, 2000)  # Adjust max_workers based on your system's capabilities
        
    #     # Use ThreadPoolExecutor to manage a pool of threads
    #     with ThreadPoolExecutor(max_workers) as executor:
    #         futures = [
    #             executor.submit(self.simulate_wrapper, s)
    #             for _ in range(self.m)
    #         ]
            
    #         # Ensure all futures are completed
    #         for future in futures:
    #             future.result()

    #     A = self.P.A(s)
    #     return A[np.argmax([self.Q[(s, a)] for a in A])]

    # def __call__(self, s: Any) -> Any:
    #     max_workers = min(self.m, 50)

    #     # Create a shared array and a lock
    #     shared_results = Array('d', [0.0])
    #     manager = Manager()
    #     lock = manager.Lock()

    #     with Pool(max_workers) as pool:
    #         # Create a list of arguments for each process
    #         args = [(s, shared_results, lock) for _ in range(self.m)]
    #         pool.starmap(self.simulate_wrapper, args)

    #     A = self.P.A(s)
    #     return A[np.argmax([self.Q[(s, a)] for a in A])]

    def __call__(self, s):
        threads = []
        def thread_task():
            self.simulate(s, d=self.d)        
        
        # Create threads
        for _ in range(self.m):
            thread = threading.Thread(target=thread_task)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to finish
        for thread in threads:
            thread.join()
        
        A = self.P.A(s)
        return A[np.argmax([self.Q[(s, a)] for a in A])]
    

    def simulate(self, s: Any, d: int):
        if d <= 0:
            return self.U(s)
        A = self.P.A(s)
        if not A:
            print("End game state detected!")
            return self.U(s)
        if (s, A[0]) not in self.N:
            for a in A:
                self.N[(s, a)] = 0
                self.Q[(s, a)] = 0.0
            return self.U(s)
        a = self.explore(s)
        s_prime, r = self.P.randstep(s, a)
        q = r + self.P.gamma * self.simulate(s_prime, d - 1)
        self.N[(s, a)] += 1
        self.Q[(s, a)] += (q - self.Q[(s, a)]) / self.N[(s, a)]
        return q

    def explore(self, s: Any) -> Any:
        A, N = self.P.A(s), self.N
        Ns = np.sum([N[(s, a)] for a in A])
        return A[np.argmax([self.ucb1(s, a, Ns) for a in A])]

    def ucb1(self, s: Any, a: Any, Ns: int) -> float:
        N, Q, c = self.N, self.Q, self.c
        return Q[(s, a)] + c*self.bonus(N[(s, a)], Ns)

    @staticmethod
    def bonus(Nsa: int, Ns: int) -> float:
        return np.inf if Nsa == 0 else np.sqrt(np.log(Ns)/Nsa)
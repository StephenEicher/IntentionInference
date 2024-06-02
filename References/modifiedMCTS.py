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

    def __call__(self, s: Any) -> Any:
        for _ in range(self.m):
            self.simulate(s, d=self.d)
            A = self.P.A(s)
        return A[np.argmax([self.Q[(s, a)] for a in A])]

    def simulate(self, s: Any, d: int):
        #print("Simulating!")
        if d <= 0:
            return self.U(s)
        A = self.P.A(s)
        if not A:
            print("End game state detected!")
            return 0
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
from collections import defaultdict


class Graph:
    """
    Graph class for tasks cycle detection
    """
    def __init__(self, graph):
        self.graph = defaultdict(list)
        self.state = defaultdict(int)
        for u, v in graph:
            self.addEdge(u, v)

    def addEdge(self, u, v):
        self.graph[u].append(v)

    def __dfs(self, v):
        self.state[v] = 1
        for neighbour in self.graph[v]:
            if self.state[neighbour] == 0:
                if self.__dfs(neighbour):
                    return True
            elif self.state[neighbour] == 1:
                return True
        self.state[v] = 2
        return False

    def checkCycle(self):
        for u in self.graph.copy():
            if self.state[u] == 0 and self.__dfs(u):
                return True
        return False


def checkCycle(graph):
    g = Graph(graph)
    return g.checkCycle()

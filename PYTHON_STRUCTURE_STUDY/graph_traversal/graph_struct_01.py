# source: https://www.tutorialspoint.com/python_data_structure/python_graphs.htm
# Create the dictionary with graph elements
graph_elements = { "a": ["b", "c"],
                   "b": ["a", "d"],
                   "c": ["a", "d"],
                   "d": ["e"],
                   "e": ["d"]
                   }


class graph:
    def __init__(self,gdict=None):
        if gdict is None:
            gdict = {}
        self.gdict = gdict

    def getVertices(self):
        return list(self.gdict.keys())

    def edges(self):
        return self.findedges()

    # Find the distinct list of edges
    def findedges(self):
        edgename = []
        for vrtx in self.gdict:
            for nxtvrtx in self.gdict[vrtx]:
                if {nxtvrtx, vrtx} not in edgename:
                    # print(f'vrtx = {vrtx}, nxtvrtx = {nxtvrtx}')
                    edgename.append({vrtx, nxtvrtx})  # {} forms a set. This will eliminate the repeating elements
                    # print(f'edgename = {edgename}')
        return edgename

    # Add the vertex as a key
    def addVertex(self, vrtx):
        if vrtx not in self.gdict:
            self.gdict[vrtx] = []

    # Add the new edge
    def AddEdge(self, edge):
        edge = set(edge)
        (vrtx1, vrtx2) = tuple(edge)
        if vrtx1 in self.gdict:
            self.gdict[vrtx1].append(vrtx2)
        else:
            self.gdict[vrtx1] = [vrtx2]


if __name__ == '__main__':
    print(graph_elements)
    g = graph(graph_elements)
    print(f'Vertices = {g.getVertices()}')
    print(f'Edges = {g.edges()}')
    print('-' * 40)
    g.addVertex("f")
    print(f'Vertices = {g.getVertices()}')
    print('-' * 40)
    g.AddEdge({'a', 'e'})
    g.AddEdge({'a', 'c'})
    print(f'Edges = {g.edges()}')
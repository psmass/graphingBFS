#!/usr/local/bin/python
# Module graphingBFS.py
""" This program finds the shortest path between a user provided root node and all the other nodes in a given graph.
    Graphing may be selected as Directed or Undirected and the user is provided member functions to graph
    minimum hop count, minimum cost, or maximum bandwidth path between any two nodes (refer to the interfaces
    in class Graph.)

    With a directed graph, path edge values are unidirectional and used directly. With undirected graph, path edge
    values are ensured to be bi-directional and symmetric (i.e. the same value).  Depending upon edge value
    representing BW or Cost, if a different value in each direction is specified, the maximum or minimum value will
    respectively be selected.  Note that if BW is selected the 'Fattest Possible' pipes will be used upstream to
    route the traffic, even if a constricting pipe common to both paths is smaller than a more direct route.

    Nodes are entered as a dictionary of {name:[adjacency path list tuples]} where each path list tuple is of the
    format ('adjacenty name', edge cost).  If edge cost is not used, any value may be provided - e.g. 0).

    Return Values: A node Hop Count or Least-cost of -1, means there is no path for the node to the root.
    A node with BW = 999 means it's either the root itself or that there is no path (i.e. no BW) for the node to
    the root.
"""
from collections import deque  # use a deque for an efficient node processing queue
import time
import logging
import enum


class Routing(enum.Enum):
    leastCost = 0
    bestBandwidth = 1
    minHopCount = 2


class Node(object):
    """ Node Object is used by the Graph Object to hold each nodes adjacencies, edge values, hops from a given
        root etc. In C++ parlance it is considered a 'friend class' to the User interface Graph Ojbect.
    """

    def __init__(self, nodeName):
        self.name = nodeName
        self.adjacencies = []  # list of tuples (adjObject, edge_cost)
        self.numHopsFromRoot = -1  # aka level
        self.upstreamNodeToRoot = self
        self.valueToRoot = -1  # calculated edge value based on least cost or bw as selected
        self.lowestBwPipeToRoot = 999  # tracts smallest pipe upstream of us

    def resetNode(self):
        """ Used by Graph.connect() to clear out an old route of the same graph (perhaps with a different constraint)"""
        self.adjacencies = []  # list of tuples (adjObject, edgeCost)
        self.numHopsFromRoot = -1  # aka level
        self.upstreamNodeToRoot = self
        self.valueToRoot = -1  # calculated edge value based on least cost or bw as selected
        self.lowestBwPipeToRoot = 999  # tracts smallest pipe upstream of us

    def printMyInfo(self):
        if self.numHopsFromRoot == 999:
            hops = "unknown"
        else:
            hops = self.numHopsFromRoot
        valueToRootStr = "unknown" if self.valueToRoot == 999 else self.valueToRoot

        print("Node: {} - Upstream node (toward root) is: {}, Hops from root: {}, Cost from root: {},"
              "lowest bandwidth pipe from root: {}, "
              .format(self.name, self.upstreamNodeToRoot.name, hops, valueToRootStr,
                      self.lowestBwPipeToRoot), end=" ")
        self.printNodeAdjacencies()

    def printNodeAdjacencies(self):
        adjNames = [(adjNode.name, adjNodeEdgeVal) for adjNode, adjNodeEdgeVal in self.adjacencies]
        print("Node: {} - Adjacency list: {}" .format(self.name, adjNames))


class Graph(object):
    """Graph object is the interface the user interacts with to graph his/her defined graph. """

    def __init__(self, nodeAdjD: dict, direct: bool, log: object):
        """ Initializes Graph, verifies ajacencies are valid and creats node objects.

            In C++ parlance, Node is a 'friend class' to Graph
        """
        self.logger = log
        self.directed = direct
        self.rootNodeName = ""
        self.node2Name = ""
        self.routingType = Routing.minHopCount  # default but does not matter as it will be overwritten
        self.routingTypeStr = ""

        # verify adj lists provided contain legal nodes - i.e. there is a dictionary key for each adjacent node
        self.logger.info("Verifying user supplied node adjacencies are defined nodes in user provided dictionary")
        for nodeName in nodeAdjD.keys():
            for (adjName, adjEdgeVal) in nodeAdjD[nodeName]:
                assert (adjName in nodeAdjD.keys()), " - Node %s: Adjacency node %s is not a defined node" \
                                                         % (nodeName, adjName)

        self.nodeAdjDict = nodeAdjD # user supplied adjacencies good so save them.
        self.logger.info("Verified valid adjacencies")

        self.logger.info("Creating graph node objects:")
        self.nodeObjDict = {nodeName: Node(nodeName) for nodeName in nodeAdjD.keys()}

    def connectAdj(self):
        """ Helper function to hook up adjacencies as directed or undirected and select values base on value
            meaning (BW or Cost).

            In the undirected case we need to create bi-directional links with the same edge value based as
            determined by the edge value type (e.g. Bandwidth or Cost). That is, if the user has specified a
            value (or different value) in each direction between adjacent nodes we need to select the highest
            if it represents BW and the lowest if it represents Cost.
        """

        self.logger.info("Connecting user specified adjacencies in instantiated node objects")
        # For each Node Object, go through the user specified adjacency lists of adjacency tuples (adjNodeName,
        # adjNodeEdgeVal) and create a list of actual adjacency object tuples (adjNode, adjNodeEdgeVal)
        #
        for nodeName in self.nodeObjDict.keys():
            for adjNodeName, adjNodeEdgeVal in self.nodeAdjDict[nodeName]:
                self.nodeObjDict[nodeName].adjacencies.append((self.nodeObjDict[adjNodeName], adjNodeEdgeVal))

        # At this point we have all node adjacency objects loaded into the node objects assuming a Directed Graph
        # if Undirected selected, then we need to go through each node's adjacencies and its adjacency's adjacency
        # to make sure the largest (BW) or smallest (Cost) edge value is used (as determined by edge bw user spec).
        # Further for an undirected (bi-directional) graph this edge values must be placed at both ends of the path
        # (i.e. in the nodes adjacency list as well as the adjacency's adjacency list.)
        time.sleep(.05)  # slight delay to pretty up output allowing logger output to catch up
        print("%s Graph Selected based on %s: "  % ("Directed" if self.directed else "Undirected", self.routingTypeStr))
        time.sleep(.05)  # slight delay to pretty up output allowing logger output to catch up

        if not self.directed:
            for nodeName in self.nodeObjDict.keys():
                node = self.nodeObjDict[nodeName]
                for i, (adjNode, adjEdgeVal) in enumerate(node.adjacencies):
                    nodeEdgeVal = adjEdgeVal
                    for j, (adjAdjNode, adjAdjEdgeVal) in enumerate(adjNode.adjacencies):
                        if node.name == adjAdjNode.name:
                            if self.routingType == Routing.bestBandwidth:
                                nodeEdgeVal = max(adjEdgeVal, adjAdjEdgeVal)
                            else:  # else edge value is cost so use the smallest
                                nodeEdgeVal = min(adjEdgeVal, adjAdjEdgeVal)
                            adjNode.adjacencies.pop(j)  # remove the node from the adjacent nodes list
                            break
                    # we should now have the new edge value for each end of he path with the corresponding adj adj node
                    # removed
                    node.adjacencies.pop(i)  # remove the adj node (both ends removed at this point)
                    node.adjacencies.append((adjNode, nodeEdgeVal))  # put back new adjNode in nodes adjacencies
                    adjNode.adjacencies.append((node, nodeEdgeVal))

    def routeFromN1toN2(self, node1Name, node2Name, routingType):
        """ User function to route FROM node1(by name) to all nodes in the graph, optimized for routingType
            (Least-cost, Best Bandwidth, or Minimum HopCount). Node2 is provided in the interface as the
            user interested path and allows other functions to use Node1 and Node2 as defaults.

            Nodes are enqueued for Breadth First Seach (BFS) from node1 through it's adjacencies, updating every
            path to the best upstream route(towards node1) and node parameter values as we go.

            The BFS process will graph all nodes that have a path to the root(Node1) optimizing for routingType
            parameter. After the routing is complete all nodes will each hold all path parameters (cost, bandwidth,
            hops) from Node1 as well as their first hop node upstream towards the root (Node1). As stated above,
            only the routingType parameter will be optimized.

            The path between node1 to to any node in the graph is found by going to the specified node
            and tracing it's path to the root (Node1) and then reversing the list.

            Note: We could have provided both routeFrom(root) as routeTo(root), but this is not needed
            as the above function provides both directions by reversing the nodes order given. Providing both
            would require a similar (but not the same) code with no no real value at the expense of additional code.
        """

        # verify user parameters
        self.logger.info("Verifying user supplied nodes are defined in user provided dictionary")
        assert (node1Name in self.nodeAdjDict.keys()), " - Provided Root Node %s: is not a defined node" \
                                                         % (node1Name)
        assert (node2Name in self.nodeAdjDict.keys()), " - Provided Root Node %s: is not a defined node" \
                                                         % (node2Name)
        # save parameters for later defaults
        self.rootNodeName = node1Name
        self.node2Name = node2Name
        self.routingType = routingType

        if self.routingType == Routing.leastCost:
            self.routingTypeStr = "Least-cost"
        elif self.routingType == Routing.bestBandwidth:
            self.routingTypeStr = "Best-bandwidth"
        else: #self.routingType == Routing.minHopCnt
            self.routingTypeStr = "Minimum hop-count"

        # clear out old node info if user previously routed this object via different constraints
        for nodeName in self.nodeObjDict.keys():
            self.nodeObjDict[nodeName].resetNode()
        self.connectAdj()  # connect adjacencies here vs. c'tor since routingType influences edge values selected

        self.logger.info("ROUTING FROM NODE %s TO NODE %s using: %s" %(node1Name, node2Name, self.routingTypeStr))

        # prime the processing queue with the from node as root
        nodeQ = deque()
        nodeQ.appendleft(self.nodeObjDict[self.rootNodeName])

        self.nodeObjDict[self.rootNodeName].numHopsFromRoot = 0
        self.nodeObjDict[self.rootNodeName].valueToRoot = 0

        while len(nodeQ) > 0:
            node = nodeQ.pop()
            self.logger.info("processing node %s" % node.name)

            # On the node we're processing (node) first see if there is a better route to root (that is we want all
            # the upstream nodes to have the best route before enqueueing the next layer of nodes). To do this we
            # will check if there is any node in the system (nodeNM), that we've visited, that points to node and its
            # upstream parameter plus the edge value is a better path? Recall (node) was enqueued with the direct
            # value from root via the Breadth First Search from root.
            for nodeNm in self.nodeObjDict.keys():
                if self.nodeObjDict[nodeNm].numHopsFromRoot != -1:  # make sure it's been visited previously
                    for (adjNode, adjNodeEdgeVal) in self.nodeObjDict[nodeNm].adjacencies:
                        if adjNode == node:
                            # At this point we found a node in the system (nodeNM) that has an adjacent node that
                            # points to the node we are processing. Is its US parameter + edge value a better path?
                            if self.routingType == Routing.bestBandwidth:
                                if ((self.nodeObjDict[nodeNm].lowestBwPipeToRoot > node.lowestBwPipeToRoot)
                                        and (adjNodeEdgeVal > node.lowestBwPipeToRoot)):
                                    self.logger.info("Fatter BW pipe to root found  via adjacent node %s with value %i"
                                                % (self.nodeObjDict[nodeNm].name,
                                                   min(self.nodeObjDict[nodeNm].lowestBwPipeToRoot, adjNodeEdgeVal)))
                                    node.upstreamNodeToRoot = self.nodeObjDict[nodeNm]
                                    node.lowestBwPipeToRoot = \
                                        min(self.nodeObjDict[nodeNm].lowestBwPipeToRoot, adjNodeEdgeVal)
                                    # update the cost to root along this path as well
                                    node.valueToRoot = self.nodeObjDict[nodeNm].valueToRoot + adjNodeEdgeVal
                                    node.numHopsFromRoot = self.nodeObjDict[nodeNm].numHopsFromRoot + 1

                            elif self.routingType == Routing.leastCost:
                                if self.nodeObjDict[nodeNm].valueToRoot + adjNodeEdgeVal < node.valueToRoot:
                                    self.logger.info("Lower cost route found")
                                    node.upstreamNodeToRoot = self.nodeObjDict[nodeNm]
                                    node.valueToRoot = self.nodeObjDict[nodeNm].valueToRoot + adjNodeEdgeVal
                                    # update the lowest bw pipe and hops to root along this route as well
                                    node.lowestBwPipeToRoot = \
                                        min(self.nodeObjDict[nodeNm].lowestBwPipeToRoot, adjNodeEdgeVal)
                                    node.numHopsFromRoot = adjNode.numHopsFromRoot + 1
                            # else self.routingType == Routing.minimumHopCount ( which we processed when we enqueued the
                            # node for processing)

            # For this upstream node we go through it's adjacencies which have not been 'visited, initialize
            # them (i.e. numHopsFromRoot, upStreamNodeToRoot, lowestBwPipeToRoot, and value to root) and thread
            # them to the queue for BF processing. Remember we process nodes as they are farther
            # hop-wise from root. We do not process nodes that are 'unreachable' from root.
            # (if self.nodeObjDict[nodeNm].numHopsFromRoot == -1 then we've not visited it before)
            for (adjNode, adjNodeEdgeVal) in node.adjacencies:
                if adjNode.numHopsFromRoot == -1:
                    adjNode.numHopsFromRoot = node.numHopsFromRoot + 1
                    adjNode.upstreamNodeToRoot = node
                    adjNode.lowestBwPipeToRoot = min(node.lowestBwPipeToRoot, adjNodeEdgeVal)
                    adjNode.valueToRoot = node.valueToRoot + adjNodeEdgeVal
                    nodeQ.appendleft(adjNode)
                    self.logger.info("appending node %s" % adjNode.name)

    def getPathAndParamsNode(self, endNode=""):
        """ Returns the path list of nodes between root and endNode (as previously graphed) along with
            parameters including hop-count, limiting-bandwidth, and total cost of route. The default
            end-node is self.node2

            Note: If least-cost graphing was previously done then the total cost will be least cost and
            the bandwidth parameter will show the lowest bandwidth pipe in the path and hop-count will
            show the hop-count to the least-cost path. If Best Band-width was selected then the path will
            be the best BW path (the path with the largest constricting BW (the smallest pipe in that path).
            This will be the Band-width returned, and both the least-cost and hop-count will simply be the
            cost hop-count of this Best Bandwidth path. If hop-count is selected then the path with the least
            hops will be shown with the bandwidth parameter being the smallest (constricting) pipe in the path,
            and the cost will again simply be the cost of this path
        """
        if endNode == "":
            endNode = self.node2Name
        path = [endNode]
        usNode = self.nodeObjDict[endNode]
        while usNode.upstreamNodeToRoot != usNode:  # while node not pointing to itself
            usNode = usNode.upstreamNodeToRoot
            path.append(usNode.name)  # back trace the path from node to root

        path.reverse()

        return path, self.nodeObjDict[endNode].valueToRoot, self.nodeObjDict[endNode].lowestBwPipeToRoot,\
            self.nodeObjDict[endNode].numHopsFromRoot

    def printFullInfo(self):
        """ For each node in the graph, prints all node info """
        print("Printing full data on each node to root-node %s:" %self.rootNodeName)
        for node in self.nodeObjDict.keys():
            self.nodeObjDict[node].printMyInfo()

    def printAdjacencies(self):
        """ For each node in the graph,  prints the nodes adjacency list"""
        for node in self.nodeObjDict.keys():
            self.nodeObjDict[node].printNodeAdjacencies()

    def printPath(self, nodeNm = ""):
        """ Prints the path from nodeNm back to the root. If no node is specified uses node1 and node2 as
            the path (specified during the previous routeFromN1toN2)
        """
        if nodeNm == "":
            nodeNm = self.node2Name
        paths, cost, bw, hopCnt = self.getPathAndParamsNode(nodeNm)
        time.sleep(.05)  # slight delay to pretty up output allowing logger output to catch up
        print("From node: %s (root node) to node: %s via path: %s with Cost: %i, BW constrained pipe: %i, Hop-count: %i"
              % (self.rootNodeName, nodeNm, paths, cost, bw, hopCnt))
        time.sleep(.05)  # slight delay to pretty up output allowing logger output to catch up

    def printPaths(self):
        """ For each node, trace back to root (node1) via the upstreamNodeToRoot and print the path based
            on the last routeFromN1toN2()
        """
        for nodeNm in self.nodeObjDict.keys():
            self.printPath(nodeNm)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(name)-s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger("Graphing")
    logger.setLevel(logging.CRITICAL)
    logger.info("Starting Logger")

    # NODE LIST 1:
    # ****************************************************************************************************************
    # A node adjacency dictionary is provided as input which is a list of each node 'name' and it's adjacencies
    # as a list of tuples. Each adjacency tuple includes the adjacent nodeName and edge value (i.e.
    # the dictionary is of the format: ('node name': [(adj1NodeName, adj1EdgeVal), (adj2NodeName, adj2EdgeVal)
    # etc..]. Adjacency names and specified routing path must match at the node names in the dictionary or an assertion
    # will be raised.
    #
    nodeAdjDict ={'a': [('b', 3)], 'b': [('a', 5), ('c', 5), ('d', 9)], 'c': [('b', 23), ('d', 7)],
                  'd': [('b', 1), ('c', 6)], 'e': [('d', 8)], 'f': [('g', 8)], 'g': [('f', 10)]}

    directed = True     # bool: optionally False for Undirected graph

    graph = Graph(nodeAdjDict, directed, logger)
    graph.routeFromN1toN2('a', 'c', Routing.bestBandwidth)
    graph.printPath()
    # graph.printFullInfo()
    print(graph.getPathAndParamsNode())
    graph.routeFromN1toN2('c', 'a', Routing.bestBandwidth)
    graph.printPath()
    graph.routeFromN1toN2('a', 'c', Routing.leastCost)
    graph.printPath()
    graph.routeFromN1toN2('c', 'a', Routing.leastCost)
    graph.printPath()

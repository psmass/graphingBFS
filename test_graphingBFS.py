# Module test_graphingBFS.py
from graphingBFS import *
import logging
import unittest

class Test(unittest.TestCase):

    def assertTestResult(self, graph, endPtName, expectedRoute, expectedLc, expectedBbw, expectedHc):
        print("Test %s graph %s, Path: %s to %s"
              % ("directed" if graph.directed else "undirected", graph.routingTypeStr, graph.rootNodeName, endPtName)
              , end=" ")
        resultRoute, resultLcRoute, resultBbw, resultHc = graph.getPathAndParamsNode(endPtName)
        self.assertEqual(resultRoute, expectedRoute)
        self.assertEqual(resultLcRoute, expectedLc)
        self.assertEqual(resultBbw, expectedBbw)
        self.assertEqual(resultHc,  expectedHc)
        print("-- PASS")

    def test1_comprehensive(self):
        logging.basicConfig(format='%(asctime)s %(name)-s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        logger = logging.getLogger("Graphing")
        logger.setLevel(logging.CRITICAL)
        logger.info("Starting Logger")
        print("\n")

        # NODE LIST 1:
        # ****************************************************************************************************************
        # A node adjacency dictionary is provided as input which is a list of each node 'name' and it's adjacencies
        # as a list of tuples. Each adjacency tuple includes the adjacent nodeName and edge value (i.e.
        # the dictionary is of the format: ('node name': [(adj1NodeName, adj1EdgeVal), (adj2NodeName, adj2EdgeVal)
        # etc..]. Adjacency names and root must match at least one of the node names in the dictionary or an assertion
        # will be raised.
        #
        nodeAdjDict = {'a': [('b', 3)], 'b': [('a', 5), ('c', 5), ('d', 9)], 'c': [('b', 23), ('d', 7)],
                       'd': [('b', 1), ('c', 6)], 'e': [('d', 8)], 'f': [('g', 8)], 'g': [('f', 10)]}

        directed = True  # bool: optionally False for Undirected graph

        graph = Graph(nodeAdjDict, directed, logger)
        graph.routeFromN1toN2( 'a', 'c', Routing.bestBandwidth)  # 'a' is root node
        self.assertTestResult(graph, 'c', ['a', 'b', 'c'], 8, 3, 2)  # first test the selected route
        # we've graphed all nodes from "root" ('a') and can process results
        self.assertTestResult(graph, 'a', ['a'], 0, 999, 0)
        self.assertTestResult(graph, 'b', ['a', 'b'], 3, 3, 1)
        self.assertTestResult(graph, 'd', ['a', 'b', 'd'], 12, 3, 2)
        self.assertTestResult(graph, 'e', ['e'], -1, 999, -1)
        self.assertTestResult(graph, 'f', ['f'], -1, 999, -1)
        self.assertTestResult(graph, 'g', ['g'], -1, 999, -1)

        graph.routeFromN1toN2('c', 'a', Routing.bestBandwidth)  # 'a' is root node
        self.assertTestResult(graph, 'a', ['c', 'b', 'a'], 28, 5, 2)  # first test the selected route
        # we've graphed all nodes from "root" ('c') and can process results
        self.assertTestResult(graph, 'b', ['c', 'b'], 23, 23, 1)
        self.assertTestResult(graph, 'c', ['c'], 0, 999, 0)
        self.assertTestResult(graph, 'd', ['c', 'b', 'd'], 32, 9, 2)
        self.assertTestResult(graph, 'e', ['e'], -1, 999, -1)
        self.assertTestResult(graph, 'f', ['f'], -1, 999, -1)
        self.assertTestResult(graph, 'g', ['g'], -1, 999, -1)

        graph.routeFromN1toN2( 'a', 'c', Routing.leastCost) # 'a' is root node
        self.assertTestResult(graph, 'c', ['a', 'b', 'c'], 8, 3, 2)  # first test the selected route
        # we've graphed all nodes from "root" ('a') and can process results
        self.assertTestResult(graph, 'a', ['a'], 0, 999, 0)
        self.assertTestResult(graph, 'b', ['a', 'b'], 3, 3, 1)
        self.assertTestResult(graph, 'd', ['a', 'b', 'd'], 12, 3, 2)
        self.assertTestResult(graph, 'e', ['e'], -1, 999, -1)
        self.assertTestResult(graph, 'f', ['f'], -1, 999, -1)
        self.assertTestResult(graph, 'g', ['g'], -1, 999, -1)

        graph.routeFromN1toN2('c', 'a', Routing.leastCost)  # 'a' is root node
        self.assertTestResult(graph, 'a', ['c', 'd', 'b', 'a'], 13, 1, 3)  # first test the selected route
        # we've graphed all nodes from "root" ('c') and can process results
        self.assertTestResult(graph, 'b', ['c', 'd', 'b'], 8, 1, 2)
        self.assertTestResult(graph, 'c', ['c'], 0, 999, 0)
        self.assertTestResult(graph, 'd', ['c', 'd'], 7, 7, 1)
        self.assertTestResult(graph, 'e', ['e'], -1, 999, -1)
        self.assertTestResult(graph, 'f', ['f'], -1, 999, -1)
        self.assertTestResult(graph, 'g', ['g'], -1, 999, -1)

        graph.routeFromN1toN2('e', 'a', Routing.minHopCount)  # 'a' is root node
        self.assertTestResult(graph, 'a', ['e', 'd', 'b', 'a'], 14, 1, 3) # first test the selected route
        # we've graphed all nodes from "root" ('a') and can process results
        self.assertTestResult(graph, 'b', ['e', 'd', 'b'], 9, 1, 2)
        self.assertTestResult(graph, 'c', ['e', 'd', 'c'], 14, 6, 2)
        self.assertTestResult(graph, 'd', ['e', 'd'], 8, 8, 1)
        self.assertTestResult(graph, 'e', ['e'], 0, 999, 0)
        self.assertTestResult(graph, 'f', ['f'], -1, 999, -1)
        self.assertTestResult(graph, 'g', ['g'], -1, 999, -1)

        graph.routeFromN1toN2('a', 'c', Routing.minHopCount)  # 'a' is root node
        self.assertTestResult(graph, 'c', ['a', 'b', 'c'], 8, 3, 2)  # first test the selected route
        # we've graphed all nodes from "root" ('c') and can process results
        self.assertTestResult(graph, 'a', ['a'], 0, 999, 0)
        self.assertTestResult(graph, 'b', ['a', 'b'], 3, 3, 1)
        self.assertTestResult(graph, 'd', ['a', 'b', 'd'], 12, 3, 2)
        self.assertTestResult(graph, 'e', ['e'], -1, 999, -1)
        self.assertTestResult(graph, 'f', ['f'], -1, 999, -1)
        self.assertTestResult(graph, 'g', ['g'], -1, 999, -1)

        directed = False # bool: optionally False for Undirected graph

        graph = Graph(nodeAdjDict, directed, logger)
        graph.routeFromN1toN2( 'a', 'c', Routing.bestBandwidth) # 'a' is root node
        self.assertTestResult(graph, 'c', ['a', 'b', 'c'], 28, 5, 2)  # first test the selected route
        # we've graphed all nodes from "root" ('a') and can process results
        self.assertTestResult(graph, 'a', ['a'], 0, 999, 0)
        self.assertTestResult(graph, 'b', ['a', 'b'], 5, 5, 1)
        self.assertTestResult(graph, 'd', ['a', 'b', 'd'], 14, 5, 2)
        self.assertTestResult(graph, 'e', ['a', 'b', 'd', 'e'], 22, 5, 3)
        self.assertTestResult(graph, 'f', ['f'], -1, 999, -1)
        self.assertTestResult(graph, 'g', ['g'], -1, 999, -1)

        graph.routeFromN1toN2('c', 'a', Routing.bestBandwidth)  # 'a' is root node
        self.assertTestResult(graph, 'a', ['c', 'b', 'a'], 28, 5, 2)  # first test the selected route
        # we've graphed all nodes from "root" ('c') and can process results
        self.assertTestResult(graph, 'b', ['c', 'b'], 23, 23, 1)
        self.assertTestResult(graph, 'c', ['c'], 0, 999, 0)
        self.assertTestResult(graph, 'd', ['c', 'b', 'd'], 32, 9, 2)
        self.assertTestResult(graph, 'e', ['c', 'b', 'd', 'e'], 40, 8, 3)
        self.assertTestResult(graph, 'f', ['f'], -1, 999, -1)
        self.assertTestResult(graph, 'g', ['g'], -1, 999, -1)

        graph.routeFromN1toN2( 'a', 'c', Routing.leastCost) # 'a' is root node
        self.assertTestResult(graph, 'c', ['a', 'b', 'c'], 8, 3, 2)  # first test the selected route
        # we've graphed all nodes from "root" ('a') and can process results
        self.assertTestResult(graph, 'a', ['a'], 0, 999, 0)
        self.assertTestResult(graph, 'b', ['a', 'b'], 3, 3, 1)
        self.assertTestResult(graph, 'd', ['a', 'b', 'd'], 4, 1, 2)
        self.assertTestResult(graph, 'e', ['a', 'b', 'd', 'e'], 12, 1, 3)
        self.assertTestResult(graph, 'f', ['f'], -1, 999, -1)
        self.assertTestResult(graph, 'g', ['g'], -1, 999, -1)

        graph.routeFromN1toN2('c', 'a', Routing.leastCost)  # 'a' is root node
        self.assertTestResult(graph, 'a', ['c', 'b', 'a'], 8, 3, 2)  # first test the selected route
        # we've graphed all nodes from "root" ('c') and can process results
        self.assertTestResult(graph, 'b', ['c', 'b'], 5, 5, 1)
        self.assertTestResult(graph, 'c', ['c'], 0, 999, 0)
        self.assertTestResult(graph, 'd', ['c', 'd'], 6, 6, 1)
        self.assertTestResult(graph, 'e', ['c', 'd', 'e'], 14, 6, 2)
        self.assertTestResult(graph, 'f', ['f'], -1, 999, -1)
        self.assertTestResult(graph, 'g', ['g'], -1, 999, -1)

        graph.routeFromN1toN2('e', 'a', Routing.minHopCount)  # 'a' is root node
        self.assertTestResult(graph, 'a', ['e', 'd', 'b', 'a'], 12, 1, 3)  # first test the selected route
        # we've graphed all nodes from "root" ('a') and can process results
        self.assertTestResult(graph, 'b', ['e', 'd', 'b'], 9, 1, 2)
        self.assertTestResult(graph, 'c', ['e', 'd', 'c'], 14, 6, 2)
        self.assertTestResult(graph, 'd', ['e', 'd'], 8, 8, 1)
        self.assertTestResult(graph, 'e', ['e'], 0, 999, 0)
        self.assertTestResult(graph, 'f', ['f'], -1, 999, -1)
        self.assertTestResult(graph, 'g', ['g'], -1, 999, -1)

        graph.routeFromN1toN2('a', 'c', Routing.minHopCount)  # 'a' is root node
        #graph.printPaths()
        self.assertTestResult(graph, 'c', ['a', 'b', 'c'], 8, 3, 2)  # first test the selected route
        # we've graphed all nodes from "root" ('c') and can process results
        self.assertTestResult(graph, 'a', ['a'], 0, 999, 0)
        self.assertTestResult(graph, 'b', ['a', 'b'], 3, 3, 1)
        self.assertTestResult(graph, 'd', ['a', 'b', 'd'], 4, 1, 2)
        self.assertTestResult(graph, 'e', ['a', 'b', 'd', 'e'], 12, 1, 3)
        self.assertTestResult(graph, 'f', ['f'], -1, 999, -1)
        self.assertTestResult(graph, 'g', ['g'], -1, 999, -1)

    def test2_assertBadAdj(self):
        logging.basicConfig(format='%(asctime)s %(name)-s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        logger = logging.getLogger("Graphing")
        logger.setLevel(logging.CRITICAL)
        logger.info("Starting Logger")
        print("\n")

        # NODE LIST 1:
        # ****************************************************************************************************************
        # A node adjacency dictionary is provided as input which is a list of each node 'name' and it's adjacencies
        # as a list of tuples. Each adjacency tuple includes the adjacent nodeName and edge value (i.e.
        # the dictionary is of the format: ('node name': [(adj1NodeName, adj1EdgeVal), (adj2NodeName, adj2EdgeVal)
        # etc..]. Adjacency names and root must match at least one of the node names in the dictionary or an assertion
        # will be raised.
        #
        nodeAdjDict = {'a': [('z', 3)], 'b': [('a', 5), ('c', 5), ('d', 9)], 'c': [('b', 23), ('d', 7)],
                       'd': [('b', 1), ('c', 6)], 'e': [('d', 8)], 'f': [('g', 8)], 'g': [('f', 10)]}

        directed = True  # bool: optionally False for Undirected graph

        with self.assertRaises(AssertionError):
            graph = Graph(nodeAdjDict, directed, logger)
            graph.routeFromN1toN2( 'a', 'c', Routing.bestBandwidth)  # 'a' is root node

    def test2_assertBadPath(self):
        logging.basicConfig(format='%(asctime)s %(name)-s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        logger = logging.getLogger("Graphing")
        logger.setLevel(logging.CRITICAL)
        logger.info("Starting Logger")
        print("\n")

        # NODE LIST 1:
        # ****************************************************************************************************************
        # A node adjacency dictionary is provided as input which is a list of each node 'name' and it's adjacencies
        # as a list of tuples. Each adjacency tuple includes the adjacent nodeName and edge value (i.e.
        # the dictionary is of the format: ('node name': [(adj1NodeName, adj1EdgeVal), (adj2NodeName, adj2EdgeVal)
        # etc..]. Adjacency names and root must match at least one of the node names in the dictionary or an assertion
        # will be raised.
        #
        nodeAdjDict = {'a': [('b', 3)], 'b': [('a', 5), ('c', 5), ('d', 9)], 'c': [('b', 23), ('d', 7)],
                       'd': [('b', 1), ('c', 6)], 'e': [('d', 8)], 'f': [('g', 8)], 'g': [('f', 10)]}

        directed = True  # bool: optionally False for Undirected graph

        with self.assertRaises(AssertionError):
            graph = Graph(nodeAdjDict, directed, logger)
            graph.routeFromN1toN2('z', 'c', Routing.bestBandwidth)  # 'a' is root node

        with self.assertRaises(AssertionError):
            graph = Graph(nodeAdjDict, directed, logger)
            graph.routeFromN1toN2('a', 'z', Routing.bestBandwidth)  # 'a' is root node


unittest.main(verbosity=2)

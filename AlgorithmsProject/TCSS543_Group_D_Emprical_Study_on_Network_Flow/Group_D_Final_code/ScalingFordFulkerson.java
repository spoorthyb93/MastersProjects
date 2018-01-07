
import java.util.HashMap;
import java.util.LinkedList;

/**
 * Implementation of Scaling Ford Fulkerson Algorithm.
 * 
 * @author Spoorthy Balasubrahmanya
 *
 */
public class ScalingFordFulkerson {

	/**
	 * Helper function to determine if there is an augmenting s-t path in the
	 * residual graph
	 * 
	 * @param adjGraph-
	 *            residual graph to check on.
	 * @param child_parent_map
	 *            - map to trace s-t path
	 * @param s
	 *            -source vertex
	 * @param t
	 *            -sink vertex
	 * @param delta
	 *            -minimum edge weight
	 * @return true if there is an augmenting st path
	 */
	private static boolean bfs(HashMap<String, LinkedList<Edge>> adjGraph, HashMap<String, Edge> child_parent_map,
			String s, String t, double delta) throws Exception {

		HashMap<String, Boolean> visitedNodes = new HashMap<>();

		for (String label : adjGraph.keySet()) {
			visitedNodes.put(label, false);
		}

		LinkedList<String> queue = new LinkedList<>();

		visitedNodes.put(s, true);
		queue.add(s);

		while (queue.size() > 0) {

			String poppedNodeLabel = queue.poll();
			LinkedList<Edge> neighbors = adjGraph.get(poppedNodeLabel);

			for (Edge e : neighbors) {
				Vertex neighbor = e.getSecondEndpoint();
				String label2 = (String) neighbor.getName();
				double value = (double) e.getData();
				if (!visitedNodes.get(label2) && value >= delta) {

					child_parent_map.put(label2, e);
					visitedNodes.put(label2, true);
					queue.add(label2);

				}

			}
		}

		return visitedNodes.get(t) == true;
	}

	/**
	 * Update the adjacency list graph with bottleneck edge weights
	 * 
	 * @param graph
	 *            - the graph to update
	 * @param path
	 *            - List of Edges to update in the graph
	 * @param updatedWeight
	 *            - The updated edge weight
	 * @param isResidual
	 *            - flag to detect if it is a residual graph.
	 */
	private static void updateGraphWithBottleneck(HashMap<String, LinkedList<Edge>> graph, LinkedList<Edge> path,
			double updatedWeight, boolean isResidual) throws Exception {

		// Update the edge flow on the graph

		for (Edge e : path) {
			Vertex first = e.getFirstEndpoint();
			String label = (String) first.getName();

			Vertex second = e.getSecondEndpoint();
			String label2 = (String) second.getName();

			LinkedList<Edge> neighbors = graph.get(label);
			for (Edge e2 : neighbors) {

				String secondLabel = (String) e2.getSecondEndpoint().getName();
				if (secondLabel.equals(label2)) {
					double wt = ((Double) e2.getData()).doubleValue();
					// Subtract bottle neck in residual graph.
					if (isResidual) {
						e2.setData(wt - updatedWeight);
					} else {
						// Add bottle neck in flow graph.
						e2.setData(wt + updatedWeight);
					}
				}

			}

			graph.put(label, neighbors);

		}

	}

	/**
	 * 
	 * @param orgGraph-
	 *            the graph with flow in forward direction
	 * @param resGraph-
	 *            the residual graph
	 * @param s
	 *            - source node
	 * @param t
	 *            - sink node
	 * @return max flow in the network
	 * @throws Exception
	 */
	public static double scalingFordFulkerson(HashMap<String, LinkedList<Edge>> orgGraph,
			HashMap<String, LinkedList<Edge>> resGraph, String s, String t) throws Exception {

		// Maintain a child_parent hash map with key as vertex label
		// and value as the Edge incident on this vertex
		// This map helps us trace the path from t back to s.
		HashMap<String, Edge> child_parent_map = new HashMap<>();

		double max_flow = 0;

		double max_cap = maxCapacityFromSource(resGraph, s);

		double delta = calculateDelta(max_cap);

		// Run scaling max flow.
		while (delta >= 1.0) {

			// As long as there is a s-t augmenting path with every edge having
			// at least delta
			while (bfs(resGraph, child_parent_map, s, t, delta)) {

				// Record all edges in this s-t path
				LinkedList<Edge> path = new LinkedList<Edge>();

				// Start at t and trace back to s
				String foo = t;
				while (!foo.equals(s)) {
					Edge e = child_parent_map.get(foo);
					path.add(e);
					Vertex _vertex = e.getFirstEndpoint();
					foo = (String) (_vertex.getName());
				}

				// Find bottleneck
				double bottleneck = Double.MAX_VALUE;

				for (String k : child_parent_map.keySet()) {
					Edge e = child_parent_map.get(k);
					double weight = ((Double) e.getData()).doubleValue();
					if (weight < bottleneck) {
						bottleneck = weight;
					}
				}

				// Add bottleneck to existing max flow and increase the max flow
				max_flow = max_flow + bottleneck;

				// Update original graph with bottleneck
				updateGraphWithBottleneck(orgGraph, path, bottleneck, false);

				// Update the Residual graph
				updateGraphWithBottleneck(resGraph, path, bottleneck, true);

				// Reset the Edges list
				path = new LinkedList<>();

				// Reset the child parent map
				child_parent_map = new HashMap<>();
			}
			delta = delta / 2.0;
		}

		return max_flow;

	}

	/**
	 * Helper function to build an adjacency list graph based on vertices and
	 * edges provided by Simple Graph
	 * 
	 * @param G
	 * @param isResidual
	 * @return Adjacency List graph
	 */
	private static HashMap<String, LinkedList<Edge>> buildGraph(SimpleGraph G, boolean isResidual) throws Exception {

		// Obtain the list of vertices in SimpleGraph
		LinkedList<Vertex> vertices = G.vertexList;

		// Obtain the list of Edges in SimpleGraph
		LinkedList<Edge> edges = G.edgeList;

		HashMap<String, LinkedList<Edge>> graph = new HashMap<>();

		// Add all vertices as keys to HashMap.
		for (Vertex v : vertices) {
			String label = (String) v.getName();
			graph.put(label, new LinkedList<Edge>());

		}

		// Add Edge objects to a LinkedList of values for a specified key
		// This LinkedList represents the neighbors for this vertex.
		// Edge weight is 0 for non residual graph and
		// Edge weight is equal to capacity for residual graph.
		for (Edge e : edges) {
			Vertex v1 = e.getFirstEndpoint();

			String label = (String) v1.getName();

			LinkedList<Edge> neighbors = graph.get(label);

			Edge e1;
			if (isResidual) {
				e1 = new Edge(e.getFirstEndpoint(), e.getSecondEndpoint(), e.getData(), e.getName());
			} else {
				e1 = new Edge(e.getFirstEndpoint(), e.getSecondEndpoint(), 0.0, e.getName());
			}

			neighbors.add(e1);

			graph.put(label, neighbors);
		}

		return graph;
	}

	/**
	 * Helper function to print adjacency list graph's vertices and edges.
	 * Useful for debugging.
	 * 
	 * @param graph
	 */
	private static void printGraph(HashMap<String, LinkedList<Edge>> graph) {
		for (String k : graph.keySet()) {

			System.out.print(k + " ");
			LinkedList<Edge> neighbors = graph.get(k);
			for (Edge e : neighbors) {
				System.out.print(e.getSecondEndpoint().getName() + " " + e.getData() + "      ");

			}
			System.out.println();

		}

	}

	/**
	 * Helper function to calculate the scaling factor delta delta is the
	 * maximum power of 2 less than equal to capacity.
	 * 
	 * @param n
	 * @return delta
	 */
	private static double calculateDelta(double n) {

		double delta = 0.0;
		double current = 1;
		while (current < n) {
			current *= 2;
		}

		delta = current / 2;
		return delta;
	}

	/**
	 * Helper function to calculate the max capacity flowing out of source node
	 * 
	 * @param graph
	 * @param s
	 * @return max capacity out of s
	 */
	private static double maxCapacityFromSource(HashMap<String, LinkedList<Edge>> graph, String s) throws Exception {
		double max_capcity_out_of_s = 0.0;

		LinkedList<Edge> neighbors = graph.get(s);

		double max = Double.MIN_VALUE;
		for (Edge e : neighbors) {
			double weight = ((Double) e.getData()).doubleValue();
			if (weight > max) {
				max = weight;
			}
		}

		max_capcity_out_of_s = max;
		return max_capcity_out_of_s;
	}

	/**
	 * Driver function for building SimpleGraph based on input file and
	 * executing scalingFordDulkerSon method
	 * 
	 * @param filePath
	 * @return max_flow
	 * @throws Exception
	 */
	public static double scalingFordFulkersonDriver(String filePath) throws Exception {
		// Build Simple Graph
		SimpleGraph G;
		G = new SimpleGraph();
		GraphInput.LoadSimpleGraph(G, filePath);

		// Construct the adjacency list based graph to push flow forward
		HashMap<String, LinkedList<Edge>> graph1 = buildGraph(G, false);

		// Construct the adjacency list based residual graph.
		HashMap<String, LinkedList<Edge>> graph2 = buildGraph(G, true);

		// Execute scalingMaxFlow
		double max_flow = scalingFordFulkerson(graph1, graph2, "s", "t");

		// Return the max_flow in the network.
		return max_flow;
	}
}

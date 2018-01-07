import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.Map;
import java.util.Queue;

import PushRelabel.PREdgeData;
import PushRelabel.PREdgeType;
import PushRelabel.PRVertexData;

public class PushRelabelAlgorithm {
	
	private SimpleGraph graph;
	private Vertex source, sink;
	private boolean isInitialized;
	private int maxFlow;
	private Queue<Vertex> relabelVertexQueue;
	private int relabelCount = 0;
	private int pushCount = 0;
	
	public PushRelabelAlgorithm(ArrayList<InputEdge> inputEdges)
	{
		this.constructGraph(inputEdges);
		this.isInitialized = false;
		this.relabelVertexQueue = new LinkedList<Vertex>();
	}
	
	public int getMaxFlow() throws Exception
	{
		if(this.isInitialized)
		{
			return this.maxFlow;
		}
		
		long start = System.currentTimeMillis();
		
		this.initialize();
		
		this.calculateMaxFlow();
		
		return this.maxFlow;
	}
	
	private void calculateMaxFlow() throws Exception
	{
		
		while (relabelVertexQueue.size() > 0) {
			
			Vertex vertex = this.relabelVertexQueue.poll();
			PRVertexData vertexData = (PRVertexData)vertex.getData();

			if (vertexData.excessFlow > 0) {
				if(!this.tryToPushForExcessFlow(vertex))
				{
					this.relabel(vertex);
				}
			}
		}

		PRVertexData sinkData = (PRVertexData)this.sink.getData();
		
		this.maxFlow = sinkData.excessFlow;
	}

	private boolean tryToPushForExcessFlow(Vertex vertexWithOverflow) throws Exception {
		
		PRVertexData vertexData = (PRVertexData)vertexWithOverflow.getData();
		
		for (Object edgeObject : vertexWithOverflow.incidentEdgeList) {
			
			Edge edge = (Edge)edgeObject;
			PREdgeData edgeData = (PREdgeData)edge.getData();
			
			if(!edge.getFirstEndpoint().equals(vertexWithOverflow))
			{
				continue;
			}
			
			Vertex secondVertex = edge.getSecondEndpoint();
			PRVertexData secondVertexData = (PRVertexData)secondVertex.getData();
			
			if(edgeData.getRemainingCapacity() > 0
					&& vertexData.height == secondVertexData.height + 1)
			{
				this.push(edge);
				
				if(!secondVertex.equals(this.sink) && !secondVertex.equals(this.source))
				{
					if(secondVertexData.excessFlow <= 0)
					{
						System.out.println("Shoudl not add this vertex");
					}
					
					this.relabelVertexQueue.add(secondVertex);
				}
			}
			
			if(vertexData.excessFlow <= 0)
			{
				break;
			}
		}
		
		if(vertexData.excessFlow > 0 && !vertexWithOverflow.equals(this.sink))
		{
			this.relabelVertexQueue.add(vertexWithOverflow);
		}
		
		return vertexData.excessFlow <= 0;
	}
	
	private void initialize() throws Exception
	{
		if(this.isInitialized)
		{
			return;
		}
		
		// set source height to |V|
		PRVertexData sourceData = (PRVertexData)this.source.getData();
		sourceData.height = this.graph.numVertices();
		
		// initialize preflow
		for (Object edgeObject : this.source.incidentEdgeList) {
			
			Edge edge = (Edge)edgeObject;
			PREdgeData edgeData = (PREdgeData)edge.getData();
			
			// reset flow if it is opposite edge
			if(!edge.getFirstEndpoint().equals(this.source))
			{
				edgeData.flow = 0;
				continue;
			}
			
			int edgeCapacity = edgeData.capacity;
			
			edgeData.flow = edgeCapacity;
			
			((PRVertexData)edge.getSecondEndpoint().getData()).excessFlow = edgeCapacity;
			
			this.relabelVertexQueue.add(edge.getSecondEndpoint());
			
			int sourceExcessFlow = sourceData.excessFlow;
			
			sourceData.excessFlow = (sourceExcessFlow - edgeCapacity);
		}
		
		this.isInitialized = true;
	}
	
	private void push(Edge edge) throws Exception
	{
		Vertex firstVertex = edge.getFirstEndpoint();
		Vertex secondVertex = edge.getSecondEndpoint();
		PREdgeData edgeData = (PREdgeData)edge.getData();
		PRVertexData firstVertexData = (PRVertexData)firstVertex.getData();
		PRVertexData secondVertexData = (PRVertexData)secondVertex.getData();
		
		//assert(firstVertex.getExcessFlow() > 0);
		//assert(firstVertex.getHeight() == secondVertex.getHeight() + 1);
		
		int deltaFlow = Math.min(firstVertexData.excessFlow, edgeData.getRemainingCapacity());
				
		Edge reverseEdge = null;
		PREdgeData reverseEdgeData = null;
		
		for (Object rEdgeObject : secondVertex.incidentEdgeList) {
			
			reverseEdge = (Edge)rEdgeObject;
			reverseEdgeData = (PREdgeData)reverseEdge.getData();
			
			if(reverseEdge.getSecondEndpoint().equals(firstVertex) && reverseEdgeData.edgeType != edgeData.edgeType)
			{
				break;
			}
		}
		
		edgeData.flow = edgeData.flow + deltaFlow;
		reverseEdgeData.flow = reverseEdgeData.flow - deltaFlow;
		
		firstVertexData.excessFlow = firstVertexData.excessFlow - deltaFlow;
		secondVertexData.excessFlow = secondVertexData.excessFlow + deltaFlow;
		
		this.pushCount++;
	}
	
	private void relabel(Vertex vertex) throws Exception
	{
		//assert(vertex.getExcessFlow() > 0);
		
		PRVertexData vertexData = (PRVertexData)vertex.getData();
		
		int minHeight = Integer.MAX_VALUE;
		
		for (Object edgeObject : vertex.incidentEdgeList) {
			
			Edge edge = (Edge)edgeObject;
			PREdgeData edgeData = (PREdgeData)edge.getData();
			
			if(!edge.getFirstEndpoint().equals(vertex))
			{
				continue;
			}
			
			if(edgeData.getRemainingCapacity() > 0)
			{
				Vertex secondVertex = edge.getSecondEndpoint();
				PRVertexData secondVertexData = (PRVertexData)secondVertex.getData();
				
				//assert(vertexData.height <= secondVertexData.height);    // (vertex.getHeight() <= secondVertex.getHeight() = true do not relabel
				
				if(minHeight > secondVertexData.height)
				{
					minHeight = secondVertexData.height;
				}
			}
		}
				
		vertexData.height = (minHeight + 1);
		
		this.relabelCount++;
	}
	
	/**
     * Constructs a simple graph for testing the algorithm
     * 
     * @return
     */
    private void constructGraph(ArrayList<InputEdge> inputEdges) {
        SimpleGraph G = new SimpleGraph();
        
        Map<String, Vertex> vertices = new HashMap<>();
        
        for (InputEdge edge : inputEdges) {
        	
        	String v1Name = edge.getFirstVertexName();
        	String v2Name = edge.getSecondVertexName();
        	Vertex v1 = null;
        	Vertex v2 = null;
        	
        	if(!vertices.containsKey(v1Name))
        	{
        		PRVertexData vertexData = new PRVertexData();
        		v1 = G.insertVertex(vertexData, v1Name);
        		vertices.put(v1Name, v1);
        	}
        	else
        	{
        		v1 = vertices.get(v1Name);
        	}
        	
        	if(!vertices.containsKey(v2Name))
        	{
        		PRVertexData vertexData = new PRVertexData();
        		v2 = G.insertVertex(vertexData, v2Name);
        		vertices.put(v2Name, v2);
        	}
        	else
        	{
        		v2 = vertices.get(v2Name);
        	}
			
        	PREdgeData edgeData = new PREdgeData(edge.getCapacity(), PREdgeType.Graph);
        	G.insertEdge(v1, v2, edgeData, v1Name + v2Name);
        	
        	PREdgeData residualEdgeData = new PREdgeData(edge.getCapacity(), PREdgeType.Resudual);
        	residualEdgeData.flow = edge.getCapacity();
        	G.insertEdge(v2, v1, residualEdgeData, v2Name + v1Name + "residual");
		}
        
        this.source = vertices.get("s");
        this.sink = vertices.get("t");
        this.graph = G;
    }
}

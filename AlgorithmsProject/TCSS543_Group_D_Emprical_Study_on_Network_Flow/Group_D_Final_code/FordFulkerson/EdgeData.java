package FordFulkerson;

public class EdgeData {
	
	private int edgeCapacity;
	private int edgeFlow;
	private boolean isBackEdge;

	public int getEdgeCapacity() {
		return this.edgeCapacity;
	}

	public int getEdgeFlow() {
		return this.edgeFlow;
	}

	public void setEdgeFlow(double edgeFlow) {
		
		this.edgeFlow = (int)edgeFlow;
		
	}

	public void setEdgeCapacity(double capacity) {
		this.edgeCapacity = (int)capacity;
	}

	public boolean isBackedge() {
		return this.isBackEdge;
	}

	public void setBackedge(boolean isBackEdge) {
		
		this.isBackEdge = isBackEdge;
	}

}

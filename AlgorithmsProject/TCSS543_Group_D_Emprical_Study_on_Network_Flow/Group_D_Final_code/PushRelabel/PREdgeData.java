package PushRelabel;

public class PREdgeData {
	public int capacity;
	public int flow;
	public PREdgeType edgeType;
	
	public PREdgeData(int capacity, PREdgeType edgeType)
	{
		this.capacity = capacity;
		this.edgeType = edgeType;
		this.flow = 0;
	}
	
	public int getRemainingCapacity()
	{
		return this.capacity - this.flow;
	}
}

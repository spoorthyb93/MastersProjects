
public class InputEdge {
	private String firstVertexName;
	private String secondVertexName;
	private int capacity;
	
	public InputEdge(String firstVertexName, String secondVertexName, int capacity)
	{
		this.firstVertexName = firstVertexName;
		this.secondVertexName = secondVertexName;
		this.capacity = capacity;
	}

	public String getFirstVertexName() {
		return firstVertexName;
	}

	public String getSecondVertexName() {
		return secondVertexName;
	}

	public int getCapacity() {
		return capacity;
	}
}

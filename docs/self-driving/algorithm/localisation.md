# 地图与定位

## Map Representation
- **metric**: The metric framework is the most common for humans and considers a two-dimensional space in which it places the objects. The objects are placed with precise coordinates. This representation is very useful, but is **sensitive to noise** and it is **difficult to calculate the distances precisely**.
- **topological**: The topological framework only considers places and relations between them. Often, the distances between places are stored. The map is then a graph, in which the **nodes corresponds to places** and **arcs correspond to the paths**.
- Voronoi diagram
- Grid

### Advantages of topological maps:
- Only sparse data storage
- Representation matches problem description: e.g.
instruct robot to move between discrete locations
- Recognition only requires consistency, not accuracy

### Advantages of metric maps
- Can extrapolate between known locations
- Can derive novel shortcuts
- Common representation to fuse sensor/motor data

This simulation creates a graph of randomly placed nodes. Each node has a set of genetic data that take the form of a vector of length 10, each index of which can contain any value bewteen -1000, and 1000. 
When a new node is born, is inherets its parent's genetic vector. Each index is marked with a flag. If the flag is true, that index is postively biased, ie we add some amount to it, otherwise we subtract from it.
Then, we add a random value to each index between -3 to 3, to simulate the genes evolving. If the vector index's values changes enough postively or negatively through the random mutation, its flag will change. Each node also has a family name which is a string of five chars that are assigned when the node is born. We use the gene vector and buckets to create the family name. Each bucket is assigned an alphanumerical character. The family names resist change. A pair of genes must change a lot for its letter to be reassigned. 

The goal of this project is to see if we can pathfind through this graph with no global knowledge. For example, distance to target would be a global variable, since we would need to see the whole graph to know that information. 
We pick two random nodes in the graph, then begin searching through the nodes. The only thing we know is our targets genetic vector, it's flags, and its family name. Can we find our way to our target by tracing genetic lineages?

A complete graph. I made sure that color is actually representative of its 10 gene vector. 
![Screenshot_2025-02-16_022040](https://github.com/user-attachments/assets/a6462d47-bacd-466e-bd44-2bcad4431f86)

Here is another graph, and the alogirthm is searching for its target using the genetic heuristic to make decisions about where to look. This version doesn't quite work yet. 
![image](https://github.com/user-attachments/assets/f632e8f4-13d6-40d9-950b-41962085c18a)


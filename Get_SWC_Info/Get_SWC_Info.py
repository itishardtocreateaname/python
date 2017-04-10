import math
from anytree import Node, RenderTree, AsciiStyle
from anytree.dotexport import RenderTreeGraph

class NeuronNode(Node):
	def __init__(self, id, type, x, y, z, r, pid):
		super(Node, self).__init__()
		self.name = id
		self.id = id
		self.type = type
		self.x = float(x)
		self.y = float(y)
		self.z = float(z)
		self.r = r
		self.pid = pid

		self.parent = None
		self.branch_node_num = 0
		self.dist_to_root = 0
		self.dist_to_leaf = 0

def readSWCFile(filename):
	with open(filename, 'r') as f:
		return (line for line in f.readlines() if not line.startswith('#'))

def d(n1, n2):
	return math.sqrt((n1.x - n2.x)**2 + (n1.y - n2.y)**2 + (n1.z - n2.z)**2)

def parseLine(line):
	return NeuronNode(*line.split())

def process(tree):
	if tree.is_root:
		tree.branch_node_num = 0
		tree.dist_to_root = 0
	else:
		tree.dist_to_root = tree.parent.dist_to_root + d(tree, tree.parent)
		if not tree.parent.is_root and len(tree.siblings) > 0:
			tree.branch_node_num = tree.parent.branch_node_num + 1
		else:
			tree.branch_node_num = tree.parent.branch_node_num
	
	for child in tree.children:
		process(child)
	else:
		if tree.is_leaf:
			tree.dist_to_leaf = 0
		else:
			dists = ((d(tree, child) + child.dist_to_leaf) for child in tree.children)
			tree.dist_to_leaf = min(dists)

def createForest(swc):
	all_node = {}
	forest = []
	for line in swc:
		node = parseLine(line) 
		all_node[node.name] = node
		if node.pid == '-1':
			forest.append(node)
		else:
			node.parent = all_node[node.pid]

	for tree in forest:
		process(tree)

	return forest

def print_tree_to_graph(forest):
	i = 1
	for tree in forest:
		RenderTreeGraph(tree).to_picture("tree%s.png" %i)
		i = i + 1

def print_detail(f, tree):
	f.writelines('{0},    {1},    {2},    {3},    {4}\n'.format(tree.id, tree.r, tree.branch_node_num, tree.dist_to_root, tree.dist_to_leaf))
	for child in tree.children:
		print_detail(f, child)

def print_detail_to_file(forest, filename):
	with open (filename, 'w') as f:
		f.writelines("Id  Radius  #branch_points  Dist_to_root  Dist_to_leaf\n")
		i = 1
		for tree in forest:
			f.writelines("\nTree%d\n" %i)
			print_detail(f, tree)
			i = i + 1

if __name__ == '__main__':
	swc = readSWCFile('test.swc')
	forest = createForest(swc)
	print_tree_to_graph(forest)
	print_detail_to_file(forest, "Node_Info.txt")

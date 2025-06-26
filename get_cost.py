#!/Library/Frameworks/Python.framework/Versions/3.11/bin/python3

import argparse
from pglast import parse_sql
from pprint import pprint
from anytree import Node, RenderTree
import json
#from pglast.stream import IndentedStream, RawStream  # can be used to get query out of AST

class myNode:
    def __init__(self, name = None, parent=None, children=None, numlinks = 0):
        self.name = name
        self.parent = parent
        self.children = children
        self.numlinks = numlinks
        
    def add_child(self, child_node):
        if self.children == None:
            self.children = []
        self.children.append(child_node)
        self.numlinks += 1
        
    def get_name(self):
        return self.name
    def get_parent(self):
        return self.parent
    def get_children(self):
        return self.children
    def get_numlinks(self):
        return self.numlinks
    
#_________________________________________________________________________________
def get_rels(sd):
    rels = []
    n1 = sd['@']
    if n1 == "SelectStmt":
        from_tup = sd["fromClause"]
        #print(from_dict)
        for i in range(len(from_tup)):
            from_dict = from_tup[i]
            n2 = from_dict["@"]
            if n2 == "RangeVar":
                rels.append(from_dict["relname"])
            elif n2 == "JoinExpr":
                arg_dict = from_dict["larg"]
                rels.append(arg_dict["relname"])
                arg_dict = from_dict["rarg"]
                rels.append(arg_dict["relname"]) 
    return rels

def compute_cost(dict):
    # hard-coded dict of cardinalities
    base_cards = {"company_name": 234997, "company_type": 4, "keyword": 134170, "link_type": 18, 
                  "movie_companies": 2609129, "movie_keyword":4523930, "movie_link": 29997, "title": 2528312,  
                  "char_name":3140339, "cast_info":36244344, "role_type":12, "info_type":113, "movie_info_idx":1380035, "name":4167491,
                  "movie_info":14835720}
    node_type = dict["@"]
    # base case 1 : RangeVar
    if node_type=="RangeVar":
        relname = dict["relname"]
        if relname not in base_cards:
            return 1
        return base_cards[relname]
    
    # recursive case 1 : JoinExpr 
    elif node_type=="JoinExpr":
        return ( compute_cost(dict["larg"]) * compute_cost(dict["rarg"]) )
    
    # recursive case 2: SelectStmt
    elif node_type=="SelectStmt":
        cost = 0
        from_tuple = dict["fromClause"]
        for dict2 in from_tuple:
            cost += compute_cost(dict2)
        return cost
    
    return -1
         
def get_subtree_nodes(parent, dict, alias_dict, nodes_lst):
    node_type = dict["@"]
    # base case 1 : RangeVar
    if node_type=="RangeVar":
        relname = dict["relname"]
        relname_alias = None
        if "alias" in dict:
            relname_alias = dict["alias"]
        if relname_alias!=None:
            alias_dict[relname_alias] = relname
            relname = relname_alias

        new_node = myNode(relname, parent, numlinks=1)
        parent.add_child(new_node)
        nodes_lst.append(new_node)
        
    
    # recursive case 1 : JoinExpr 
    elif node_type=="JoinExpr":
        new_node = myNode("join", parent, [], 1)
        parent.add_child(new_node)
        nodes_lst.append(new_node)
        alias_dict, nodes_lst = get_subtree_nodes(new_node, dict["larg"], alias_dict, nodes_lst)
        alias_dict, nodes_lst = get_subtree_nodes(new_node, dict["rarg"], alias_dict, nodes_lst)
        
    # recursive/base case [?]: any expression
    elif "Expr" in node_type:
        new_node = myNode("expr", parent, numlinks=1)
        parent.add_child(new_node)
        nodes_lst.append(new_node)
        if "lexpr" in dict:
            pass
    
    # recursive case 2: SelectStmt
    elif node_type=="SelectStmt":
        new_node = myNode("select", parent, [], 1)
        parent.add_child(new_node)
        nodes_lst.append(new_node)
        from_tuple = dict["fromClause"]
        
        for dict2 in from_tuple:
            alias_dict, nodes_lst = get_subtree_nodes(new_node, dict2, alias_dict, nodes_lst)
            
    else:
        pass
    
    return alias_dict, nodes_lst

def construct_tree(parent, child_lst):
    # 1. Regardless of case, create nodes and link to parent
    for my_node in child_lst:
        tree_node = Node(my_node.get_name(), parent = parent)
        off_shoot = my_node.get_children()
        # 2. Recursive case
        if off_shoot != None:
            construct_tree(tree_node, off_shoot)
    return parent

def construct_tree_dict(parent, op_counts):
    #parent_name = parent.get_name()
    plan_dict = {}
    # 1. create the nodes and put them in the parent's list of children in the plan_dict
    child_lst = parent.get_children()
    for child in child_lst:
        key_name = child.get_name()
        if key_name in op_counts:
            count = op_counts[key_name]
            key_name = key_name + "_" + str(count)
            op_counts[key_name] = count + 1
        else:
            op_counts[key_name] = 1
            key_name = key_name + "_" + str(0)
        plan_dict[key_name] = {}
        
        # 2. Recursive case
        off_shoot = child.get_children()
        if off_shoot != None:
            plan_dict[key_name], op_counts = construct_tree_dict(child, op_counts)
            
        else:
            # do not want the _i next to relation names
            plan_dict[child.get_name()] = plan_dict[key_name]
            del plan_dict[key_name]
    return plan_dict, op_counts


def plan_json(my_root):
    #1. get the plan in a dictionary format
    plan_dict = {"root":{}}
    plan_dict["root"], _ = construct_tree_dict(my_root, {})

    # 2. write plan_dict to json file
    with open("test.json", "w") as f:
        f.write(json.dumps(plan_dict, indent=1))
    # 3. return string version
    return json.dumps(plan_dict, indent=1)


def main():

    #1. Get user input for SQL query and epsilon (to be used later)
    parser = argparse.ArgumentParser()
    parser.add_argument('query', type=str)
    args = parser.parse_args()
    
    #2. Use pg_last to get an AST for the query
    q = args.query
    root = parse_sql(q)
    
    for i in range(len(root)):
        stmt = root[i]
        #pprint(stmt())
    
        #3. Get the names of the tables/relations
        stmt_dict = stmt.stmt(skip_none=True)
        rels = get_rels(stmt_dict)
        #print(rels)
        #print(compute_cost(stmt_dict))
        
    #3. Get tree nodes
    rootNode = myNode("root", None, [], 0)
    alias_dict, nodes_lst = get_subtree_nodes(rootNode, stmt_dict, {}, [rootNode])
    #print(nodes_lst)
    
    #4. Draw tree
    # 4(a) find root in list of nodes
    my_root, root = None, None
    for my_node in nodes_lst:
        if my_node.get_name()=="root":
            my_root = my_node
            root = Node("root")
    
    # 4(b) recursively construct tree
    root = construct_tree(root, my_root.get_children())
    json_obj = plan_json(my_root)
    print(json_obj)
   
    '''for child in subtree:
        node = Node(child.get_name(), parent=root)
        grand_children = child.get_children()
        if grand_children!=None:
            for grand_child in grand_children:
                node2 = Node(grand_child.get_name(), parent=node)'''
                                   
    # 4(c) Render the tree
    for pre, fill, node in RenderTree(root):
        print(f"{pre}{node.name}")
            
    # Access the RawStmt attributes
    '''print("Statement:", stmt.stmt)
    print("Location:", stmt.stmt_location)
    print("Length:", stmt.stmt_len)'''
    
   
    
 

if __name__=="__main__":
    main()
    
# test_query: 
# "select c1 from r1 join r2 on c1 where r1.c2 < 2 and r2.c3 > 3;"
# "select c1 from r1 where r1.c1 in (select c1 from r2);"

# Decisions that might look dumb but have valid reasons:
# 1. The construct_tree function takes the list of children but
## construct_tree_dict does not. Why? Because construct_tree takes parent
## in the form of a Node object provided by the python libary used to draw trees
## but construct_tree_dict takes parent in the form of the myNode object I wrote
## which has links to the myNode objects represeting its children.
from curses import def_prog_mode
from platform import node
from node import Node
import math
import parse

# calculate entropy for the given examples
def entropy(examples):
  pos = 0.0
  neg = 0.0
  for row in examples:
    if row['Class'] == '1':
      pos += 1
    else:
      neg += 1
  if pos == 0.0 or neg == 0.0:
    return 0.0
  else:
    p = pos / (pos + neg)
    n = neg / (pos + neg)
  return -(p * math.log(p, 2) + n * math.log(n, 2))

# calculate the information gain of an attribute to the given examples 
def info_gain(examples, attr):
  
    total_gain = entropy(examples)

    unique_v = set()
    for row in examples:
        unique_v.add(row[attr])
    for v in unique_v:
        cur_ex = []
        for row in examples:
            if row[attr] == v:
                cur_ex.append(row)
        sub_e = entropy(cur_ex)
        total_gain -= (float(len(cur_ex)) / float(len(examples))) * sub_e

    return total_gain


def ID3(examples, default):
    '''
    Takes in an array of examples, and returns a tree (an instance of Node) 
    trained on the examples.  Each example is a dictionary of attribute:value pairs,
    and the target class variable is a special attribute with the name "Class".
    Any missing attributes are denoted with a value of "?"
    '''
    for row in examples:
      if row['Class'] == '?':
        row['Class'] == default
    
    feat = [k for k in examples[0].keys()]
    feat.remove('Class')
    return ID3_helper(examples, feat, default)
  

def ID3_helper(examples, attributes, default):
  
    root = Node()
    
    max_gain = 0
    max_f = ''
    
    # find the attribute with the max information gain
    for f in attributes:
      info_g = info_gain(examples, f)
      if info_g > max_gain:
        max_gain = info_g
        max_f = f
    
    # No attribute has positive information gain
    if max_gain == 0:
      root.label = default
      return root 
    
    # find all distinct values for this attribute 
    root.attr = max_f
    unique_v = set()
    for row in examples:
        unique_v.add(row[max_f])
    
    # Iterate over every value and group examples by them, then calculate each entropy 
    for v in unique_v:
      cur_ex = []
      for row in examples:
            if row[max_f] == v:
                cur_ex.append(row)
      sub_e = entropy(cur_ex)
      
      # if all data have the same class 
      if sub_e == 0:
        newnode = Node()
        newnode.attr = v
        # label the node with the class, or default value if there is no data
        newnode.label = cur_ex[0]['Class'] if len(cur_ex) > 0 else default
        root.children[v] = newnode 
      # if not, continue to split 
      else:
        cur_attr = attributes.copy()
        cur_attr.remove(max_f)
        child = ID3_helper(cur_ex, cur_attr, default)
        root.children[v] = child    
    return root


def prune(node, examples):
    '''
    Takes in a trained tree and a validation set of examples.  Prunes nodes in order
    to improve accuracy on the validation data; the precise pruning strategy is up to you.
    '''


def test(node, examples):
    '''
    Takes in a trained tree and a test set of examples.  Returns the accuracy (fraction
    of examples the tree classifies correctly).
    '''
    total = len(examples)
    correct = 0.0
    for e in examples:
      real_v = e['Class']
      pred_v = evaluate(node, e)
      if real_v == pred_v:
        correct += 1.0
    return correct / total


def evaluate(node, example):
    '''
    Takes in a tree and one example.  Returns the Class value that the tree
    assigns to the example.
    '''
    # cur_node = Node()
    #node_c = node
    while node.label is None:
      cur_attr = node.attr
      ex_v = example[cur_attr]
      #print(ex_v)
      node = node.children[ex_v]
    return node.label



d = parse.parse('tennis.data')
n = ID3(d, '0')

nn = Node()
print(test(n, d))

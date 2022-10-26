from curses import def_prog_mode
from doctest import Example
from os import curdir
from platform import node
from node import Node
import math
import parse

# the default 'Class' value as missing 'Class' and most common 'Class' value
default_class = 0

# calculate entropy for the given examples
def entropy(examples):
    total_entropy = 0
    total = len(examples)
    unique_v = set()
    for row in examples:
        unique_v.add(row['Class'])
    for v in unique_v:
        count = 0
        for row in examples:
            if row['Class'] == v:
                count += 1
        cur_p = count / total
        cur_entropy = cur_p * math.log(cur_p, 2)
        total_entropy += cur_entropy

    return -total_entropy

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
    global default_class
    default_class = default
    
    process_example(examples)
    feat = [k for k in examples[0].keys()]
    feat.remove('Class')

    for row in examples:
        if row['Class'] == '?':
            row['Class'] == default

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
    # find the attribute with most unique values and split the data using it
    # if only one attribute left, label the data with the most commmon class
    if max_gain == 0:
        if len(attributes) > 1:
            len_attr = 1
            for attr in attributes:
                v_set = set()
                for row in examples:
                    v_set.add(row[attr])
                if len(v_set) > len_attr:
                    max_f = attr
                    len_attr = len(v_set)
        else:
            root.label = mode(examples, 'Class')
            return root

    if max_f == '':
      root.label = mode(examples, 'Class')
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
            newnode.label = cur_ex[0]['Class'] if len(
                cur_ex) > 0 else mode(examples, 'Class')
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

    # if this is a leaf, return
    if not node.children:
        return

    # if there is no validation example, make the current node as a leaf
    if len(examples) == 0:
        node.children = {}
        node.label = mode(examples, 'Class')
        return

    # classify the current validation examples by the current attribute from the trained tree
    # store classification results in a dictionary, take attribute value as key, corresponding example as value
    cur_ex = {}
    cur_attr = node.attr

    for row in examples:
        if not row[cur_attr] in cur_ex.keys():
            cur_ex[row[cur_attr]] = [row]
        else:
            cur_ex[row[cur_attr]].append(row)

    # prune the subtree using the child node and classified examples
    # if there is no validation example for nodes with some attribute values, prune these nodes
    for attr in node.children.keys():
        if attr in cur_ex.keys():
            prune(node.children[attr], cur_ex[attr])
        else:
            prune(node.children[attr], {})

    # calculate the accuracy before and after pruning the current node, if it is better after pruning, then prune the current node
    correct = 0
    for row in examples:
        if row['Class'] == mode(examples, 'Class'):
            correct += 1

    if float(correct) / len(examples) >= test(node, examples):
        node.children = {}
        node.label = mode(examples, 'Class')


def test(node, examples):
    '''
    Takes in a trained tree and a test set of examples.  Returns the accuracy (fraction
    of examples the tree classifies correctly).
    '''
    process_example(examples)
    
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

    while node.label is None:
        cur_attr = node.attr
        ex_v = example[cur_attr]
        node = node.children[ex_v]
    return node.label


def mode(examples, attr):
    attr_num = {}
    for row in examples:
        if row[attr] != '?':
            if row[attr] in attr_num.keys():
                attr_num[row[attr]] += 1
            else:
                attr_num[row[attr]] = 1
    return max(attr_num, key=attr_num.get) if len(examples) > 0 else default_class


def process_example(examples):
    feat = [k for k in examples[0].keys()]
    feat_mode = {}
    for f in feat:
      feat_mode[f] = mode(examples, f)

    for row in examples:
      for f in feat:
        if row[f] == '?':
            row[f] = feat_mode[f]
    return examples


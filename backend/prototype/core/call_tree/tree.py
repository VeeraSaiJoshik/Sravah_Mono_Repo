from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from enum import Enum
from typing import Literal
import models.checklist as cl

class NodeCategory(Enum) : 
    BLOCKER = 1
    YESTERDAY_TASKS = 2
    TODAY_TASKS = 3

class NodeType(Enum) : 
    CHECKLIST_QUESTIONER = 1
    LINE_ITEMS = 2
    REAFFIRM = 3

class Profile(BaseModel) :
    project_id: int

    weight: int
    node_category: NodeCategory
    node_type: NodeType
    node_description: str

    raw_convo_snippet: str
    context: list[str]
    response: str

    @property
    def checklist(self) -> str :
        if self.node_type != NodeType.CHECKLIST_QUESTIONER : return ""

        if self.node_category == NodeCategory.BLOCKER : 
            return cl.blocker_checklist
        if self.node_category == NodeCategory.YESTERDAY_TASKS : 
            return cl.yesterday_checklist
        if self.node_category == NodeCategory.TODAY_TASKS : 
            return cl.today_checklist

class Node(BaseModel) : 
    id: UUID = Field(default_factory=uuid4)
    profile: Profile

    parent_node: "Node" | None
    children_nodes: list["Node"]
    pre_req_tasks: list[str]
    post_req_tasks: list[str]

    height: int
    depth: int

class Tree : 
    def __init__(self):
        starting_node: Node = Node(
            id="", 
            profile=Profile(),
            parent_node=None,
            children_nodes=[],
            pre_req_tasks=[],
            weight=0,
            height=0,
            depth=0
        )
        self.nodes_src_list: dict[str, Node] = {
            starting_node.id : starting_node
        }

    """ Basic Tree Node Manipulation Functions """

    def get_frontier_nodes(self, cur_node: Node | None) -> list[Node] : 
        if cur_node == None : 
            cur_node = self.nodes_src_list[0]
        
        if len(cur_node.children_nodes) == 0 : 
            return [cur_node]

        end_nodes = []
        for child in cur_node.children_nodes : 
            end_nodes += self.get_frontier_nodes(child)
        
        return end_nodes
    
    def get_conversation_path(self, cur_node: Node) : 
        if cur_node.parent_node == None : 
            return [cur_node]
        
        return self.get_conversation_path(cur_node.parent_node)
    
    def add_nodes(self, nodes: list[Profile]) :
        for node_profile in nodes : 
            node = Node(
                children_nodes=[],
                depth=0,
                height=1,
                parent_node=self.nodes_src_list[0],
                pre_req_tasks=[],
                post_req_tasks=[],
                profile=node_profile
            )
            self.nodes_src_list[node.id] = node
    
    def add_child_node(self, parent_id, nodes: list[Profile]) :
        parent = self.nodes_src_list.get(parent_id, None)
        if parent == None : 
            return
        
        for node_profile in nodes : 
            node = Node(
                children_nodes=[],
                depth=0,
                height=parent.height + 1,
                parent_node=self.nodes_src_list[0],
                pre_req_tasks=[],
                post_req_tasks=[],
                profile=node_profile
            )
            self.nodes_src_list[node.id] = node

            parent.children_nodes.append(node)

    def merge_tree_frontier(frontier: list[Node]):
        return frontier

    def sort_tree_frontier(frontier: list[Node]): 
        return frontier
    


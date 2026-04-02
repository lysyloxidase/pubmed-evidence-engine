from typing import List, Dict, Any

def build_knowledge_graph(documents: List[Dict[str, Any]], annotations_map: Dict[str, List[Dict[str, Any]]]) -> dict:
    """
    Builds a JSON serializable graph from documents and their annotations.
    Nodes: Documents, Genes, Diseases, Chemicals
    Edges: Document -> Annotation
    """
    nodes = []
    edges = []
    
    doc_nodes = set()
    ann_nodes = set()
    
    for i, doc in enumerate(documents):
        doc_id = doc.get("pmid", doc.get("id"))
        if not doc_id: continue
        
        doc_node_id = f"doc_{doc_id}"
        doc_label = f"[{i+1}] " + doc.get("title", f"Doc {doc_id}")
        if len(doc_label) > 35:
            doc_label = doc_label[:35] + "..."
            
        if doc_node_id not in doc_nodes:
            nodes.append({"id": doc_node_id, "label": doc_label, "group": "Document"})
            doc_nodes.add(doc_node_id)
            
        anns = annotations_map.get(str(doc_id), [])
        valid_anns = [a for a in anns if a.get("exact") and a.get("type")]
        
        # Limit annotations per doc to keep graph readable
        for ann in valid_anns[:6]:
            ann_text = ann["exact"].lower()
            ann_type = ann["type"]
            ann_node_id = f"ann_{ann_type}_{ann_text}"
            
            if ann_node_id not in ann_nodes:
                nodes.append({"id": ann_node_id, "label": ann["exact"], "group": ann_type})
                ann_nodes.add(ann_node_id)
                
            edges.append({"source": doc_node_id, "target": ann_node_id})
            
    return {"nodes": nodes, "edges": edges}

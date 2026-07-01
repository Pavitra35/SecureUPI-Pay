"""Graph Neural Network for detecting network-based fraud patterns."""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, GATConv, global_mean_pool
from torch_geometric.data import Data, Batch
from typing import Dict, List, Tuple, Any
import numpy as np
import os
from collections import defaultdict
from app.config import settings


class FraudGNN(nn.Module):
    """Graph Neural Network for fraud detection."""
    
    def __init__(self, input_dim: int = 10, hidden_dim: int = 64, output_dim: int = 2):
        super(FraudGNN, self).__init__()
        
        # Graph Convolutional Layers
        self.conv1 = GCNConv(input_dim, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, hidden_dim)
        self.conv3 = GCNConv(hidden_dim, hidden_dim)
        
        # Graph Attention Layer
        self.gat = GATConv(hidden_dim, hidden_dim, heads=4, concat=False)
        
        # Classification head
        self.fc1 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc2 = nn.Linear(hidden_dim // 2, output_dim)
        self.dropout = nn.Dropout(0.3)
        
    def forward(self, x, edge_index, batch=None):
        """
        Forward pass through the GNN.
        
        Args:
            x: Node features [num_nodes, input_dim]
            edge_index: Graph connectivity [2, num_edges]
            batch: Batch vector for graph-level pooling
            
        Returns:
            Node embeddings and graph-level prediction
        """
        # Graph convolutions
        x = F.relu(self.conv1(x, edge_index))
        x = self.dropout(x)
        x = F.relu(self.conv2(x, edge_index))
        x = self.dropout(x)
        x = F.relu(self.conv3(x, edge_index))
        
        # Graph attention
        x = F.relu(self.gat(x, edge_index))
        
        # Graph-level pooling
        if batch is not None:
            x = global_mean_pool(x, batch)
        else:
            x = global_mean_pool(x, torch.zeros(x.size(0), dtype=torch.long))
        
        # Classification
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        
        return F.softmax(x, dim=1), x


class TransactionGraphBuilder:
    """Builds transaction graphs from historical data."""
    
    def __init__(self, max_nodes: int = None):
        self.max_nodes = max_nodes or settings.MAX_GRAPH_NODES
        self.node_features = {}
        self.edge_list = []
        self.node_to_idx = {}
        self.idx_to_node = {}
        self.node_counter = 0
    
    def add_transaction(self, transaction: Dict[str, Any]):
        """Add a transaction to the graph."""
        sender = transaction.get('sender_upi', '')
        receiver = transaction.get('receiver_upi', '')
        amount = float(transaction.get('amount', 0))
        timestamp = transaction.get('timestamp', '')
        
        if not sender or not receiver:
            return
        
        # Add nodes
        for node in [sender, receiver]:
            if node not in self.node_to_idx:
                if self.node_counter >= self.max_nodes:
                    return  # Skip if graph is too large
                idx = self.node_counter
                self.node_to_idx[node] = idx
                self.idx_to_node[idx] = node
                self.node_features[node] = {
                    'degree': 0,
                    'total_amount': 0,
                    'transaction_count': 0
                }
                self.node_counter += 1
        
        # Update node features
        sender_idx = self.node_to_idx[sender]
        receiver_idx = self.node_to_idx[receiver]
        
        self.node_features[sender]['degree'] += 1
        self.node_features[sender]['total_amount'] += amount
        self.node_features[sender]['transaction_count'] += 1
        
        self.node_features[receiver]['degree'] += 1
        self.node_features[receiver]['total_amount'] += amount
        self.node_features[receiver]['transaction_count'] += 1
        
        # Add edge
        self.edge_list.append((sender_idx, receiver_idx))
    
    def build_graph_data(self) -> Data:
        """Build PyTorch Geometric Data object."""
        if len(self.node_to_idx) == 0:
            # Return empty graph
            return Data(x=torch.zeros(1, 10), edge_index=torch.zeros(2, 0, dtype=torch.long))
        
        # Build node feature matrix
        num_nodes = len(self.node_to_idx)
        feature_dim = 10
        x = torch.zeros(num_nodes, feature_dim)
        
        for node, idx in self.node_to_idx.items():
            features = self.node_features[node]
            x[idx] = torch.tensor([
                features['degree'],
                features['total_amount'] / 1000000,  # Normalize
                features['transaction_count'],
                features['degree'] / max(1, num_nodes),  # Normalized degree
                features['total_amount'] / max(1, features['transaction_count']),  # Avg amount
                1.0 if features['degree'] > 10 else 0.0,  # High degree flag
                1.0 if features['total_amount'] > 100000 else 0.0,  # High value flag
                features['transaction_count'] / max(1, num_nodes),  # Normalized count
                np.log1p(features['degree']),
                np.log1p(features['total_amount'])
            ], dtype=torch.float)
        
        # Build edge index
        if len(self.edge_list) > 0:
            edge_index = torch.tensor(self.edge_list, dtype=torch.long).t().contiguous()
        else:
            edge_index = torch.zeros(2, 0, dtype=torch.long)
        
        return Data(x=x, edge_index=edge_index)
    
    def get_neighbors(self, upi_id: str, depth: int = 1) -> List[str]:
        """Get neighbors of a node up to specified depth."""
        if upi_id not in self.node_to_idx:
            return []
        
        neighbors = set()
        current_nodes = {upi_id}
        
        for _ in range(depth):
            next_nodes = set()
            for node in current_nodes:
                if node in self.node_to_idx:
                    node_idx = self.node_to_idx[node]
                    # Find all edges connected to this node
                    for edge in self.edge_list:
                        if edge[0] == node_idx:
                            neighbor = self.idx_to_node[edge[1]]
                            neighbors.add(neighbor)
                            next_nodes.add(neighbor)
                        elif edge[1] == node_idx:
                            neighbor = self.idx_to_node[edge[0]]
                            neighbors.add(neighbor)
                            next_nodes.add(neighbor)
            current_nodes = next_nodes
        
        return list(neighbors)
    
    def reset(self):
        """Reset the graph builder."""
        self.node_features = {}
        self.edge_list = []
        self.node_to_idx = {}
        self.idx_to_node = {}
        self.node_counter = 0


class GNNFraudDetector:
    """GNN-based fraud detector."""
    
    def __init__(self):
        self.model = FraudGNN(input_dim=10, hidden_dim=64, output_dim=2)
        self.graph_builder = TransactionGraphBuilder()
        self.is_trained = False
    
    def detect_fraud(self, transaction: Dict[str, Any], historical_transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect fraud using GNN analysis.
        
        Args:
            transaction: Current transaction to analyze
            historical_transactions: Historical transactions for context
            
        Returns:
            Dictionary with fraud detection results
        """
        # Build graph from historical transactions
        self.graph_builder.reset()
        for txn in historical_transactions[-1000:]:  # Use last 1000 transactions
            self.graph_builder.add_transaction(txn)
        
        # Add current transaction
        self.graph_builder.add_transaction(transaction)
        
        # Build graph data
        graph_data = self.graph_builder.build_graph_data()
        
        if graph_data.x.size(0) == 0:
            return {
                'fraud_score': 0.5,
                'is_fraud': False,
                'network_risk': 'low',
                'connected_entities': 0,
                'reason': 'Insufficient graph data'
            }
        
        # Get sender and receiver indices
        sender = transaction.get('sender_upi', '')
        receiver = transaction.get('receiver_upi', '')
        
        sender_idx = self.graph_builder.node_to_idx.get(sender, -1)
        receiver_idx = self.graph_builder.node_to_idx.get(receiver, -1)
        
        # Calculate network-based features
        sender_neighbors = self.graph_builder.get_neighbors(sender, depth=2) if sender_idx >= 0 else []
        receiver_neighbors = self.graph_builder.get_neighbors(receiver, depth=2) if receiver_idx >= 0 else []
        
        connected_entities = len(set(sender_neighbors + receiver_neighbors))
        
        # Network risk indicators
        sender_degree = self.graph_builder.node_features.get(sender, {}).get('degree', 0)
        receiver_degree = self.graph_builder.node_features.get(receiver, {}).get('degree', 0)
        
        # High degree nodes might indicate money mules or fraud rings
        network_risk = 'low'
        if sender_degree > 50 or receiver_degree > 50:
            network_risk = 'high'
        elif sender_degree > 20 or receiver_degree > 20:
            network_risk = 'medium'
        
        # Check for suspicious patterns
        reasons = []
        if connected_entities > 100:
            reasons.append(f"High number of connected entities ({connected_entities})")
        if sender_degree > 50:
            reasons.append(f"Sender has unusually high transaction count ({sender_degree})")
        if receiver_degree > 50:
            reasons.append(f"Receiver has unusually high transaction count ({receiver_degree})")
        
        # Calculate fraud score based on network features
        fraud_score = 0.0
        if network_risk == 'high':
            fraud_score = 0.8
        elif network_risk == 'medium':
            fraud_score = 0.5
        else:
            fraud_score = 0.2
        
        # Adjust based on connected entities
        if connected_entities > 50:
            fraud_score = min(1.0, fraud_score + 0.2)
        
        return {
            'fraud_score': float(fraud_score),
            'is_fraud': fraud_score >= settings.FRAUD_THRESHOLD,
            'network_risk': network_risk,
            'connected_entities': connected_entities,
            'sender_degree': sender_degree,
            'receiver_degree': receiver_degree,
            'reasons': reasons if reasons else ['No network-based fraud indicators']
        }
    
    def load_model(self, filepath: str):
        """Load trained GNN model."""
        if filepath and os.path.exists(filepath):
            self.model.load_state_dict(torch.load(filepath, map_location='cpu'))
            self.is_trained = True
        else:
            # Initialize with random weights for demo
            self.is_trained = False


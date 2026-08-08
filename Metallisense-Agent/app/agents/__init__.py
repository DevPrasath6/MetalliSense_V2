"""
Agents Module - Production AI Agent System

This module contains the agent architecture for MetalliSense:
- Agent wrappers (production interfaces)
- Agent manager (orchestration)
- ML models (training & inference)
"""

# ML Models (for training and direct inference)
from .anomaly_agent import AnomalyDetectionAgent
from .alloy_agent import AlloyCorrectionAgent

# Production Agent Wrappers
from .anomaly_agent_wrapper import (
    AnomalyDetectionAgentWrapper,
    get_anomaly_agent
)
from .alloy_agent_wrapper import (
    AlloyCorrectionAgentWrapper,
    get_alloy_agent
)

# Agent Orchestration
from .agent_manager import (
    AgentManager,
    get_agent_manager
)

__all__ = [
    # ML Models
    'AnomalyDetectionAgent',
    'AlloyCorrectionAgent',
    
    # Agent Wrappers
    'AnomalyDetectionAgentWrapper',
    'AlloyCorrectionAgentWrapper',
    'get_anomaly_agent',
    'get_alloy_agent',
    
    # Agent Manager
    'AgentManager',
    'get_agent_manager',
]


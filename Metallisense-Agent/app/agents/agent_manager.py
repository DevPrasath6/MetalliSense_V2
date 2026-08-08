"""
AGENT MANAGER
Orchestration layer for MetalliSense AI Agents

🎯 Purpose:
    The brain of the AI system
    Coordinates agent invocation
    Enforces safety rules
    Defines interaction order
    
🔄 Invocation Flow:
    Incoming Data → Rule Engine → Agent Manager → Agents
    
🔐 Safety:
    - Agents never call each other
    - Manager decides
    - All outputs logged
    - Human approval required
"""
import sys
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timezone

sys.path.append(str(Path(__file__).parent.parent))

from agents.anomaly_agent_wrapper import get_anomaly_agent
from agents.alloy_agent_wrapper import get_alloy_agent
from policies.decision_policy import DecisionPolicy


class AgentManager:
    """
    Agent Manager - Orchestration Layer
    
    Responsibilities:
    1. Coordinate agent invocation
    2. Enforce decision policies
    3. Aggregate agent responses
    4. Ensure safety rules
    5. Provide audit trail
    
    Design Principles:
    - Stateless orchestration
    - Safe by design
    - Never autonomous
    - Always explainable
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        """Initialize Agent Manager"""
        self.anomaly_agent = None
        self.alloy_agent = None
        self.policy = DecisionPolicy()
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize agent instances (lazy loading)"""
        try:
            self.anomaly_agent = get_anomaly_agent()
            self.alloy_agent = get_alloy_agent()
            print("✓ Agent Manager: All agents initialized")
        except Exception as e:
            print(f"✗ Agent Manager: Error initializing agents: {e}")
            raise
    
    def analyze(
        self, 
        composition: Dict[str, float], 
        grade: str
    ) -> Dict:
        """
        Orchestrate full agent analysis
        
        Workflow:
        1. Check if anomaly detection should run (always)
        2. Run anomaly detection agent
        3. Check if alloy recommendation should run (conditional)
        4. If MEDIUM or HIGH severity, run alloy agent
        5. Aggregate results
        6. Add safety notes
        
        Args:
            composition: Element composition dictionary
            grade: Target metal grade
            
        Returns:
            Aggregated agent response with recommendations
        """
        print("\n" + "="*60)
        print("AGENT MANAGER: Starting Analysis")
        print("="*60)
        
        # Initialize response
        response = {
            "anomaly_agent": None,
            "alloy_agent": None,
            "final_note": self.policy.get_safety_note(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Step 1: Anomaly Detection (ALWAYS runs)
        if self.policy.should_check_anomaly(composition):
            print("→ Running Anomaly Detection Agent...")
            anomaly_result = self._run_anomaly_agent(composition)
            response["anomaly_agent"] = anomaly_result
            
            # Validate response
            if self.policy.validate_agent_response(
                "AnomalyDetectionAgent", 
                anomaly_result
            ):
                print(f"  ✓ Anomaly Score: {anomaly_result['anomaly_score']:.3f}")
                print(f"  ✓ Severity: {anomaly_result['severity']}")
                print(f"  ✓ Confidence: {anomaly_result['confidence']:.3f}")
            else:
                print("  ✗ Invalid anomaly agent response")
        
        # Step 2: Alloy Recommendation (CONDITIONAL on MEDIUM or HIGH severity)
        if self.policy.should_recommend_alloy(
            anomaly_result=response.get("anomaly_agent"),
            grade=grade
        ):
            print("→ Running Alloy Correction Agent...")
            alloy_result = self._run_alloy_agent(grade, composition)
            response["alloy_agent"] = alloy_result
            
            # Validate response
            if self.policy.validate_agent_response(
                "AlloyCorrectionAgent", 
                alloy_result
            ):
                additions = alloy_result['recommended_additions']
                print(f"  ✓ Recommendations: {len(additions)} elements")
                print(f"  ✓ Confidence: {alloy_result['confidence']:.3f}")
            else:
                print("  ✗ Invalid alloy agent response")
        else:
            print("→ Alloy Correction Agent: SKIPPED (severity not MEDIUM/HIGH)")
            response["alloy_agent"] = {
                "agent": "AlloyCorrectionAgent",
                "recommended_additions": {},
                "confidence": 0.0,
                "explanation": "Not invoked - anomaly severity below threshold (must be MEDIUM or HIGH)"
            }
        
        # Step 3: Safety check
        if self.policy.requires_human_approval(
            response.get("anomaly_agent"),
            response.get("alloy_agent")
        ):
            print("⚠ Human approval REQUIRED before any action")
        
        print("="*60)
        print("AGENT MANAGER: Analysis Complete")
        print("="*60 + "\n")
        
        return response
    
    def _run_anomaly_agent(self, composition: Dict[str, float]) -> Dict:
        """
        Run anomaly detection agent
        
        Args:
            composition: Element composition
            
        Returns:
            Anomaly agent response
        """
        try:
            if not self.anomaly_agent.is_ready():
                raise RuntimeError("Anomaly agent not ready")
            
            result = self.anomaly_agent.analyze(composition)
            
            # Log decision
            self.policy.log_decision(
                decision="ANOMALY_CHECK",
                reason=f"Severity: {result['severity']}, Score: {result['anomaly_score']:.3f}"
            )
            
            return result
        
        except Exception as e:
            print(f"Error in anomaly agent: {e}")
            return {
                "agent": "AnomalyDetectionAgent",
                "anomaly_score": 0.0,
                "severity": "ERROR",
                "confidence": 0.0,
                "explanation": f"Agent execution error: {str(e)}"
            }
    
    def _run_alloy_agent(
        self, 
        grade: str, 
        composition: Dict[str, float]
    ) -> Dict:
        """
        Run alloy correction agent
        
        Args:
            grade: Target grade
            composition: Element composition
            
        Returns:
            Alloy agent response
        """
        try:
            if not self.alloy_agent.is_ready():
                raise RuntimeError("Alloy agent not ready")
            
            result = self.alloy_agent.recommend(grade, composition)
            
            # Log decision
            additions = result.get("recommended_additions", {})
            self.policy.log_decision(
                decision="ALLOY_RECOMMENDATION",
                reason=f"Grade: {grade}, Additions: {len(additions)} elements"
            )
            
            return result
        
        except Exception as e:
            print(f"Error in alloy agent: {e}")
            return {
                "agent": "AlloyCorrectionAgent",
                "recommended_additions": {},
                "confidence": 0.0,
                "explanation": f"Agent execution error: {str(e)}"
            }
    
    def is_ready(self) -> bool:
        """Check if all agents are ready"""
        return (
            self.anomaly_agent is not None and 
            self.anomaly_agent.is_ready() and
            self.alloy_agent is not None and 
            self.alloy_agent.is_ready()
        )
    
    def get_status(self) -> Dict:
        """Get manager status"""
        return {
            "manager_version": self.VERSION,
            "policy_version": self.policy.VERSION,
            "agents": {
                "anomaly": {
                    "ready": self.anomaly_agent.is_ready() if self.anomaly_agent else False,
                    "metadata": self.anomaly_agent.get_metadata() if self.anomaly_agent else {}
                },
                "alloy": {
                    "ready": self.alloy_agent.is_ready() if self.alloy_agent else False,
                    "metadata": self.alloy_agent.get_metadata() if self.alloy_agent else {}
                }
            },
            "ready": self.is_ready()
        }


# Global manager instance
_manager_instance = None


def get_agent_manager() -> AgentManager:
    """Get or create global agent manager instance"""
    global _manager_instance
    
    if _manager_instance is None:
        _manager_instance = AgentManager()
    
    return _manager_instance


if __name__ == "__main__":
    # Test agent manager
    manager = get_agent_manager()
    
    print("="*60)
    print("AGENT MANAGER TEST")
    print("="*60)
    print(f"Status: {manager.get_status()}")
    
    # Test analysis
    test_comp = {
        "Fe": 81.2,
        "C": 4.4,
        "Si": 3.1,
        "Mn": 0.4,
        "P": 0.04,
        "S": 0.02
    }
    test_grade = "SG-IRON"
    
    print(f"\nInput Composition: {test_comp}")
    print(f"Target Grade: {test_grade}")
    
    result = manager.analyze(test_comp, test_grade)
    
    print("\n" + "="*60)
    print("RESULT")
    print("="*60)
    print(f"Anomaly Agent: {result['anomaly_agent']}")
    print(f"Alloy Agent: {result['alloy_agent']}")
    print(f"Final Note: {result['final_note']}")
    print("="*60)

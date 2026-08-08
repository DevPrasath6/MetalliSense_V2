"""
DECISION POLICY
Defines when agents are invoked and in what order

🎯 Purpose:
    Controls agent orchestration logic
    Ensures safe, deterministic agent invocation
    
🔐 Safety Rules:
    - Agents never call each other directly
    - Manager decides invocation order
    - All decisions are logged
    - Human approval required for actions
"""
from typing import Dict, Optional
from enum import Enum


class SeverityLevel(Enum):
    """Anomaly severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    ERROR = "ERROR"


class DecisionPolicy:
    """
    Decision Policy Engine
    
    Determines:
    1. When to invoke Anomaly Agent
    2. When to invoke Alloy Agent
    3. Order of execution
    """
    
    VERSION = "1.0.0"
    
    @staticmethod
    def should_check_anomaly(composition: Dict[str, float]) -> bool:
        """
        Determine if anomaly detection should be performed
        
        Policy: ALWAYS check for anomalies
        
        Args:
            composition: Input composition
            
        Returns:
            True if anomaly check should be performed
        """
        # Policy: Always check for anomalies on every composition
        return True
    
    @staticmethod
    def should_recommend_alloy(
        anomaly_result: Optional[Dict] = None,
        grade: Optional[str] = None
    ) -> bool:
        """
        Determine if alloy recommendation should be performed
        
        Policy: Recommend alloy if anomaly severity is MEDIUM or HIGH
        
        Args:
            anomaly_result: Result from anomaly agent
            grade: Target grade
            
        Returns:
            True if alloy recommendation should be performed
        """
        if anomaly_result is None:
            return False
        
        # Extract severity
        severity = anomaly_result.get("severity", "LOW")
        
        # Policy: Invoke alloy agent for MEDIUM or HIGH severity anomalies
        if severity in [SeverityLevel.MEDIUM.value, SeverityLevel.HIGH.value]:
            return True
        
        return False
    
    @staticmethod
    def get_execution_order() -> list:
        """
        Get agent execution order
        
        Returns:
            List of agent names in execution order
        """
        # Policy: Anomaly detection MUST run first
        # Alloy correction is conditional based on anomaly result
        return [
            "AnomalyDetectionAgent",
            "AlloyCorrectionAgent"  # Conditional
        ]
    
    @staticmethod
    def requires_human_approval(
        anomaly_result: Optional[Dict] = None,
        alloy_result: Optional[Dict] = None
    ) -> bool:
        """
        Determine if human approval is required
        
        Policy: ALL agent outputs require human approval
        
        Args:
            anomaly_result: Anomaly detection result
            alloy_result: Alloy recommendation result
            
        Returns:
            True if human approval required (always True)
        """
        # Policy: ALWAYS require human approval
        # Agents are advisory only
        return True
    
    @staticmethod
    def is_action_allowed(action: str) -> bool:
        """
        Determine if an action is allowed
        
        Policy: NO autonomous actions allowed
        
        Args:
            action: Action name
            
        Returns:
            False (no actions allowed without human approval)
        """
        # Policy: NO autonomous actions
        # All actions must be approved by human or rule engine
        return False
    
    @staticmethod
    def get_safety_note() -> str:
        """
        Get safety note for all agent responses
        
        Returns:
            Safety note string
        """
        return "Human approval required before action"
    
    @staticmethod
    def validate_agent_response(agent_name: str, response: Dict) -> bool:
        """
        Validate agent response structure
        
        Args:
            agent_name: Name of the agent
            response: Agent response
            
        Returns:
            True if response is valid
        """
        # Check for required fields
        required_fields = ["agent", "confidence", "explanation"]
        
        for field in required_fields:
            if field not in response:
                return False
        
        # Check agent name matches
        if response["agent"] != agent_name:
            return False
        
        # Check confidence is valid
        confidence = response.get("confidence", 0)
        if not (0 <= confidence <= 1):
            return False
        
        return True
    
    @staticmethod
    def log_decision(decision: str, reason: str) -> None:
        """
        Log decision for audit trail
        
        Args:
            decision: Decision made
            reason: Reason for decision
        """
        # In production, this would log to a proper logging system
        print(f"[DECISION POLICY] {decision} - Reason: {reason}")


if __name__ == "__main__":
    # Test decision policy
    print("="*60)
    print("DECISION POLICY TEST")
    print("="*60)
    
    policy = DecisionPolicy()
    
    # Test 1: Should check anomaly
    print(f"\n1. Should check anomaly: {policy.should_check_anomaly({})}")
    
    # Test 2: Should recommend alloy (LOW severity)
    low_result = {"severity": "LOW"}
    print(f"2. Should recommend alloy (LOW): {policy.should_recommend_alloy(low_result)}")
    
    # Test 3: Should recommend alloy (HIGH severity)
    high_result = {"severity": "HIGH"}
    print(f"3. Should recommend alloy (HIGH): {policy.should_recommend_alloy(high_result)}")
    
    # Test 4: Execution order
    print(f"4. Execution order: {policy.get_execution_order()}")
    
    # Test 5: Requires human approval
    print(f"5. Requires human approval: {policy.requires_human_approval()}")
    
    # Test 6: Is action allowed
    print(f"6. Is action allowed: {policy.is_action_allowed('adjust_furnace')}")
    
    # Test 7: Safety note
    print(f"7. Safety note: {policy.get_safety_note()}")
    
    print("="*60)

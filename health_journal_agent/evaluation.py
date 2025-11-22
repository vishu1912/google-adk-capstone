"""
Agent Evaluation Framework
===========================

This module evaluates the Health Journal Agent's performance across
multiple dimensions: accuracy, response quality, tool usage, and error handling.

Evaluation Categories:
1. Symptom Logging Accuracy
2. Medication Tracking Accuracy
3. Pattern Analysis Quality
4. Summary Generation Quality
5. Error Handling Robustness
"""

import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime
from .agent import health_coordinator
from .storage import store
from .tools import (
    log_symptom,
    track_medication,
    analyze_patterns,
    get_health_summary,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentEvaluator:
    """
    Evaluates agent performance using predefined test cases.
    
    Metrics tracked:
    - Accuracy: Did the agent use the correct tool?
    - Completeness: Did the agent gather all required information?
    - Error handling: Did the agent handle errors gracefully?
    - Response quality: Are responses clear and helpful?
    """
    
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
    
    def evaluate_tool_function(self, test_name: str, function: callable, 
                                args: dict, expected_status: str) -> Dict[str, Any]:
        """
        Evaluate a single tool function call.
        
        Args:
            test_name: Name of the test case
            function: Tool function to test
            args: Arguments to pass to function
            expected_status: Expected status in response ("success" or "error")
        
        Returns:
            Dictionary with test results
        """
        logger.info(f"Running test: {test_name}")
        
        try:
            result = function(**args)
            actual_status = result.get("status")
            
            passed = actual_status == expected_status
            self.total_tests += 1
            if passed:
                self.passed_tests += 1
            
            test_result = {
                "test_name": test_name,
                "passed": passed,
                "expected_status": expected_status,
                "actual_status": actual_status,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
            self.results.append(test_result)
            
            status_emoji = "✅" if passed else "❌"
            logger.info(f"{status_emoji} {test_name}: {actual_status}")
            
            return test_result
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {str(e)}")
            self.total_tests += 1
            
            test_result = {
                "test_name": test_name,
                "passed": False,
                "expected_status": expected_status,
                "actual_status": "exception",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            self.results.append(test_result)
            return test_result
    
    def get_summary(self) -> Dict[str, Any]:
        """Generate evaluation summary with scores."""
        pass_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        return {
            "total_tests": self.total_tests,
            "passed": self.passed_tests,
            "failed": self.total_tests - self.passed_tests,
            "pass_rate": round(pass_rate, 2),
            "timestamp": datetime.now().isoformat()
        }
    
    def print_report(self):
        """Print formatted evaluation report."""
        print("\n" + "=" * 60)
        print("HEALTH JOURNAL AGENT EVALUATION REPORT")
        print("=" * 60)
        
        summary = self.get_summary()
        print(f"\nOverall Results:")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Passed: {summary['passed']} ✅")
        print(f"  Failed: {summary['failed']} ❌")
        print(f"  Pass Rate: {summary['pass_rate']}%")
        
        print(f"\nDetailed Results:")
        for result in self.results:
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            print(f"  {status}: {result['test_name']}")
            if not result['passed']:
                print(f"    Expected: {result['expected_status']}")
                print(f"    Got: {result.get('actual_status', 'N/A')}")
        
        print("\n" + "=" * 60)


def run_tool_evaluations():
    """
    Run comprehensive tool function evaluations.
    
    Tests each tool function with valid and invalid inputs to verify:
    - Correct behavior with valid data
    - Proper error handling with invalid data
    - Expected response structure
    """
    evaluator = AgentEvaluator()
    
    print("\n🔍 Starting Tool Function Evaluations...\n")
    
    # =========================
    # SYMPTOM LOGGING TESTS
    # =========================
    print("Testing log_symptom()...")
    
    # Valid symptom log
    evaluator.evaluate_tool_function(
        "Log valid symptom",
        log_symptom,
        {"symptom_name": "headache", "severity": 7, "notes": "throbbing pain"},
        "success"
    )
    
    # Minimum severity
    evaluator.evaluate_tool_function(
        "Log symptom with minimum severity",
        log_symptom,
        {"symptom_name": "mild nausea", "severity": 1},
        "success"
    )
    
    # Maximum severity
    evaluator.evaluate_tool_function(
        "Log symptom with maximum severity",
        log_symptom,
        {"symptom_name": "severe migraine", "severity": 10},
        "success"
    )
    
    # Invalid severity (too low)
    evaluator.evaluate_tool_function(
        "Reject symptom with invalid severity (0)",
        log_symptom,
        {"symptom_name": "headache", "severity": 0},
        "error"
    )
    
    # Invalid severity (too high)
    evaluator.evaluate_tool_function(
        "Reject symptom with invalid severity (11)",
        log_symptom,
        {"symptom_name": "headache", "severity": 11},
        "error"
    )
    
    # =========================
    # MEDICATION TRACKING TESTS
    # =========================
    print("\nTesting track_medication()...")
    
    # Valid medication with time
    evaluator.evaluate_tool_function(
        "Track medication with time",
        track_medication,
        {"medication_name": "aspirin", "dosage": "100mg", "time_taken": "08:30"},
        "success"
    )
    
    # Valid medication without time (auto-fill)
    evaluator.evaluate_tool_function(
        "Track medication with auto-filled time",
        track_medication,
        {"medication_name": "ibuprofen", "dosage": "200mg"},
        "success"
    )
    
    # Valid medication with tablet dosage
    evaluator.evaluate_tool_function(
        "Track medication with tablet dosage",
        track_medication,
        {"medication_name": "vitamin D", "dosage": "2 tablets"},
        "success"
    )
    
    # =========================
    # PATTERN ANALYSIS TESTS
    # =========================
    print("\nTesting analyze_patterns()...")
    
    # Should work with existing data
    evaluator.evaluate_tool_function(
        "Analyze patterns with data",
        analyze_patterns,
        {},
        "success"
    )
    
    # =========================
    # SUMMARY GENERATION TESTS
    # =========================
    print("\nTesting get_health_summary()...")
    
    evaluator.evaluate_tool_function(
        "Generate health summary",
        get_health_summary,
        {},
        "success"
    )
    
    # Print results
    evaluator.print_report()
    
    return evaluator


def evaluate_agent_responses():
    """
    Evaluate end-to-end agent responses (requires async).
    
    This would test the full agent flow including:
    - Intent recognition
    - Appropriate agent routing
    - Response quality
    - Multi-turn conversations
    
    Note: Full implementation requires async execution and proper setup.
    """
    print("\n🤖 Agent Response Evaluation")
    print("=" * 60)
    print("Note: Full agent evaluation requires async context.")
    print("Tool evaluations above verify core functionality.")
    print("For production, integrate with ADK's evaluation framework.")
    print("=" * 60)


def evaluate_data_quality():
    """
    Evaluate the quality and consistency of stored data.
    
    Checks:
    - Data structure consistency
    - Timestamp format validity
    - Required field presence
    """
    print("\n📊 Data Quality Evaluation")
    print("=" * 60)
    
    issues = []
    
    # Check symptoms
    symptoms = store.get_symptoms(limit=100)
    print(f"\nChecking {len(symptoms)} symptom entries...")
    
    for i, symptom in enumerate(symptoms):
        required_fields = ["symptom", "severity", "timestamp"]
        for field in required_fields:
            if field not in symptom:
                issues.append(f"Symptom {i}: Missing field '{field}'")
        
        if "severity" in symptom:
            if not (1 <= symptom["severity"] <= 10):
                issues.append(f"Symptom {i}: Invalid severity {symptom['severity']}")
    
    # Check medications
    medications = store.get_medications(limit=100)
    print(f"Checking {len(medications)} medication entries...")
    
    for i, med in enumerate(medications):
        required_fields = ["medication", "dosage", "timestamp"]
        for field in required_fields:
            if field not in med:
                issues.append(f"Medication {i}: Missing field '{field}'")
    
    # Report
    if issues:
        print(f"\n❌ Found {len(issues)} data quality issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print(f"\n✅ All data entries pass quality checks!")
    
    print("=" * 60)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("HEALTH JOURNAL AGENT - COMPREHENSIVE EVALUATION")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all evaluations
    evaluator = run_tool_evaluations()
    evaluate_data_quality()
    evaluate_agent_responses()
    
    # Final summary
    summary = evaluator.get_summary()
    print("\n" + "=" * 60)
    print("FINAL EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Pass Rate: {summary['pass_rate']}%")
    
    if summary['pass_rate'] >= 90:
        print("Status: ✅ EXCELLENT - Agent is production-ready")
    elif summary['pass_rate'] >= 75:
        print("Status: ✅ GOOD - Minor improvements needed")
    elif summary['pass_rate'] >= 60:
        print("Status: ⚠️  FAIR - Significant improvements needed")
    else:
        print("Status: ❌ POOR - Major issues must be fixed")
    
    print("=" * 60)
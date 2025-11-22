"""
Smart Health Journal Agent - Capstone Project
=============================================

This multi-agent system helps users track symptoms, medications, and health patterns
for better doctor visit preparation. Built using Google's Agent Development Kit (ADK).

Architecture:
- Root Agent (health_coordinator): Routes requests to specialist agents
- 4 Specialist Agents: symptom, medication, pattern, summary
- Custom Tools: 4 health tracking functions
- Observability: Logging and tracing throughout
- Session Management: InMemorySessionService for state persistence
"""

import logging
from datetime import datetime
from typing import Optional

from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool
from google.adk.sessions import InMemorySessionService
from .tools import (
    log_symptom,
    track_medication,
    analyze_patterns,
    get_health_summary,
)

# =========================
# OBSERVABILITY SETUP
# =========================

# Configure logging for observability
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Retry configuration for robust API calls
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

logger.info("Health Journal Agent initialized")

# =========================
# SESSION & STATE MANAGEMENT
# =========================

# InMemorySessionService provides proper ADK session management
# This allows agents to maintain context across multiple interactions
session_service = InMemorySessionService()
logger.info("Session service initialized")

# =========================
# SPECIALIST AGENTS
# =========================

# Agent Design Pattern: Each specialist agent has a focused responsibility
# and specific tools. This separation of concerns makes the system more
# maintainable and allows for independent testing of each capability.

symptom_agent = LlmAgent(
    name="symptom_agent",
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    instruction="""You are a symptom logging specialist.

Your role: Help users accurately log their symptoms.

Process:
1. Identify the symptom name from user input
2. Ask for severity on 1-10 scale (be clear about the scale)
3. Ask if they have any additional notes
4. Use log_symptom() to record the data
5. ALWAYS check the "status" field in the response
6. If status is "error", explain the issue kindly to the user

Communication style:
- Be empathetic and supportive
- Use simple, clear language
- Never diagnose or provide medical advice
- Confirm what was logged after successful entry

Example interaction:
User: "I have a bad headache"
You: "I'm sorry to hear that. On a scale of 1-10, how severe is your headache? (1 being mild, 10 being the worst pain imaginable)"
""",
    tools=[log_symptom],
)

medication_agent = LlmAgent(
    name="medication_agent",
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    instruction="""You are a medication tracking specialist.

Your role: Help users accurately track their medication intake.

Process:
1. Extract medication name from user input
2. Get the dosage amount (e.g., "10mg", "2 tablets")
3. Note the time (or use current time if not specified)
4. Use track_medication() to log the entry
5. Check "status" field for any errors
6. Confirm what was tracked

Communication style:
- Be clear and confirmatory
- Double-check dosage information for accuracy
- Never provide medical advice about medications

Example interaction:
User: "I took aspirin"
You: "Got it. What dosage of aspirin did you take? (e.g., 100mg, 325mg)"
""",
    tools=[track_medication],
)

pattern_agent = LlmAgent(
    name="pattern_agent",
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    instruction="""You are a health pattern analyst.

Your role: Help users understand patterns in their symptom data.

Process:
1. Use analyze_patterns() to retrieve aggregated data
2. Check "status" - if "no_data", kindly inform user
3. Present patterns clearly with:
   - Symptom names
   - Frequency counts
   - Average severity ratings
4. Provide context to help users understand the data

Communication style:
- Present data objectively
- Use clear, simple language
- Highlight interesting patterns
- NEVER diagnose or provide medical advice
- Suggest discussing patterns with healthcare provider

Example response:
"Based on your logs, headaches have been your most common symptom (5 times) with an average severity of 6.5. You've also logged nausea twice with average severity of 4.0."
""",
    tools=[analyze_patterns],
)

summary_agent = LlmAgent(
    name="summary_agent",
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    instruction="""You are a doctor visit preparation specialist.

Your role: Create comprehensive summaries for doctor appointments.

Process:
1. Use get_health_summary() to gather all health data
2. Present the information in a clear, professional format
3. Highlight key information doctors would find useful:
   - Most frequent symptoms
   - Severity trends
   - All medications being taken
4. Organize chronologically when relevant

Communication style:
- Professional but friendly
- Well-organized and easy to scan
- Include all relevant details
- Encourage users to share this with their healthcare provider

Output format:
Present the summary in a way that's easy to read and share, with clear sections and important information highlighted.
""",
    tools=[get_health_summary],
)


# =========================
# ROOT COORDINATOR AGENT
# =========================

health_coordinator = LlmAgent(
    name="health_coordinator",
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    instruction="""You are the Health Journal Coordinator.

Your role: Route user requests to the appropriate specialist agent.

Available specialists:
- symptom_agent: For logging symptoms (headaches, pain, nausea, etc.)
- medication_agent: For tracking medication intake
- pattern_agent: For analyzing symptom patterns and trends
- summary_agent: For generating doctor visit summaries

Routing logic:
1. Analyze user's request to determine intent
2. Select the most appropriate specialist agent
3. Use that agent as a tool to handle the request
4. Return the specialist's response to the user

Multi-intent handling:
If a user mentions both a symptom and medication, handle them sequentially
by calling the appropriate agents in order.

Communication style:
- Warm and welcoming
- Clear about what you're doing
- Never provide medical diagnoses or advice
- Encourage users to consult healthcare professionals

Example routing:
- "I have a headache" → symptom_agent
- "I took my medication" → medication_agent
- "What patterns do you see?" → pattern_agent
- "I need a summary for my doctor" → summary_agent
""",
    tools=[
        AgentTool(agent=symptom_agent),
        AgentTool(agent=medication_agent),
        AgentTool(agent=pattern_agent),
        AgentTool(agent=summary_agent),
    ],
)

# Export root agent for ADK runtime
# This is the entry point for the agent system
root_agent = health_coordinator

logger.info("All agents initialized successfully")
logger.info("Health Journal Agent ready to serve")
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Any, Literal, Optional
from pydantic import BaseModel, Field

from google.adk.agents import Agent
from google.adk.apps import App, ResumabilityConfig
from google.adk.models import Gemini
from google.adk.tools import FunctionTool
from google.genai import types

# Import the custom culinary tools
from app.tools import (
    list_household_members,
    get_household_member_profile,
    get_meal_history,
    add_meal_to_history,
    get_preferred_blogs,
    search_recipe_blogs,
    get_current_date,
    send_meal_plan_email,
    confirm_and_execute_meal_plan
)

# ==========================================
# Replay fallback tools to prevent ValueError during session restoration
# ==========================================
def fallback_planner_agent(request: str) -> Dict[str, Any]:
    """Fallback tool representing the planner sub-agent. This is used to prevent tool lookup errors during session replay."""
    return {"status": "success", "message": "Replay fallback"}
fallback_planner_agent.__name__ = "planner_agent"

def fallback_chef_agent(request: str) -> Dict[str, Any]:
    """Fallback tool representing the chef sub-agent. This is used to prevent tool lookup errors during session replay."""
    return {"status": "success", "message": "Replay fallback"}
fallback_chef_agent.__name__ = "chef_agent"

def fallback_takeout_concierge_agent(request: str) -> Dict[str, Any]:
    """Fallback tool representing the takeout concierge sub-agent. This is used to prevent tool lookup errors during session replay."""
    return {"status": "success", "message": "Replay fallback"}
fallback_takeout_concierge_agent.__name__ = "takeout_concierge_agent"

def fallback_shopping_assistant_agent(request: str) -> Dict[str, Any]:
    """Fallback tool representing the shopping assistant sub-agent. This is used to prevent tool lookup errors during session replay."""
    return {"status": "success", "message": "Replay fallback"}
fallback_shopping_assistant_agent.__name__ = "shopping_assistant_agent"

def fallback_historian_agent(request: str) -> Dict[str, Any]:
    """Fallback tool representing the historian sub-agent. This is used to prevent tool lookup errors during session replay."""
    return {"status": "success", "message": "Replay fallback"}
fallback_historian_agent.__name__ = "historian_agent"

replay_fallback_tools = [
    fallback_planner_agent,
    fallback_chef_agent,
    fallback_takeout_concierge_agent,
    fallback_shopping_assistant_agent,
    fallback_historian_agent
]

# ==========================================
# 1. Pydantic Schemas for Structured Delegation
# ==========================================

# --- Planner Schemas ---
class DailyMeal(BaseModel):
    day: str = Field(description="Name of the day (e.g., Monday, Tuesday, etc.)")
    dish: str = Field(description="Name of the home-cooked dish or leftovers planned for this day.")
    protein_type: Literal["Beef", "Chicken", "Pork", "Seafood", "Vegetarian", "Other"] = Field(description="Type of protein in this meal.")
    effort_level: Literal["Low", "Medium", "High"] = Field(description="The level of time/effort commitment required to prep and cook this dish.")
    prep_time_minutes: int = Field(description="Estimated preparation and active cooking time in minutes.")
    cooking_leader: Literal["T.J.", "Nikki", "None (Leftovers)", "None (Takeout)"] = Field(description="Who will do the cooking, or leftovers/takeout.")
    eaters: List[str] = Field(description="List of family members who will eat this meal (e.g., T.J., Nikki, Jackson, Alice, Daphne).")
    rationale: str = Field(description="Why this dish was chosen and how it respects preferences, accommodates kid dislikes (e.g. no visible onions/greens for Jackson/Daphne, or custom adjustments), and matches protein/effort goals.")

class WeeklyMealPlan(BaseModel):
    plan: List[DailyMeal] = Field(description="The planned dinner menu.")
    variety_explanation: str = Field(description="How this plan introduces variety and avoids repeating recent dishes from the meal history. The favorite dishes list should be a guide, not a strict limit.")
    leftover_day: Optional[str] = Field(None, description="Which day was designated as the leftover day, if any.")
    target_effort_explanation: str = Field(description="Explanation of the effort levels assigned to specific days (incorporating any specific user requests, or explaining the default mix of high, medium, and low effort).")
    protein_distribution: Dict[str, int] = Field(description="A count of the protein types used across the home-cooked days to ensure a healthy, balanced mix.")

# --- Recipe Sourcing Schema (Chef Agent) ---
class RecipeResearchResult(BaseModel):
    dish: str = Field(description="Name of the dish searched.")
    blog_source: str = Field(description="The preferred blog site the recipe was sourced from (e.g. Serious Eats, Smitten Kitchen, Half Baked Harvest).")
    recipe_title: str = Field(description="The official title of the recipe.")
    ingredients: List[str] = Field(description="List of required ingredients.")
    steps: List[str] = Field(description="Numbered step-by-step cooking instructions.")
    source_url: str = Field(description="Simulated URL of the recipe source.")
    cooking_tips: List[str] = Field(description="Special chef tips from the blog to ensure success.")

# --- Takeout Concierge Schemas ---
class TakeoutDay(BaseModel):
    day: str = Field(description="Takeout day (e.g., Friday, Saturday).")
    restaurant: str = Field(description="The selected takeout restaurant (must be from the favorites of the active eaters).")
    cuisine: str = Field(description="Cuisine type (e.g., Thai, Japanese, Italian, Burgers).")
    ordered_items: List[str] = Field(description="Specific items ordered for each active family member based on their favorite dishes and dislikes (T.J., Nikki, Jackson, Alice, Daphne).")
    eaters: List[str] = Field(description="Family members participating in this takeout order.")
    rationale: str = Field(description="Explanation of how this choice accommodates tastes and matches likes/dislikes.")

class TakeoutPlan(BaseModel):
    takeouts: List[TakeoutDay] = Field(description="Takeout choices for the week.")

# --- Shopping Assistant Schema ---
class ShoppingList(BaseModel):
    items_by_category: Dict[str, List[str]] = Field(description="Categorized list of groceries needed for all cooked dishes (e.g. 'Produce', 'Meat & Seafood', 'Dairy', 'Pantry').")
    substitution_suggestions: List[str] = Field(description="Suggestions for standard household substitutions, kid-friendly adjustments, or common pantry staples.")

# --- Historian Schemas ---
class LoggedMeal(BaseModel):
    date: str = Field(description="Date of the meal (YYYY-MM-DD).")
    dish: str = Field(description="Dish or restaurant meal logged.")
    meal_type: Literal["dinner", "takeout"] = Field(description="Type of meal.")
    eaters: List[str] = Field(description="Family members who ate the meal.")
    restaurant: Optional[str] = Field(None, description="The restaurant name (for takeout).")
    notes: str = Field("", description="Optional notes on how the meal went.")

class HistoricalSaveResult(BaseModel):
    saved_entries: List[LoggedMeal] = Field(description="List of logged entries successfully written to persistent storage.")
    status: str = Field(description="Overall status of the write operation.")

# ==========================================
# 2. Subagent Definitions (ADK Task Mode)
# ==========================================

planner_agent = Agent(
    name="planner_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    mode="task",
    output_schema=WeeklyMealPlan,
    description="Plans dinner meals for a requested duration (default 1 week) ensuring protein diversity, customized daily effort levels (Low/Medium/High), and accommodating individual dislikes.",
    instruction=(
        "You are the Master Meal Planner. Your task is to draft a weekly dinner proposal for the Peters family (T.J., Nikki, Jackson, Alice, Daphne).\n\n"
        "To perform this task successfully, you MUST:\n"
        "1. List the household members using `list_household_members` and load each of their profiles using `get_household_member_profile` to read their favorite dishes, preferred blogs, and absolute dislikes.\n"
        "2. Retrieve the recent dinner history using `get_meal_history` to ensure you do not repeat any dishes eaten recently (this ensures variety!).\n"
        "3. Incorporate the planning length (how many days/weeks, defaulting to 1 week) and which day(s) should be takeout or leftovers.\n"
        "4. Plan cooking days by assigning either T.J. or Nikki to cook. Ensure that who is eating that dish actually likes it (e.g., Jackson, Alice, and Daphne are kids with strict dislikes like spicy food, visible onions, and seafood. Ensure there is something on the menu every day that they will eat, or note a custom simple alternative like butter pasta or quesadilla for them if a parent-friendly meal is planned).\n"
        "5. Balance the proteins! Ensure a diverse mix of proteins (e.g., chicken, beef, pork, vegetarian, seafood) rather than repeating the same protein consecutively.\n"
        "6. Handle Effort Level requests:\n"
        "   - Check the user's instructions for any specific daily effort requests (e.g. 'Make Tuesday low effort' or 'I want Wednesday to be low effort').\n"
        "   - If no specific effort level is requested for a day, default to a varied mix of Low, Medium, and High effort dishes across the cooked days of the week (e.g. one High effort meal like slow-cooked pork/beef or complex homemade pasta, some Medium effort meals, and some Low effort meals).\n"
        "7. Note: Family favorite dishes are a guide, not a strict limit. Feel free to introduce new, interesting dishes that fit their flavor preferences!\n"
        "8. Once your plan is complete, format it into the WeeklyMealPlan schema and return it."
    ),
    tools=[list_household_members, get_household_member_profile, get_meal_history, get_current_date] + replay_fallback_tools
)

chef_agent = Agent(
    name="chef_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    mode="task",
    output_schema=RecipeResearchResult,
    description="Researches and fetches detailed recipes from the parents' preferred home-cooking blogs (Serious Eats, Smitten Kitchen, Half Baked Harvest, Kenji's Grid) for a specific dish.",
    instruction=(
        "You are the Chef Agent. Your task is to find a premium recipe for a requested dish.\n\n"
        "To perform this task:\n"
        "1. Retrieve the list of preferred blogs using `get_preferred_blogs`.\n"
        "2. Run a search for the requested dish on one of those preferred blogs using `search_recipe_blogs`. If the dish is best suited for a parent's specific blog (e.g., T.J. prefers Serious Eats and Kenji's Grid; Nikki prefers Smitten Kitchen and Half Baked Harvest), target that blog specifically!\n"
        "3. Extract and synthesize the recipe title, list of ingredients, cooking steps, source URL (with working link), and append helpful chef tips.\n"
        "4. Return the recipe structured in the RecipeResearchResult schema."
    ),
    tools=[get_preferred_blogs, search_recipe_blogs] + replay_fallback_tools
)

takeout_concierge_agent = Agent(
    name="takeout_concierge_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    mode="task",
    output_schema=TakeoutPlan,
    description="Plans takeout orders for designated takeout days based on family member restaurant favorites and preferred items.",
    instruction=(
        "You are the Takeout Concierge. Your task is to plan takeout meals for Friday, Saturday, or other user-designated takeout days.\n\n"
        "To perform this task:\n"
        "1. List and retrieve the profiles of all family members (T.J., Nikki, Jackson, Alice, Daphne) using `list_household_members` and `get_household_member_profile`.\n"
        "2. Identify their favorite takeout restaurants and what dishes they love or dislike.\n"
        "3. Select a restaurant for each requested takeout day that accommodates the entire family (especially the kids Jackson, Alice, and Daphne, who have distinct favorites at Pizza Bella, Burger Town, and Taco Loco).\n"
        "4. Design the specific ordered items for each active family member.\n"
        "5. Return the finalized plan structured in the TakeoutPlan schema."
    ),
    tools=[list_household_members, get_household_member_profile] + replay_fallback_tools
)

shopping_assistant_agent = Agent(
    name="shopping_assistant_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    mode="task",
    output_schema=ShoppingList,
    description="Compiles a comprehensive, categorized shopping list based on the ingredients of the selected recipes.",
    instruction=(
        "You are the Shopping Assistant. Your task is to analyze the ingredients of all planned, cooked recipes and compile a clean, unified grocery shopping list.\n\n"
        "To perform this task:\n"
        "1. Review the lists of ingredients from each of the researched recipes.\n"
        "2. Combine duplicate or overlapping items (e.g., if multiple recipes use garlic or olive oil, list them cleanly).\n"
        "3. Organize the items into intuitive, store-friendly categories (e.g. Produce, Meat & Seafood, Dairy, Bakery, Pantry, Spices/Baking).\n"
        "4. Provide intelligent substitution suggestions, kid-friendly adjustments, or common pantry items the user might already have.\n"
        "5. Return the list structured in the ShoppingList schema."
    ),
    tools=[] + replay_fallback_tools
)

historian_agent = Agent(
    name="historian_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    mode="task",
    output_schema=HistoricalSaveResult,
    description="Saves and records consumed meals and takeout details to persistent history storage.",
    instruction=(
        "You are the Culinary Historian. Your task is to log the planned or eaten dinners to persistent storage so the family can track their consumption.\n\n"
        "To perform this task:\n"
        "1. Retrieve the current date using `get_current_date` to understand what today's date is.\n"
        "2. Deduce the correct YYYY-MM-DD date for each planned meal of the week relative to today (e.g. if today is Tuesday, Monday is yesterday, Wednesday is tomorrow, etc.).\n"
        "3. For each meal (cooked, leftovers, takeout), log it by calling `add_meal_to_history` with the calculated date, dish, eaters, and any notes/restaurant names.\n"
        "4. After successfully logging all items, return the logged entries and status using the HistoricalSaveResult schema."
    ),
    tools=[add_meal_to_history, get_meal_history, get_current_date] + replay_fallback_tools
)

# ==========================================
# 3. Root Agent Definition (Orchestrator with HITL)
# ==========================================

# Wrap the confirmation tool with native ADK require_confirmation
confirm_meal_plan_tool = FunctionTool(
    confirm_and_execute_meal_plan,
    require_confirmation=True
)

root_agent = Agent(
    name="peters_family_culinary_assistant",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Peters Family Culinary Assistant, an elite personal chef and meal planning coordinator.\n"
        "You lead a team of specialized subagents to deliver a premium, high-fidelity human-in-the-loop culinary planning experience for T.J., Nikki, Jackson, Alice, and Daphne.\n\n"
        "### Workflow Guidelines:\n"
        "When a user asks you to plan a week or request a menu:\n\n"
        "#### PHASE 1: Proposal Draft (No persistence, no recipes yet)\n"
        "1. **Identify Constraints**: Extract user preferences from input:\n"
        "   - Length of plan (how many days or weeks, default to 1 week).\n"
        "   - Effort levels requested for specific days (e.g. 'Make Tuesday low effort').\n"
        "   - Which day(s) are takeout days (e.g., 'Friday and Saturday').\n"
        "   - Target recipient email address (e.g., 'tj@example.com'). If none is provided, ask the user or use a sensible mock email like 'tj@example.com'.\n"
        "2. **Draft Cooked/Leftover Proposal**: Call the `planner_agent` with these constraints to generate the menu schedule.\n"
        "3. **Draft Takeout Proposal**: Call the `takeout_concierge_agent` with the specified takeout day constraints.\n"
        "4. **Format & Present Proposal**: Merge these schedules into a beautiful, easy-to-read markdown table showing the proposed dinners, cooking leaders, eaters, and effort levels. Highlight that this is a **PROPOSAL** awaiting their review.\n"
        "5. **Human-in-the-Loop Gate**: Call the `confirm_and_execute_meal_plan` tool. Pass the markdown proposal and target email address. **DO NOT skip this step!** Calling this tool is mandatory to prompt the user for approval.\n"
        "   - Note: If the user approves the tool, you will receive a success response and can proceed to PHASE 2.\n"
        "   - If the user rejects the tool, or requests modifications, report the feedback, DO NOT save anything to history, and invite them to refine the constraints.\n\n"
        "#### PHASE 2: Execution (Only after approval)\n"
        "6. **Sourcing Recipes**: For each home-cooked dish in the approved menu, call the `chef_agent` to research detailed recipes, ingredients, and steps from preferred blogs.\n"
        "7. **Compiling Shopping List**: Collect all the ingredients from the researched recipes and call the `shopping_assistant_agent` to draft a categorized, store-ready grocery list.\n"
        "8. **Logging to History**: Call the `historian_agent` to save the approved menu into your persistent `history.json` on disk.\n"
        "9. **Delivering Email**: Compose the final comprehensive meal guide containing the menu, detailed recipe steps, and the compiled shopping list. Call `send_meal_plan_email` to send it to the provided email address.\n"
        "10. **Final Report**: Present the complete, final compiled guide to the user, showcasing the recipes and shopping list, and let them know that the plan is officially logged and emailed successfully!"
    ),
    sub_agents=[planner_agent, chef_agent, takeout_concierge_agent, shopping_assistant_agent, historian_agent],
    tools=[confirm_meal_plan_tool, send_meal_plan_email]
)

app = App(
    root_agent=root_agent,
    name="app",
    resumability_config=ResumabilityConfig(is_resumable=True)
)

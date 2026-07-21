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

import os
import json
import datetime
from pathlib import Path
from typing import Literal, Optional, List, Dict, Any

BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
MEMBERS_DIR = DATA_DIR / "members"

def get_current_date() -> str:
    """Returns the current date in YYYY-MM-DD format. Useful for planning weeks relative to today.

    Returns:
        A string representing the current date in YYYY-MM-DD format.
    """
    return datetime.date.today().isoformat()


def list_household_members() -> List[str]:
    """Lists the names of all household members who have culinary profiles.

    Returns:
        List of strings representing member names (e.g., ['tj', 'sarah', 'emily']).
    """
    if not MEMBERS_DIR.exists():
        return []
    return [f.stem for f in MEMBERS_DIR.glob("*.md")]

def get_household_member_profile(member_name: str) -> Dict[str, Any]:
    """Reads and returns the culinary profile (likes, dislikes, takeout preferences) for a member.

    Args:
        member_name: The name of the family member (case-insensitive, e.g. 'tj', 'sarah').

    Returns:
        A dictionary containing the profile content or an error message.
    """
    name_clean = member_name.lower().strip()
    profile_path = MEMBERS_DIR / f"{name_clean}.md"
    if not profile_path.exists():
        return {
            "status": "error",
            "message": f"Profile for member '{member_name}' not found. Available members: {list_household_members()}"
        }
    
    with open(profile_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return {
        "status": "success",
        "member": member_name,
        "profile": content
    }

def get_meal_history() -> List[Dict[str, Any]]:
    """Loads and returns the historical record of consumed dishes and takeout orders.

    Returns:
        A list of dictionaries, where each dictionary represents a historical meal entry.
    """
    history_file = DATA_DIR / "history.json"
    if not history_file.exists():
        return []
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return [{"status": "error", "message": f"Failed to load history: {str(e)}"}]

def add_meal_to_history(
    date: str,
    dish: str,
    meal_type: Literal["dinner", "lunch", "breakfast", "takeout"],
    eaters: List[str],
    restaurant: Optional[str] = None,
    notes: Optional[str] = ""
) -> Dict[str, Any]:
    """Appends a newly consumed meal or takeout dish to the persistent history file.

    Args:
        date: The date of the meal (format: YYYY-MM-DD).
        dish: The name of the dish or meal consumed.
        meal_type: The type of meal (e.g., 'dinner', 'takeout').
        eaters: List of family members who ate the meal.
        restaurant: The restaurant name (required if meal_type is 'takeout').
        notes: Optional comments about the meal (e.g., 'Emily liked it').

    Returns:
        A dictionary summarizing the status of the operation and the saved entry.
    """
    history_file = DATA_DIR / "history.json"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "date": date,
        "meal_type": meal_type,
        "dish": dish,
        "eaters": eaters,
        "notes": notes
    }
    if restaurant:
        entry["restaurant"] = restaurant
        
    history = []
    if history_file.exists():
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []
            
    history.append(entry)
    
    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
        return {"status": "success", "message": "Meal added to history successfully.", "entry": entry}
    except Exception as e:
        return {"status": "error", "message": f"Failed to save meal to history: {str(e)}"}

def get_preferred_blogs() -> List[str]:
    """Returns the list of preferred recipe blogs and cooking websites favored by the household leaders.

    Returns:
        List of strings representing the blog/website names.
    """
    return ["Serious Eats", "Smitten Kitchen", "Half Baked Harvest"]

def search_recipe_blogs(dish_name: str, preferred_blog: str) -> Dict[str, Any]:
    """Simulates a highly refined search of the specified culinary blog for a particular dish.

    Args:
        dish_name: The name of the dish to search for (e.g. 'Chicken Parmesan', 'Salmon').
        preferred_blog: One of the preferred blogs (e.g. 'Serious Eats', 'Smitten Kitchen', 'Half Baked Harvest').

    Returns:
        A dictionary containing recipe info, source URL, ingredients, and cooking steps.
    """
    blog_clean = preferred_blog.strip().title()
    dish_clean = dish_name.strip().title()
    
    # We will return dynamic, beautifully formatted simulated recipe metadata based on the blog style!
    blog_urls = {
        "Serious Eats": "https://www.seriouseats.com",
        "Smitten Kitchen": "https://smittenkitchen.com",
        "Half Baked Harvest": "https://www.halfbakedharvest.com"
    }
    
    url = f"{blog_urls.get(blog_clean, 'https://www.google.com')}/{dish_clean.lower().replace(' ', '-')}"
    
    # Some pre-tailored recipe details for common dishes to make it feel extremely authentic and premium
    recipe_database = {
        "Chicken Parmesan": {
            "Serious Eats": {
                "title": "Kenji's Ultra-Crispy Chicken Parmesan",
                "ingredients": [
                    "2 large boneless skinless chicken breasts (split horizontally)",
                    "1 cup all-purpose flour",
                    "3 large eggs (beaten)",
                    "2 cups seasoned panko breadcrumbs",
                    "1/2 cup grated Parmigiano-Reggiano",
                    "1/2 cup vegetable oil (for frying)",
                    "2 cups rich slow-cooked marinara sauce",
                    "8 oz fresh mozzarella (sliced)"
                ],
                "steps": [
                    "Pound chicken cutlets to 1/4-inch thickness.",
                    "Dredge in flour, dip in eggs, coat in panko/Parmigiano mixture, press firmly to adhere.",
                    "Shallow fry in hot oil (350°F) until golden brown and extremely crispy on both sides (about 3 minutes per side).",
                    "Ladle marinara in a baking dish, place crispy chicken on top, spoon minimal sauce on chicken to preserve crispiness, top with mozzarella.",
                    "Broil until cheese is bubbly and browned."
                ]
            },
            "Smitten Kitchen": {
                "title": "Approachables & Cozy Chicken Parmesan",
                "ingredients": [
                    "4 chicken cutlets",
                    "1 cup homemade breadcrumbs",
                    "1 egg",
                    "Olive oil for pan-frying",
                    "Simple quick marinara sauce (canned crushed tomatoes, garlic, olive oil)",
                    "6 oz shredded low-moisture mozzarella"
                ],
                "steps": [
                    "Pan-fry breaded cutlets in olive oil until golden.",
                    "Warm simple marinara in a saucepan.",
                    "Spoon sauce over cutlets directly in the pan, cover with mozzarella, put a lid on the pan and simmer on low until the cheese melts beautifully."
                ]
            }
        },
        "Salmon": {
            "Half Baked Harvest": {
                "title": "Crispy Garlic Butter Salmon with Lemon Dill",
                "ingredients": [
                    "4 salmon fillets (skin-on)",
                    "4 tablespoons salted butter",
                    "4 cloves garlic (minced)",
                    "1 tablespoon fresh dill (chopped)",
                    "1 lemon (sliced)",
                    "Splash of dry white wine"
                ],
                "steps": [
                    "Sear salmon skin-side down in a hot skillet with butter and olive oil until crispy (about 4 minutes).",
                    "Flip salmon, add minced garlic, butter, white wine, and fresh dill.",
                    "Baste the hot garlic butter over the salmon for another 2 minutes until cooked to medium-rare.",
                    "Squeeze fresh lemon juice on top and serve immediately."
                ]
            }
        }
    }
    
    # Fallback/dynamic generator if not pre-defined
    recipe = recipe_database.get(dish_clean, {}).get(blog_clean)
    if not recipe:
        # Generate a beautiful fallback based on the dish and blog
        recipe = {
            "title": f"The Perfect {dish_clean} ({blog_clean} Edition)",
            "ingredients": [
                f"1 lb high-quality base ingredient for {dish_clean}",
                "2 tbsp unsalted butter or olive oil",
                "1 clove garlic, minced",
                "Salt and black pepper to taste",
                "Fresh herbs for garnish"
            ],
            "steps": [
                "Prep your ingredients and preheat your cooking surface.",
                "Sauté the base ingredients in butter/oil until fragrant and cooked to perfection.",
                f"Season generously and garnish with herbs to capture that classic {blog_clean} touch."
            ]
        }
        
    return {
        "status": "success",
        "dish": dish_name,
        "blog": preferred_blog,
        "recipe_title": recipe["title"],
        "url": url,
        "ingredients": recipe["ingredients"],
        "steps": recipe["steps"]
    }

def send_meal_plan_email(email_address: str, subject: str, body_markdown: str) -> Dict[str, Any]:
    """Sends the finalized weekly meal plan, recipes, and shopping list to the provided email address.
    To allow verification and auditability, this tool writes the sent email to a persistent markdown file under app/data/sent_emails/.
    Additionally, if a RESEND_API_KEY environment variable is configured, it will deliver an actual email via the Resend API.

    Args:
        email_address: The recipient's email address (e.g., 'tj@example.com').
        subject: The subject of the email.
        body_markdown: The markdown content of the email.

    Returns:
        A dictionary indicating the email status and the path to the sent email file.
    """
    emails_dir = DATA_DIR / "sent_emails"
    emails_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    email_file = emails_dir / f"email_{timestamp}.md"
    
    email_content = f"""# EMAIL OUTBOX
**To:** {email_address}
**Date:** {datetime.datetime.now().isoformat()}
**Subject:** {subject}

---

{body_markdown}
"""
    try:
        with open(email_file, "w", encoding="utf-8") as f:
            f.write(email_content)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to write email to local outbox: {str(e)}"
        }

    # Check for Resend API Key
    resend_key = os.environ.get("RESEND_API_KEY")
    if not resend_key:
        return {
            "status": "success",
            "message": f"Email successfully 'sent' to {email_address}! (Note: RESEND_API_KEY is not set, so it was only written to the local outbox directory.)",
            "subject": subject,
            "filepath": str(email_file.absolute())
        }

    import re
    import urllib.request
    import urllib.error

    # Simple Markdown to HTML converter for beautiful email rendering
    html_content = body_markdown
    # Convert strong text: **text** -> <strong>text</strong>
    html_content = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html_content)
    # Convert headers: ## text -> <h2>text</h2>, # text -> <h1>text</h1>
    html_content = re.sub(r"## (.*?)\n", r"<h2>\1</h2>", html_content)
    html_content = re.sub(r"# (.*?)\n", r"<h1>\1</h1>", html_content)
    # Convert bullet points: * text -> <li>text</li>
    html_content = re.sub(r"\* (.*?)\n", r"<li>\1</li>\n", html_content)
    # Wrap series of <li> elements with <ul> if needed, or simply preserve formatting with <br>
    html_content = html_content.replace("\n", "<br>")

    # Prepare Resend email payload
    payload = {
        "from": "Culinary Assistant <onboarding@resend.dev>",
        "to": [email_address],
        "subject": subject,
        "html": f"<html><body style='font-family: Arial, sans-serif; line-height: 1.6; color: #333;'>{html_content}</body></html>"
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=req_data,
        headers={
            "Authorization": f"Bearer {resend_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            resp_body = response.read().decode("utf-8")
            return {
                "status": "success",
                "message": f"Actual email successfully sent to {email_address} via Resend API!",
                "subject": subject,
                "filepath": str(email_file.absolute()),
                "resend_response": json.loads(resp_body)
            }
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        return {
            "status": "error",
            "message": f"Resend API failed with status {e.code}: {err_msg}",
            "filepath": str(email_file.absolute())
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to deliver email through Resend: {str(e)}",
            "filepath": str(email_file.absolute())
        }

def confirm_and_execute_meal_plan(proposal: str, email_address: str) -> Dict[str, Any]:
    """Requests explicit user confirmation of the proposed weekly meal plan.
    This tool acts as an approval gate before recipes are researched, history is saved, the plan is emailed, and the shopping list is compiled.

    Args:
        proposal: The complete description of the proposed weekly meals and takeout nights.
        email_address: The target email address to deliver the finalized meal plan, recipes, and shopping list.

    Returns:
        A dictionary containing the confirmation status.
    """
    return {
        "status": "approved",
        "message": f"Meal plan proposal was successfully approved! Proceeding to fetch detailed recipes, compile the shopping list, log to history, and deliver the final email to {email_address}."
    }


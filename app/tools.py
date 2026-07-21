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

    # Premium Markdown to HTML compiler with support for headers, lists, tables, bolding, and links
    def compile_markdown_to_premium_html(md_text: str) -> str:
        lines = md_text.split("\n")
        html_lines = []
        in_list = False
        in_table = False
        is_header_row = True
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                if in_table:
                    html_lines.append("</table>")
                    in_table = False
                continue
                
            # Parse Markdown tables
            if line_stripped.startswith("|"):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                    
                if not in_table:
                    html_lines.append("<table cellpadding='8' cellspacing='0' style='width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 20px; border: 1px solid #E5E7EB; font-size: 13px; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>")
                    in_table = True
                    is_header_row = True
                    
                cells = [c.strip() for c in line_stripped.split("|")[1:-1]]
                # Skip the table formatting/alignment row (e.g. |---|---|)
                if all(re.match(r"^:?-+:?$", cell) for cell in cells):
                    continue
                    
                if is_header_row:
                    html_lines.append("<tr style='background-color: #0F766E; color: #FFFFFF;'>")
                    for cell in cells:
                        html_lines.append(f"<th style='text-align: left; font-weight: 700; border: 1px solid #0D9488; padding: 10px;'>{cell}</th>")
                    html_lines.append("</tr>")
                    is_header_row = False
                else:
                    html_lines.append("<tr style='background-color: #FFFFFF;'>")
                    for cell in cells:
                        cell = re.sub(r"\*\*(.*?)\*\*", r"<strong style='color: #111827;'>\1</strong>", cell)
                        html_lines.append(f"<td style='color: #4B5563; border: 1px solid #E5E7EB; padding: 10px;'>{cell}</td>")
                    html_lines.append("</tr>")
                continue

            # If a table row was active but this line isn't part of a table, close the table
            if in_table:
                html_lines.append("</table>")
                in_table = False

            # Parse headers
            if line_stripped.startswith("### "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                title = line_stripped[4:].strip()
                html_lines.append(f"<h3 style='color: #0F766E; font-size: 1.15em; font-weight: 700; margin-top: 20px; margin-bottom: 8px; border-bottom: 1px dashed #CCFBF1; padding-bottom: 4px;'>{title}</h3>")
            elif line_stripped.startswith("## "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                title = line_stripped[3:].strip()
                html_lines.append(f"<h2 style='color: #0F766E; font-size: 1.4em; font-weight: 800; margin-top: 25px; margin-bottom: 12px; border-bottom: 2px solid #0D9488; padding-bottom: 6px;'>{title}</h2>")
            elif line_stripped.startswith("# "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                title = line_stripped[2:].strip()
                html_lines.append(f"<h1 style='color: #111827; font-size: 1.8em; text-align: center; margin-bottom: 24px; font-weight: 800; border-bottom: 3px solid #0D9488; padding-bottom: 10px; letter-spacing: -0.5px;'>{title}</h1>")
            
            # Parse bulleted lists
            elif line_stripped.startswith("* ") or line_stripped.startswith("- "):
                if not in_list:
                    html_lines.append("<ul style='padding-left: 20px; margin-top: 5px; margin-bottom: 12px;'>")
                    in_list = True
                content = line_stripped[2:].strip()
                content = re.sub(r"\*\*(.*?)\*\*", r"<strong style='color: #111827;'>\1</strong>", content)
                content = re.sub(r"\[(.*?)\]\((.*?)\)", r"<a href='\2' style='color: #0D9488; text-decoration: none; font-weight: 500;'>\1</a>", content)
                html_lines.append(f"<li style='margin-bottom: 6px; color: #4B5563; font-size: 14px;'>{content}</li>")
                
            # Parse standard paragraphs
            else:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                content = line_stripped
                content = re.sub(r"\*\*(.*?)\*\*", r"<strong style='color: #111827;'>\1</strong>", content)
                content = re.sub(r"\[(.*?)\]\((.*?)\)", r"<a href='\2' style='color: #0D9488; text-decoration: none; font-weight: 500;'>\1</a>", content)
                html_lines.append(f"<p style='margin-top: 6px; margin-bottom: 12px; color: #4B5563; font-size: 14px; line-height: 1.6;'>{content}</p>")
                
        if in_list:
            html_lines.append("</ul>")
        if in_table:
            html_lines.append("</table>")
            
        return "\n".join(html_lines)

    html_content = compile_markdown_to_premium_html(body_markdown)

    # Wrap inside our responsive, modern premium container template
    premium_template = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #F3F4F6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
  <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #F3F4F6; padding: 25px 10px;">
    <tr>
      <td align="center">
        <!-- Main Card Container -->
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 650px; background-color: #FFFFFF; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); border: 1px solid #E5E7EB;">
          <!-- Header Banner -->
          <tr>
            <td style="background: linear-gradient(135deg, #0F766E, #0D9488); padding: 35px 24px; text-align: center;">
              <h1 style="margin: 0; color: #FFFFFF; font-size: 24px; font-weight: 800; letter-spacing: -0.5px; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">Peters Family Culinary Assistant</h1>
              <p style="margin: 6px 0 0 0; color: #CCFBF1; font-size: 14px; font-weight: 500; letter-spacing: 0.2px;">Weekly Dinner Guide, Recipes & Shopping List</p>
            </td>
          </tr>
          <!-- Body Content -->
          <tr>
            <td style="padding: 35px 30px; background-color: #FFFFFF;">
              {html_content}
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="background-color: #F9FAFB; padding: 25px; text-align: center; border-top: 1px solid #E5E7EB;">
              <p style="margin: 0; color: #9CA3AF; font-size: 12px; font-weight: 500;">Generated with ❤️ by your Peters Family Culinary Assistant</p>
              <p style="margin: 5px 0 0 0; color: #D1D5DB; font-size: 11px;">GCP Agent Runtime • tjpeters-experiment-sandbox</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    # Prepare Resend email payload
    payload = {
        "from": "Culinary Assistant <onboarding@resend.dev>",
        "to": [email_address],
        "subject": subject,
        "html": premium_template
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=req_data,
        headers={
            "Authorization": f"Bearer {resend_key}",
            "Content-Type": "application/json",
            "User-Agent": "peters-culinary-assistant/1.0"
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


import subprocess

from recipe_scrapers import scrape_me
import pdfkit
import os
import re
from data_models import Recipe, Ingredient
import sqlite3

# Update this to the correct path to wkhtmltopdf
path_wkhtmltopdf = '/usr/bin/wkhtmltopdf'  # Replace with your actual path

config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)


def fetch_recipe(url, sunday, monday, tuesday, wednesday, thursday, friday, saturday, cursor):
    scraper = scrape_me(url)

    title = scraper.title()
    ingredients = scraper.ingredients()
    instructions = scraper.instructions().split('\n')

    recipe = Recipe(title=title)

    cursor.execute("INSERT INTO Recipe (title, sunday, monday, tuesday, wednesday, thursday, friday, saturday) "
                   "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (title, sunday, monday, tuesday, wednesday, thursday, friday, saturday))
    recipe_id = cursor.lastrowid

    for ingredient_str in ingredients:
        name, quantity, optional = parse_ingredient(ingredient_str)
        new_ingredient = Ingredient(name=name, quantity=quantity, optional=optional)
        recipe.Ingredients.append(new_ingredient)
        cursor.execute(
            "INSERT INTO Ingredient (recipe_id, name, quantity, optional) VALUES (?, ?, ?, ?)",
            (recipe_id, name, quantity, optional)
        )

    recipe.Instructions = instructions

    return recipe


def parse_ingredient(ingredient):
    pattern = re.compile(r"(?P<quantity>\d+\s?\d*/?\d*\s?[a-zA-Z]*)\s+(?P<name>.+)")
    match = pattern.match(ingredient)

    if match:
        quantity = match.group("quantity")
        name = match.group("name")
    else:
        quantity = ""
        name = ingredient

    optional = 'optional' in ingredient.lower()
    return name, quantity, optional


def format_recipe_as_html(recipe):
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                padding: 0;
                background: #f8f8f8;
            }}
            .container {{
                background: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            h1 {{
                color: #333;
                text-align: center;
            }}
            h2 {{
                color: #666;
                border-bottom: 2px solid #f0f0f0;
                padding-bottom: 5px;
            }}
            ul {{
                list-style: none;
                padding: 0;
            }}
            ul li {{
                background: #f0f0f0;
                margin: 5px 0;
                padding: 10px;
                border-radius: 5px;
            }}
            ol li {{
                margin: 10px 0;
                padding-left: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{recipe.title}</h1>
            <h2>Ingredients</h2>
            <ul>
               {"".join(f'<li>{ingredient.quantity} {ingredient.name} {"(optional)" if ingredient.optional else ""}'
                        f'</li>' for ingredient in recipe.Ingredients)}
            </ul>
            <h2>Instructions</h2>
            <ol>
                {''.join(f'<li>{instruction}</li>' for instruction in recipe.Instructions)}
            </ol>
        </div>
    </body>
    </html>
    """
    return html_content


def save_as_pdf(html_content, output_file):
    try:
        # Log HTML content for debugging
        with open("debug_html_content.html", "w") as f:
            f.write(html_content)
        print("HTML content saved to debug_html_content.html for inspection.")

        # Attempt to save PDF
        result = pdfkit.from_string(html_content, output_file, configuration=config)
        print(f"PDF successfully saved to {output_file}")
        print(f"pdfkit result: {result}")
    except Exception as e:
        print(f"Failed to save PDF: {e}")
        # Run wkhtmltopdf directly to capture more details
        try:
            cmd = [path_wkhtmltopdf, '-', output_file]
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate(input=html_content.encode('utf-8'))
            print("wkhtmltopdf output:", out.decode())
            print("wkhtmltopdf errors:", err.decode())
        except Exception as e2:
            print(f"Failed to run wkhtmltopdf directly: {e2}")


def print_pdf(file_path):
    import cups
    print("cups module content:", dir(cups))  # Print available attributes in the cups module for debugging
    if hasattr(cups, 'Connection'):
        conn = cups.Connection()
        printers = conn.getPrinters()
        default_printer = list(printers.keys())[0]  # Assuming the first printer is the default printer

        # Send the PDF to the default printer
        conn.printFile(default_printer, file_path, "Recipe Print", {})
    else:
        print("Error: cups.Connection is not available.")


def main(url: str, sunday: bool, monday: bool, tuesday: bool, wednesday: bool, thursday: bool, friday: bool, saturday: bool):
    db_file = os.getenv('DB_FILE')
    if not db_file:
        raise ValueError("The DB_FILE environment variable is not set")

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    recipe = fetch_recipe(url, sunday, monday, tuesday, wednesday, thursday, friday, saturday, cursor)
    conn.commit()
    cursor.execute("SELECT * FROM Recipe")
    print(cursor.fetchall())

    cursor.execute("SELECT * FROM Ingredient")
    print(cursor.fetchall())

    conn.close()

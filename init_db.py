"""Create and seed recipes.db. Run once to rebuild: python init_db.py"""

import os
import sqlite3
from werkzeug.security import generate_password_hash

if os.path.exists("recipes.db"):
    os.remove("recipes.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL UNIQUE,
    ingredients TEXT NOT NULL,
    instructions TEXT NOT NULL DEFAULT '',
    is_public INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

USERS_SEED = [
    ("JayR", "jayr@example.com", generate_password_hash("Password123!")),
    ("Losin_It", "lost@example.com", generate_password_hash("Password123!")),
    ("senileviking", "viking@example.com", generate_password_hash("Password123!")),
    ("Pepper", "pepper@example.com", generate_password_hash("Password123!")),
    ("BlyMountainChef", "bly@example.com", generate_password_hash("Password123!")),
    ("NightShiftCook", "nightshift@example.com", generate_password_hash("Password123!")),
]

SEED = [
    (
        "Double Guacamole Bacon Smashburger",
        "1/2 lb 80/20 ground chuck, 4 strips thick-cut hickory bacon, 1 ripe avocado, lime juice, diced red onion, cilantro, 2 slices pepper jack cheese, toasted brioche bun, chipotle mayo",
        "Smash two thin beef patties onto a smoking-hot cast iron skillet for 2 minutes per side. Melt pepper jack over both, stack with crispy bacon, fresh smashed guacamole, and chipotle mayo on a butter-toasted brioche bun.",
        1,
    ),
    (
        "Crispy Fried Zucchini Spears & Jalapeno Ranch",
        "3 medium zucchinis cut into spears, 1 cup panko breadcrumbs, 1/2 cup buttermilk, 1 tsp smoked paprika, 1/2 tsp garlic powder, 1/2 cup ranch dressing, 2 tbsp minced pickled jalapenos, dash of cayenne",
        "Dip zucchini spears in seasoned buttermilk, press into panko, and fry at 375F for 3 minutes until golden crunch. Whisk minced jalapenos, brine, and cayenne into cold ranch for dipping.",
        1,
    ),
    (
        "Bench-Side 3 AM Garlic Butter Steak Bites",
        "1 lb sirloin steak cubed, 3 tbsp salted butter, 5 cloves minced garlic, 1 tsp cracked black pepper, fresh rosemary sprig, splash of Worcestershire sauce",
        "Sear steak cubes in screaming-hot cast iron without crowding for 90 seconds. Drop heat, toss in butter, garlic, rosemary, and Worcestershire, and baste for 60 seconds.",
        1,
    ),
    (
        "Blackout Espresso Rubbed Tri-Tip",
        "2.5 lb beef tri-tip, 2 tbsp finely ground dark espresso, 1 tbsp brown sugar, 1 tbsp kosher salt, 2 tsp ancho chili powder, 1 tsp onion powder",
        "Coat tri-tip in espresso rub and rest uncovered in the fridge for 6 hours. Reverse-sear at 225F until internal temp hits 125F, then sear 90 seconds per side over open flame.",
        0,
    ),
    (
        "3 AM Cast-Iron Skillet Chili",
        "2 lbs ground beef, 1 lb hot Italian sausage, 2 cans dark red kidney beans, 28 oz fire-roasted crushed tomatoes, 2 chipotle peppers in adobo, 2 tbsp cumin, 1 tbsp unsweetened cocoa powder, 1 cup beef broth",
        "Brown beef and sausage with diced yellow onion and garlic. Deglaze with beef broth, stir in tomatoes, chipotles, spices, and beans, and simmer low for 2 hours until thick enough to stand a spoon in.",
        1,
    ),
    (
        "Secret family hot sauce",
        "habaneros, garlic, vinegar, a secret ingredient",
        "If we wrote it down here, it wouldn't be a secret.",
        0,
    ),
    (
        "Habanero Garlic Garage Hot Sauce",
        "12 orange habaneros, 6 cloves roasted garlic, 1 cup apple cider vinegar, 1/2 cup shredded carrot, 1 tbsp honey, 1 tsp sea salt",
        "Simmer habaneros, carrot, garlic, vinegar, and salt for 15 minutes until tender. Blend on high with honey until velvety smooth and bottle hot.",
        0,
    ),
    (
        "Loaded Jalapeno Popper Tater Tot Skillet",
        "1 bag crispy tater tots, 6 strips crumbled bacon, 4 oz softened cream cheese, 1 cup shredded sharp cheddar, 3 sliced fresh jalapenos, green onions",
        "Bake tater tots extra crispy in a cast-iron skillet. Dollop cream cheese, scatter cheddar, bacon, and jalapenos over the top, and broil 3 minutes until bubbly.",
        1,
    ),
    (
        "Root Beer Braised Pulled Pork",
        "4 lb pork shoulder, 12 oz glass-bottle root beer, 1 cup smoky BBQ sauce, 1 tbsp smoked paprika, 1 tsp mustard powder, salt, pepper",
        "Rub pork shoulder with spices and sear all sides. Transfer to slow cooker with root beer, cook on low 8 hours, shred with forks, and toss with reduced cooking liquid and BBQ sauce.",
        1,
    ),
    (
        "Iron Skillet Viking Meatballs & Lingonberry Gravy",
        "1 lb ground beef, 1/2 lb ground pork, 1/2 cup breadcrumbs, 1 egg, 1/4 tsp allspice, 1/4 tsp nutmeg, 2 cups beef stock, 1/3 cup heavy cream, 2 tbsp lingonberry jam",
        "Roll spiced meat mixture into 1-inch balls and brown in butter. Whisk flour, beef stock, cream, and lingonberry jam into the pan drippings and simmer meatballs 10 minutes.",
        1,
    ),
    (
        "Smoked Gouda & Bacon Beer Cheese Dip",
        "8 oz shredded smoked gouda, 8 oz sharp cheddar, 1/2 cup dark amber beer, 4 oz cream cheese, 1 tsp Dijon mustard, 4 strips crispy bacon, soft pretzel bites",
        "Warm beer and cream cheese over low heat, whisk in Dijon, then slowly fold in smoked gouda and cheddar until glossy. Top with crumbled bacon and serve immediately.",
        1,
    ),
    (
        "Nordic Cold-Smoked Salmon & Dill Toast",
        "4 slices dark rye bread, 6 oz cold-smoked salmon, 4 oz whipped cream cheese, fresh dill, capers, thinly sliced red onion, lemon wedges",
        "Toast dark rye until crisp, spread thick with whipped cream cheese, layer smoked salmon ribbons, capers, red onion, and fresh dill, and finish with lemon juice.",
        0,
    ),
    (
        "Overnight oats",
        "rolled oats, milk, yogurt, chia seeds, honey",
        "Stir everything together and refrigerate overnight.",
        1,
    ),
    (
        "Overnight Vanilla Espresso Oats",
        "1/2 cup rolled oats, 1/2 cup whole milk, 1/4 cup Greek yogurt, 1 tbsp chia seeds, 1 tbsp pure maple syrup, 1 shot chilled espresso, pinch of sea salt",
        "Whisk all ingredients together in a sealed glass jar until chia seeds are evenly suspended. Refrigerate at least 6 hours and top with shaved dark chocolate before serving.",
        1,
    ),
    (
        "Brown Butter Vanilla Bean Custard",
        "2 cups whole milk, 1/2 cup heavy cream, 4 large egg yolks, 1/3 cup sugar, 3 tbsp unsalted butter, 2 tbsp cornstarch, 1 tsp vanilla bean paste, flaky salt",
        "Brown butter in a saucepan until nutty and golden. Whisk egg yolks, sugar, and cornstarch, temper with hot milk and cream, cook until thick, and fold in brown butter and vanilla.",
        0,
    ),
    (
        "Crispy Lemon Herb Roast Chicken Thighs",
        "6 bone-in skin-on chicken thighs, 2 tbsp olive oil, zest and juice of 1 lemon, 4 smashed garlic cloves, fresh thyme, oregano, kosher salt",
        "Pat chicken skin bone-dry, season aggressively, and roast skin-side up at 425F for 38 minutes until skin shatters like glass and pan juices caramelize.",
        1,
    ),
    (
        "Bly Mountain Hickory Brisket Rub",
        "1/2 cup coarse kosher salt, 1/2 cup 16-mesh black pepper, 2 tbsp smoked paprika, 2 tbsp dark brown sugar, 1 tbsp garlic powder, 1 tbsp mustard seed, 1 tsp cayenne",
        "Grind mustard seed lightly and mix all spices thoroughly. Coat packer brisket heavily and smoke over hickory and white oak at 225F until bark sets dark mahogany.",
        0,
    ),
    (
        "Cast-Iron Campfire Cornbread",
        "1.5 cups yellow cornmeal, 1/2 cup all-purpose flour, 1 tbsp baking powder, 1 tsp salt, 1 cup buttermilk, 2 eggs, 1/4 cup melted bacon drippings, 2 tbsp honey",
        "Preheat a 10-inch cast-iron skillet with bacon drippings in a 425F oven. Whisk wet and dry ingredients just until combined, pour into sizzling skillet, and bake 22 minutes.",
        1,
    ),
    (
        "Maple Bourbon Smoked Pork Belly Burnt Ends",
        "3 lbs skinless pork belly cubed, 1/4 cup BBQ rub, 1/2 cup pure maple syrup, 1/4 cup bourbon, 3 tbsp butter, 1/2 cup apple cider BBQ glaze",
        "Smoke pork belly cubes at 250F for 2.5 hours. Transfer to a foil pan with butter, maple syrup, and bourbon, cover for 90 minutes, then toss with glaze and tack up uncovered for 20 minutes.",
        1,
    ),
    (
        "Graveyard Shift Bacon Egg & Cheese Breakfast Burrito",
        "3 large eggs, 4 strips crispy bacon, 1/2 cup crispy hash browns, 1/2 cup shredded cheddar, 2 tbsp salsa verde, 1 extra-large flour tortilla",
        "Scramble eggs soft in bacon fat, layer onto a warm tortilla with crispy hash browns, crumbled bacon, cheddar, and salsa verde, roll tight, and toast seam-side down in a dry skillet.",
        1,
    ),
    (
        "15-Minute Spicy Garlic Chili Oil Noodles",
        "8 oz wide wheat noodles, 3 tbsp chili crisp oil, 2 tbsp soy sauce, 1 tbsp black vinegar, 1 tsp sugar, 3 cloves grated garlic, sliced scallions, toasted sesame seeds",
        "Boil noodles until chewy. Whisk chili oil, soy sauce, black vinegar, sugar, and grated garlic in a bowl, toss hot noodles directly into the sauce, and top with scallions and sesame.",
        1,
    ),
    (
        "Salted Caramel Dark Chocolate Skillet Cookie",
        "1/2 cup browned butter, 3/4 cup dark brown sugar, 1/4 cup white sugar, 1 egg plus 1 yolk, 1.25 cups flour, 1/2 tsp baking soda, 1 cup dark chocolate chunks, flaky sea salt",
        "Cream cooled brown butter with sugars and eggs, fold in dry ingredients and chocolate chunks, press into an 8-inch cast-iron skillet, bake at 350F for 18 minutes, and finish with flaky salt.",
        1,
    ),
]

connection = sqlite3.connect("recipes.db")
connection.executescript(SCHEMA)

connection.executemany(
    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
    USERS_SEED,
)
connection.executemany(
    "INSERT INTO recipes (title, ingredients, instructions, is_public) VALUES (?, ?, ?, ?)",
    SEED,
)

connection.commit()
print(f"Created recipes.db with {len(USERS_SEED)} users and {len(SEED)} recipes.")
connection.close()


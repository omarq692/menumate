$(document).ready(function() {
    // 1) Recipe data keyed by data‑recipe‑id on each card
    const recipes = {
      1: {
        title: 'Spinach and Feta Breakfast Scramble',
        img: 'assets/img/recipes/Spinach-Feta-Breakfast-Scramble.png',
        desc: 'A fluffy scramble loaded with spinach, tangy feta, and fresh tomato.',
        instructions: `
          <h6>Ingredients:</h6>
          <ul>
            <li>2 large eggs</li>
            <li>1 cup fresh spinach, chopped</li>
            <li>1/4 cup feta cheese, crumbled</li>
            <li>1 small tomato, diced</li>
            <li>1/4 teaspoon garlic powder</li>
            <li>Salt and pepper, to taste</li>
            <li>1 teaspoon olive oil</li>
          </ul>
          <h6>Instructions:</h6>
          <ol>
            <li>Heat the olive oil in a non‑stick skillet over medium heat.</li>
            <li>Add the chopped spinach and sauté for 1–2 minutes until wilted.</li>
            <li>In a bowl, whisk the eggs with garlic powder, salt, and pepper.</li>
            <li>Pour eggs over the spinach; let sit briefly, then gently scramble.</li>
            <li>When nearly set, stir in diced tomato and feta cheese.</li>
            <li>Cook another minute until eggs are fully cooked and feta soft.</li>
            <li>Remove from heat and serve immediately.</li>
          </ol>
        `,
        nutrition: `
          <h6>Nutritional Information (per serving):</h6>
          <ul>
            <li>Calories: Approximately 250</li>
            <li>Protein: 15g</li>
            <li>Carbohydrates: 6g</li>
            <li>Fat: 18g</li>
          </ul>
        `
      },
      2: {
        title: 'Quinoa and Black Bean Salad',
        img: 'assets/img/recipes/Quinoa-Black-Bean-Salad.png',
        desc: 'A zesty, protein-rich salad with quinoa, black beans, fresh veggies, and lime-cilantro dressing.',
        instructions: `
          <h6>Ingredients:</h6>
          <ul>
            <li>1 cup quinoa, rinsed</li>
            <li>2 cups water</li>
            <li>1 (15 oz) can black beans, drained and rinsed</li>
            <li>1 medium red bell pepper, diced</li>
            <li>1/2 red onion, finely chopped</li>
            <li>1 avocado, diced</li>
            <li>1/4 cup fresh cilantro, chopped</li>
            <li>1/4 cup lime juice</li>
            <li>2 tablespoons olive oil</li>
            <li>1 teaspoon ground cumin</li>
            <li>1/2 teaspoon chili powder</li>
            <li>Salt and pepper, to taste</li>
          </ul>
          <h6>Instructions:</h6>
          <ol>
            <li>Bring water to a boil, add quinoa, reduce heat, cover, and simmer 15–20 minutes until tender.</li>
            <li>Fluff quinoa and let cool for 5 minutes.</li>
            <li>Combine quinoa, black beans, bell pepper, and onion in a bowl.</li>
            <li>Whisk lime juice, olive oil, cumin, chili powder, salt, and pepper; pour over salad.</li>
            <li>Toss gently; fold in avocado and cilantro.</li>
            <li>Serve chilled or at room temperature.</li>
          </ol>
        `,
        nutrition: `
          <h6>Nutritional Information (per serving):</h6>
          <ul>
            <li>Calories: Approximately 220</li>
            <li>Protein: 9g</li>
            <li>Carbohydrates: 35g</li>
            <li>Fat: 7g</li>
          </ul>
        `
      },
      3: {
        title: 'Grilled Chicken and Vegetable Kabobs',
        img: 'assets/img/recipes/Grilled-Chicken-Vegetable-Kabobs.png',
        desc: 'Juicy chicken skewers with colorful veggies, marinated in a lemon-garlic herb blend.',
        instructions: `
          <h6>Ingredients:</h6>
          <ul>
            <li>2 boneless chicken breasts, cubed</li>
            <li>1 zucchini, sliced</li>
            <li>1 red bell pepper, chunked</li>
            <li>1 yellow bell pepper, chunked</li>
            <li>1 red onion, chunked</li>
            <li>Wooden or metal skewers</li>
            <li>2 tablespoons olive oil</li>
            <li>2 tablespoons lemon juice</li>
            <li>1 teaspoon garlic powder</li>
            <li>1 teaspoon dried oregano</li>
            <li>Salt and pepper, to taste</li>
          </ul>
          <h6>Instructions:</h6>
          <ol>
            <li>Marinate chicken in olive oil, lemon juice, garlic, oregano, salt, and pepper for 30+ minutes.</li>
            <li>Preheat grill to medium-high heat.</li>
            <li>Thread chicken and veggies onto skewers.</li>
            <li>Grill 10–15 minutes, turning occasionally until cooked and tender.</li>
            <li>Serve hot with rice or salad.</li>
          </ol>
        `,
        nutrition: `
          <h6>Nutritional Information (per serving):</h6>
          <ul>
            <li>Calories: Approximately 250</li>
            <li>Protein: 26g</li>
            <li>Carbohydrates: 15g</li>
            <li>Fat: 10g</li>
          </ul>
        `
      },
      4: {
        title: 'Baked Salmon with Herb Crust',
        img: 'assets/img/recipes/Baked-Salmon-Herb-Crust.png',
        desc: 'Tender salmon fillets topped with a crispy herb breadcrumb crust.',
        instructions: `
          <h6>Ingredients:</h6>
          <ul>
            <li>4 salmon fillets (6 oz each)</li>
            <li>2 tablespoons Dijon mustard</li>
            <li>1 cup whole wheat breadcrumbs</li>
            <li>2 tablespoons chopped fresh parsley</li>
            <li>1 tablespoon chopped fresh dill</li>
            <li>Zest of 1 lemon</li>
            <li>2 garlic cloves, minced</li>
            <li>Salt and pepper, to taste</li>
            <li>Olive oil spray</li>
          </ul>
          <h6>Instructions:</h6>
          <ol>
            <li>Preheat oven to 400°F (200°C).</li>
            <li>Line a baking sheet with parchment; place salmon skin-side down.</li>
            <li>Spread mustard on top of each fillet.</li>
            <li>Mix breadcrumbs, parsley, dill, lemon zest, garlic, salt, and pepper.</li>
            <li>Press crumb mixture onto salmon; lightly spray with olive oil.</li>
            <li>Bake 12–15 minutes until salmon is cooked and crust is golden.</li>
            <li>Serve with steamed veggies or salad.</li>
          </ol>
        `,
        nutrition: `
          <h6>Nutritional Information (per serving):</h6>
          <ul>
            <li>Calories: Approximately 300</li>
            <li>Protein: 35g</li>
            <li>Carbohydrates: 15g</li>
            <li>Fat: 12g</li>
          </ul>
        `
      },
      5: {
        title: 'Apple and Walnut Spinach Salad',
        img: 'assets/img/recipes/Apple-Walnut-Spinach-Salad.png',
        desc: 'Crisp spinach tossed with sweet apples, crunchy walnuts, and creamy cheese.',
        instructions: `
          <h6>Ingredients:</h6>
          <ul>
            <li>4 cups fresh spinach leaves</li>
            <li>1 apple, cored and thinly sliced</li>
            <li>1/2 cup walnuts, chopped</li>
            <li>1/4 cup crumbled goat or feta cheese</li>
            <li>1/4 red onion, thinly sliced</li>
          </ul>
          <h6>Instructions:</h6>
          <ol>
            <li>Combine spinach, apple slices, walnuts, cheese, and onion in a bowl.</li>
            <li>Whisk olive oil, vinegar, mustard, honey, salt, and pepper for dressing.</li>
            <li>Drizzle dressing over salad and toss gently.</li>
            <li>Serve immediately for maximum freshness.</li>
          </ol>
        `,
        nutrition: `
          <h6>Nutritional Information (per serving):</h6>
          <ul>
            <li>Calories: Approximately 180</li>
            <li>Protein: 5g</li>
            <li>Carbohydrates: 15g</li>
            <li>Fat: 12g</li>
          </ul>
        `
      },
      6: {
        title: 'Cauliflower Fried Rice',
        img: 'assets/img/recipes/Cauliflower-Fried-Rice.png',
        desc: 'A low-carb twist on fried rice, loaded with veggies and scrambled egg.',
        instructions: `
          <h6>Ingredients:</h6>
          <ul>
            <li>1 head cauliflower, riced</li>
            <li>2 tbsp sesame oil</li>
            <li>1 small onion, diced</li>
            <li>1 cup carrots, diced</li>
            <li>1/2 cup frozen peas</li>
            <li>2 cloves garlic, minced</li>
            <li>2 eggs, beaten</li>
            <li>3 tbsp low-sodium soy sauce</li>
            <li>1/2 cup green onions, chopped</li>
            <li>Optional: sesame seeds, cilantro for garnish</li>
          </ul>
          <h6>Instructions:</h6>
          <ol>
            <li>Heat 1 tbsp oil; cook onion, carrots, and peas until tender (5 min).</li>
            <li>Add garlic; cook 1 min more.</li>
            <li>Push vegetables aside, add remaining oil, pour in eggs, scramble.</li>
            <li>Stir in cauliflower rice and soy sauce; cook 5–7 min until tender.</li>
            <li>Remove from heat; garnish with onions, sesame seeds, cilantro.</li>
          </ol>
        `,
        nutrition: `
          <h6>Nutritional Information (per serving):</h6>
          <ul>
            <li>Calories: Approximately 150</li>
            <li>Protein: 8g</li>
            <li>Carbohydrates: 15g</li>
            <li>Fat: 7g</li>
          </ul>
        `
      },
      7: {
        title: 'Lentil and Vegetable Stew',
        img: 'assets/img/recipes/Lentil-Vegetable-Stew.png',
        desc: 'Hearty stew of lentils and root veggies, simmered in savory broth.',
        instructions: `
          <h6>Ingredients:</h6>
          <ul>
            <li>1 cup dried lentils, rinsed</li>
            <li>2 tbsp olive oil</li>
            <li>1 onion, chopped</li>
            <li>2 carrots, diced</li>
            <li>2 celery stalks, diced</li>
            <li>3 garlic cloves, minced</li>
            <li>1 can (14.5 oz) diced tomatoes</li>
            <li>4 cups vegetable broth</li>
            <li>2 cups spinach, chopped</li>
            <li>1 tsp ground cumin</li>
            <li>1 tsp dried thyme</li>
            <li>Salt and pepper, to taste</li>
            <li>Fresh parsley for garnish</li>
          </ul>
          <h6>Instructions:</h6>
          <ol>
            <li>Heat oil in a pot; cook onion, carrots, celery 5 min until soft.</li>
            <li>Add garlic, cumin, thyme; cook 1 min until fragrant.</li>
            <li>Stir in lentils, tomatoes, broth; bring to boil, reduce heat, simmer 25–30 min.</li>
            <li>Add spinach; cook 2–3 min until wilted.</li>
            <li>Season with salt/pepper; serve garnished with parsley.</li>
          </ol>
        `,
        nutrition: `
          <h6>Nutritional Information (per serving):</h6>
          <ul>
            <li>Calories: Approximately 220</li>
            <li>Protein: 14g</li>
            <li>Carbohydrates: 35g</li>
            <li>Fat: 4g</li>
          </ul>
        `
      },
      8: {
        title: 'Zucchini Noodles with Pesto and Cherry Tomatoes',
        img: 'assets/img/recipes/Zucchini-Noodles-Pesto-Cherry-Tomatoes.png',
        desc: 'Light zucchini noodles tossed in basil pesto and fresh tomatoes.',
        instructions: `
          <h6>Ingredients:</h6>
          <ul>
            <li>4 zucchini, spiralized</li>
            <li>1 cup cherry tomatoes, halved</li>
            <li>1/2 cup basil pesto</li>
            <li>2 tbsp olive oil</li>
            <li>Salt and pepper, to taste</li>
            <li>Optional: grated Parmesan</li>
          </ul>
          <h6>Instructions:</h6>
          <ol>
            <li>Heat oil in a skillet; sauté zucchini noodles 2–3 min until just tender.</li>
            <li>Remove from heat; stir in tomatoes and pesto until coated.</li>
            <li>Season with salt/pepper; serve topped with Parmesan.</li>
          </ol>
        `,
        nutrition: `
          <h6>Nutritional Information (per serving):</h6>
          <ul>
            <li>Calories: Approximately 150</li>
            <li>Protein: 4g</li>
            <li>Carbohydrates: 10g</li>
            <li>Fat: 11g</li>
          </ul>
        `
      },
      9: {
        title: 'Roasted Butternut Squash and Kale Salad',
        img: 'assets/img/recipes/Roasted-Butternut-Squash-Kale-Salad.png',
        desc: 'Sweet roasted squash and tender kale tossed in balsamic honey dressing.',
        instructions: `
          <h6>Ingredients:</h6>
          <ul>
            <li>1 butternut squash, cubed</li>
            <li>1 bunch kale, chopped</li>
            <li>1/4 red onion, sliced</li>
            <li>1/2 cup goat cheese</li>
            <li>1/4 cup pumpkin seeds</li>
            <li>3 tbsp olive oil, divided</li>
            <li>2 tbsp balsamic vinegar</li>
            <li>1 tsp honey</li>
            <li>Salt and pepper, to taste</li>
          </ul>
          <h6>Instructions:</h6>
          <ol>
            <li>Preheat oven to 400°F. Toss squash with 1 tbsp oil, roast 25–30 min until tender.</li>
            <li>Massage kale with 1 tbsp oil to soften.</li>
            <li>Whisk remaining oil, vinegar, and honey for dressing.</li>
            <li>Combine kale, squash, onion, cheese, and seeds in a bowl.</li>
            <li>Drizzle dressing; toss to combine.</li>
            <li>Serve at room temperature or chilled.</li>
          </ol>
        `,
        nutrition: `
          <h6>Nutritional Information (per serving):</h6>
          <ul>
            <li>Calories: Approximately 200</li>
            <li>Protein: 6g</li>
            <li>Carbohydrates: 20g</li>
            <li>Fat: 12g</li>
          </ul>
        `
      }
    };
  
    // 2) On '+' click, inject recipe data into modal
    $('.single-cat .plus-btn').on('click', function() {
      const id = $(this).closest('.single-cat').data('recipe-id');
      const r = recipes[id];
      if (!r) return;
  
      $('#recipeModalLabel').text(r.title);
      $('#recipeModalImg').attr('src', r.img).attr('alt', r.title);
      $('#recipeModalDesc').text(r.desc);
      $('#recipeModalRecipe').html(r.instructions);
      $('#recipeModalNutrition').html(r.nutrition);
    });
  });
  
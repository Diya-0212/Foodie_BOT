
import streamlit as st
from model import RecipeModel

# Initialize the model
recipe_model = RecipeModel()

# Streamlit UI
st.title("Recipe Chatbot 🍽️")
st.write("Provide ingredients, and I'll suggest dishes and recipes!")

# Memory Display
if "history" not in st.session_state:
    st.session_state["history"] = []

# User Input: Ingredients
ingredients = st.text_input("Enter ingredients (comma-separated):", key="ingredients")

# Generate Dish Suggestions
if st.button("Get Dish Suggestions"):
    if ingredients:
        dishes = recipe_model.get_dishes(ingredients=ingredients)
        st.session_state["dishes"] = dishes
        st.session_state["history"].append({"User": ingredients, "Bot": dishes})
        st.write("### Dishes Categorized:")
        for category, items in dishes.items():
            st.write(f"**{category}**")
            for dish in items:
                st.write("- " + dish)
    else:
        st.write("Please provide ingredients.")

# Select a Dish to Get Recipe
if "dishes" in st.session_state:
    selected_dish = st.selectbox("Choose a dish to see its recipe:", options=[
        dish for category in st.session_state["dishes"].values() for dish in category
    ])
    if st.button("Get Recipe"):
        recipe = recipe_model.get_recipe(dish=selected_dish)
        st.session_state["history"].append({"User": f"Recipe for {selected_dish}", "Bot": recipe})
        st.write(f"### Recipe for {selected_dish}")
        st.write(recipe)

# Modify Recipe
if "history" in st.session_state:
    preference = st.text_input("Modify recipe (e.g., 'avoid oil', 'add garlic'):")
    if st.button("Update Recipe"):
        modified_recipe = recipe_model.modify_recipe(selected_dish, preference)
        st.session_state["history"].append({"User": preference, "Bot": modified_recipe})
        st.write("### Updated Recipe:")
        st.write(modified_recipe)

# Show Chat History
st.write("### Chat History:")
for chat in st.session_state["history"]:
    st.write(f"**User:** {chat['User']}")
    st.write(f"**Bot:** {chat['Bot']}")


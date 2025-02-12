from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import os
from dotenv import  load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

class RecipeModel:
    def __init__(self) -> None:
        # Initialize memory and LLM
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.llm = ChatGroq(
            temperature=0.8,
            model="llama-3.1-8b-instant",
            groq_api_key=os.getenv("GroqKeyD")
        )
        # Prompts
        self.ingredient_prompt = PromptTemplate(
            input_variables=["ingredients"],
            template="""
        You are a recipe expert. Suggest dishes based on these ingredients:
        {ingredients}

        Categorize them as:
        - Starters (4 items: 2 Indian, 2 International)
        - Main Course (4 items: 2 Indian, 2 International)
        - Desserts (4 items: 2 Indian, 2 International)
        Use this exact format:
    Starters:
    - Dish 1
    - Dish 2
    - Dish 3
    - Dish 4
    Main Course:
    - Dish 5
    - Dish 6
    - Dish 7
    - Dish 8
    Desserts:
    - Dish 9
    - Dish 10
    - Dish 11
    - Dish 12
        """
        )
        self.recipe_prompt = PromptTemplate(
            input_variables=["dish"],
            template="""
        You are a recipe expert. Provide a detailed recipe for the dish: {dish}.
        Include:
        - Ingredients required
        - Step-by-step instructions
        """
        )
        self.modify_prompt = PromptTemplate(
            input_variables=["dish", "preference"],
            template="""
        You are a recipe expert. Modify the recipe for the dish: {dish}.
        User preference: {preference}.
        Provide updated step-by-step instructions.
        """
        )

    def get_dishes(self, ingredients):
        chain = LLMChain(llm=self.llm, prompt=self.ingredient_prompt)
        response = chain.run(ingredients=ingredients)
        return self._parse_dishes(response)

    def get_recipe(self, dish):
        chain = LLMChain(llm=self.llm, prompt=self.recipe_prompt)
        return chain.run(dish=dish)

    def modify_recipe(self, dish, preference):
        chain = LLMChain(llm=self.llm, prompt=self.modify_prompt)
        return chain.run(dish=dish, preference=preference)

    def _parse_dishes(self, response):
        # Split the response into lines
        lines = response.split("\n")

        # Initialize a dictionary to hold categorized dishes
        categories = ["Starters", "Main Course", "Desserts"]
        dishes = {category: [] for category in categories}

        # Variable to keep track of the current category
        current_category = None

        for line in lines:
            line = line.strip()  # Remove leading/trailing spaces

            if not line:  # Skip empty lines
                continue

            # Check if the line matches a category
            if any(category in line for category in categories):
                current_category = next(
                    (category for category in categories if category in line), None
                )
            elif current_category:
                # Add dish to the current category
                dishes[current_category].append(line.strip("- ").strip())

        print("Parsed Dishes:", dishes)  # Debugging
        return dishes
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


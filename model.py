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


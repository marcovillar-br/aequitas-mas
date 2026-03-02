# -*- coding: utf-8 -*-
"""
A temporary diagnostic script to list available Google Generative AI models.

This script will connect to the Google AI API and print a list of all available
models that support the 'generateContent' method, which is used by the agents.
This helps in identifying the correct model name to use and avoids '404 Not Found'
errors.
"""
import google.generativeai as genai
import os

def list_available_models():
    """
    Connects to the Google AI API and lists models that support 'generateContent'.
    """
    try:
        # The API key is expected to be set as an environment variable
        # e.g., GOOGLE_API_KEY
        if not os.environ.get("GOOGLE_API_KEY"):
            print("ERROR: The GOOGLE_API_KEY environment variable is not set.")
            print("Please set the API key to run this script.")
            return

        print("Fetching available models from Google Generative AI...")
        print("-" * 50)

        model_count = 0
        for m in genai.list_models():
            # Check if the model supports the 'generateContent' method
            if 'generateContent' in m.supported_generation_methods:
                print(f"Model found: {m.name}")
                model_count += 1
        
        if model_count == 0:
            print("No models supporting 'generateContent' were found.")
        else:
            print("-" * 50)
            print(f"Found {model_count} suitable models.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print("Please ensure your API key is correct and has the necessary permissions.")

if __name__ == "__main__":
    list_available_models()

import json
import os
from openai import OpenAI

# Connect to local Ollama instance
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama', # required but ignored by Ollama
)

# You can change the model to whatever Llama 3 model you have pulled in Ollama
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.1")

def load_dataset(filepath="dataset.json"):
    with open(filepath, "r") as f:
        return json.load(f)

def generate_replies(dataset):
    # We will use the first two examples as few-shot prompts to ground the tone
    few_shot_examples = dataset[:2]
    test_examples = dataset[2:]
    
    system_prompt = (
        "You are a professional, empathetic, and helpful customer support agent. "
        "Your job is to draft replies to incoming customer emails. "
        "Do not invent new policies or false promises. Keep it concise but polite.\n\n"
        "Here are some examples of the tone and style we expect:\n"
    )
    
    for ex in few_shot_examples:
        system_prompt += f"\nIncoming Email: {ex['incoming_email']}\n"
        system_prompt += f"Response:\n{ex['reference_reply']}\n"
        system_prompt += "-" * 20 + "\n"
        
    print(f"Generating responses for {len(test_examples)} emails using {MODEL_NAME}...")
    
    generated_results = []
    
    for ex in test_examples:
        print(f"Processing Email ID {ex['id']} (Category: {ex['category']})...")
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Incoming Email:\n{ex['incoming_email']}\n\nPlease generate a response."}
                ],
                temperature=0.7,
            )
            
            generated_reply = response.choices[0].message.content.strip()
            
            result = {
                "id": ex["id"],
                "category": ex["category"],
                "incoming_email": ex["incoming_email"],
                "reference_reply": ex["reference_reply"],
                "generated_reply": generated_reply
            }
            generated_results.append(result)
            
        except Exception as e:
            print(f"Error generating response for ID {ex['id']}: {e}")
            
    with open("generated_responses.json", "w") as f:
        json.dump(generated_results, f, indent=4)
        
    print("Generation complete! Results saved to generated_responses.json")

if __name__ == "__main__":
    dataset = load_dataset()
    generate_replies(dataset)

import json
import os
from openai import OpenAI

# Connect to local Ollama instance
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama', # required but ignored by Ollama
)

MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.1")

def load_responses(filepath="generated_responses.json"):
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found. Run generate_response.py first.")
        return []
    with open(filepath, "r") as f:
        return json.load(f)

def evaluate_responses(responses):
    print(f"Evaluating {len(responses)} responses using {MODEL_NAME} as a judge...")
    
    evaluation_prompt = """
You are an expert customer support manager evaluating AI-generated replies.
You will be provided with:
1. The Incoming Email
2. The Generated Reply

Evaluate the Generated Reply on the following three criteria on a scale of 1 to 5:
- Relevance (1-5): Does the reply directly address the core issue/question of the incoming email?
- Tone (1-5): Is the reply professional, polite, and empathetic?
- Accuracy (1-5): Does the reply avoid hallucinations (making up policies, features, or links not provided)?

Respond ONLY with a valid JSON object matching this schema exactly:
{
    "relevance_score": int,
    "tone_score": int,
    "accuracy_score": int,
    "reasoning": "A short 1-2 sentence explanation for the scores."
}
"""

    evaluations = []
    
    for ex in responses:
        print(f"Evaluating Email ID {ex['id']}...")
        
        user_prompt = (
            f"Incoming Email: {ex['incoming_email']}\n"
            f"Generated Reply: {ex['generated_reply']}\n"
        )
        
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": evaluation_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            
            raw_eval = response.choices[0].message.content.strip()
            eval_dict = json.loads(raw_eval)
            
            # Combine original data with evaluation
            result = {
                **ex,
                "evaluation": eval_dict
            }
            evaluations.append(result)
            
        except Exception as e:
            print(f"Error evaluating ID {ex['id']}: {e}")
            
    # Calculate overall metrics
    if evaluations:
        avg_relevance = sum(e["evaluation"].get("relevance_score", 0) for e in evaluations) / len(evaluations)
        avg_tone = sum(e["evaluation"].get("tone_score", 0) for e in evaluations) / len(evaluations)
        avg_accuracy = sum(e["evaluation"].get("accuracy_score", 0) for e in evaluations) / len(evaluations)
        overall = (avg_relevance + avg_tone + avg_accuracy) / 3
        
        print("\n--- EVALUATION SUMMARY ---")
        print(f"Total Evaluated: {len(evaluations)}")
        print(f"Average Relevance: {avg_relevance:.2f} / 5.0")
        print(f"Average Tone:      {avg_tone:.2f} / 5.0")
        print(f"Average Accuracy:  {avg_accuracy:.2f} / 5.0")
        print(f"OVERALL SYSTEM SCORE: {overall:.2f} / 5.0")
        print("--------------------------\n")
        
    with open("evaluation_results.json", "w") as f:
        json.dump(evaluations, f, indent=4)
        
    print("Evaluation complete! Full results saved to evaluation_results.json")

if __name__ == "__main__":
    responses = load_responses()
    if responses:
        evaluate_responses(responses)

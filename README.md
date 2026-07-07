# AI Email Suggested-Response System

This repository contains an end-to-end AI system designed to suggest replies to customer support emails and automatically evaluate their accuracy.

## Architecture

The system consists of three main components:
1.  **Dataset Construction (`build_dataset.py`)**: Generates a high-quality synthetic dataset of customer support emails and reference replies.
2.  **Gen AI Response Generator (`generate_response.py`)**: Uses a generative AI model to read incoming emails and draft a reply based on few-shot examples from the dataset.
3.  **Accuracy / Evaluation System (`evaluate.py`)**: Uses an "LLM-as-a-judge" approach to rigorously grade the generated replies.

## Why "LLM-as-a-Judge"? (The Accuracy Metric)

When evaluating generative AI responses—especially in conversational contexts like email—traditional NLP metrics like BLEU or ROUGE fall short. An exact word-for-word match is far too strict; there are many valid ways to say "I'm sorry, here is your refund."

Instead, this system uses an **LLM-as-a-judge** to evaluate generated replies across three critical dimensions (each scored 1-5):
1.  **Relevance**: Does the reply address the core issue of the email?
2.  **Tone**: Is it professional, polite, and empathetic?
3.  **Accuracy**: Does it avoid hallucinations (e.g., promising a feature that doesn't exist, or linking to a fake URL)?

The evaluator outputs these scores along with a short natural language reasoning explaining *why* it gave those scores. Finally, the system aggregates these into an **Overall System Score**.

## Prerequisites

This system is designed to run entirely locally using **Ollama** and the `llama3.1` model (or similar), ensuring zero API costs and full data privacy.

1.  Install [Ollama](https://ollama.com/).
2.  Pull the Llama 3.1 model:
    ```bash
    ollama run llama3.1
    ```
    *(You can keep this running in a separate terminal or just ensure the Ollama service is active).*
3.  Ensure you have Python 3.8+ installed.

## Setup and Execution

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Generate the dataset**:
    ```bash
    python build_dataset.py
    ```
    *This creates `dataset.json` containing the sample emails.*

3.  **Generate AI replies**:
    ```bash
    python generate_response.py
    ```
    *This reads `dataset.json` and uses the first few examples to prompt Ollama to generate replies for the rest. It outputs `generated_responses.json`.*
    *(Note: You can change the model by setting `OLLAMA_MODEL` environment variable. Default is `llama3.1`).*

4.  **Evaluate accuracy**:
    ```bash
    python evaluate.py
    ```
    *This evaluates the generated replies using the LLM-as-a-judge rubrics and outputs a summary to the console, saving the detailed breakdown (with reasoning) to `evaluation_results.json`.*

## AI Tools Used
- The initial architecture and evaluation strategy (LLM-as-a-judge) were designed with the help of an AI assistant.
- Code structures and boilerplate were generated iteratively.

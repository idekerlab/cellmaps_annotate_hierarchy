import json
import openai
import os
import time 
import argparse
# openai.api_key = os.getenv("OPENAI_API_KEY")

def load_log(LOG_FILE):
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    else:
        return {"tokens_used": 0, "dollars_spent": 0.0, "time_taken_last_run": 0.0, "time_taken_total": 0.0}

def save_log(LOG_FILE,log_data):
    with open(LOG_FILE, "w") as f:
        json.dump(log_data, f, indent=4)

def estimate_cost(tokens, rate_per_token):
    return tokens * rate_per_token

def openai_chat(context, prompt, model,temperature, max_tokens, rate_per_token, LOG_FILE, DOLLAR_LIMIT):
    log_data = load_log(LOG_FILE)
    tokens_estimate = len(prompt) + max_tokens

    if estimate_cost(log_data["tokens_used"] + tokens_estimate, rate_per_token) > DOLLAR_LIMIT:
        print("The API call is estimated to exceed the dollar limit. Aborting.")
        return

    try:
        start_time = time.time()
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "system", "content": context},{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=temperature,
        )
        end_time = time.time() 

        # print(response)
        tokens_used = response["usage"]["total_tokens"]
        
        # Update and save the log
        log_data["tokens_used"] += tokens_used
        log_data["dollars_spent"] = estimate_cost(log_data["tokens_used"], rate_per_token)
        time_usage = end_time - start_time
        log_data["time_taken_last_run"] = time_usage
        log_data["time_taken_total"] += time_usage
        print(tokens_used)
        save_log(LOG_FILE,log_data)

        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# excute the script
if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--openai_api_key", type=str, required=True)
    argparser.add_argument("--context", type=str, default="I am a highly intelligent question answering bot. If you ask me a question that is rooted in truth, I will give you the answer. If you ask me a question that is nonsense, trickery, or has no clear answer, I will respond with \"Unknown\".")
    argparser.add_argument("--prompt",required=True, type=str, help="input prompt to chatgpt")
    argparser.add_argument("--model", type=str, default="gpt-3.5-turbo")
    argparser.add_argument("--temperature", type=float, default=0, help="temperature for chatgpt to control randomness, 0 means deterministic, 1 means random")
    argparser.add_argument("--max_tokens", type=int, default=500, help="max tokens for chatgpt response")
    argparser.add_argument("--rate_per_token", type=float, default=0.0005, help="rate per token to estimate cost")
    argparser.add_argument("--log_file", type=str, default="./log.json", help="PATH to the log file to save tokens used and dollars spent")
    argparser.add_argument("--dollor_limit", type=float, default=5.0, help="dollor limit to abort the chatgpt query")
    argparser.add_argument("--file_path", type=str, default="./response.txt", help="PATH to the file to save the response")
    
    args = argparser.parse_args()

    openai.api_key = args.openai_api_key

    context = args.context
    prompt = args.prompt
    model = args.model
    temperature = args.temperature
    max_tokens = args.max_tokens
    rate_per_token = args.rate_per_token
    file_path = args.file_path

    LOG_FILE = args.log_file
    DOLLAR_LIMIT = args.dollor_limit
    response_text = openai_chat(context, prompt, model,temperature, max_tokens, rate_per_token, LOG_FILE, DOLLAR_LIMIT)
    if response_text:
        with open(file_path, "w") as f:
            f.write(response_text)
        # print(response_text)

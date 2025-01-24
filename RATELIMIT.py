import time
import requests
import threading

def ping_discord():
    pas_b = 552590450171838466  # ID du canal
    url = f"https://discord.com/api/v10/channels/{pas_b}/messages"
    bot_token = "NzExNzU2MjQ5MzkzMjY2NzAx.GmFMZm.Iix3QbOdIdcPsVDgt_lxALK9qMRDYRO-mm4y1Y" 
    headers = {
        "User-Agent": "My Discord Bot (https://discord.com, v1.0)",
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json"
    }
    
    while True:
        try:
            # Utilisation de POST pour envoyer un message
            data = {
                "content": "Ping from my bot!"  # Contenu du message à envoyer
            }
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                print("Ping successful!")
            else:
                print(f"Ping failed with status code: {response.status_code}, message: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
        
        time.sleep(1)  # Délai raisonnable entre les requêtes

def start_threads(thread_count):
    threads = []
    for _ in range(thread_count):
        thread = threading.Thread(target=ping_discord)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    THREAD_COUNT = 5  # Nombre de threads souhaités (réduit pour éviter une surcharge)
    start_threads(THREAD_COUNT)

from mitmproxy import http
import logging
import time
import asyncio

# Paramètres de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class RateLimiter:
    def __init__(self, max_requests_per_second: int = 50):
        self.max_requests_per_second = max_requests_per_second
        self.current_requests = 0
        self.last_reset = time.time()



    def is_allowed(self):
        # Si on dépasse le nombre de requêtes autorisées par seconde
        if time.time() - self.last_reset >= 1:
            self.current_requests = 0
            self.last_reset = time.time()

        if self.current_requests < self.max_requests_per_second:
            self.current_requests += 1
            return True
        return False

rate_limiter = RateLimiter()

# Fonction pour intercepter et traiter les requêtes
def request(flow: http.HTTPFlow) -> None:
    if flow.request.pretty_url.startswith("https://discord.com/api/v10/"):
        if rate_limiter.is_allowed():
            logging.info(f"Requête autorisée: {flow.request.pretty_url}")
        else:
            logging.warning(f"Trop de requêtes. Mise en pause: {flow.request.pretty_url}")
            flow.response = http.Response.make(
                429,  # Code d'erreur HTTP 429 - Too Many Requests
                b"Rate limit exceeded. Try again later.",
                {"Content-Type": "text/plain"}
            )

# Lancer mitmproxy avec ce script
def start_proxy():
    logging.info("Lancement de mitmproxy avec un rate limiter...")
    from mitmproxy.tools.main import mitmdump
    mitmdump(["-s", "rate_limiter.py", "-p", "8082"])

if __name__ == "__main__":
    start_proxy()

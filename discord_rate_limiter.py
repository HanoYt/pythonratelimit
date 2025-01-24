import aiohttp
import asyncio
import logging
from datetime import datetime
from typing import Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DiscordBotManager:
    def __init__(self, max_requests_per_second: int = 5):
        self.bots: Dict[str, Dict] = {}
        self.request_queue = asyncio.Queue()
        self.global_rate_limit = max_requests_per_second
        self.current_requests = 0
        self.session = None
        self.tasks = []  # Stocke les tâches des workers

    async def initialize(self):
        self.session = aiohttp.ClientSession()
        # Démarrer les workers
        self.tasks.append(asyncio.create_task(self.process_queue()))
        self.tasks.append(asyncio.create_task(self.reset_counter()))

    async def shutdown(self):
        # Annuler toutes les tâches des workers
        for task in self.tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logging.info(f"Tâche {task.get_name()} arrêtée proprement.")
        # Fermer la session HTTP
        await self.session.close()
        logging.info("Session aiohttp fermée.")

    async def add_bot(self, bot_token: str, channel_id: str):
        self.bots[bot_token] = {
            'channel_id': channel_id,
            'last_request': datetime.now(),
            'requests_count': 0
        }

    async def process_queue(self):
        try:
            while True:
                request_data = await self.request_queue.get()
                if self.current_requests >= self.global_rate_limit:
                    logging.warning("Limite globale atteinte, attente d'une seconde.")
                    await asyncio.sleep(1)
                    self.current_requests = 0

                async with self.session.request(
                    method=request_data['method'],
                    url=request_data['url'],
                    headers=request_data['headers'],
                    data=request_data.get('data')
                ) as response:
                    self.current_requests += 1

                    if response.status == 429:  # Rate limit atteint
                        retry_after = int(response.headers.get('Retry-After', 1))
                        logging.warning(f"Rate limit atteint. Réessai après {retry_after} secondes.")
                        await asyncio.sleep(retry_after)
                        await self.request_queue.put(request_data)
                    else:
                        logging.info(f"Requête réussie pour le bot {request_data['bot_token'][:10]}")

                await asyncio.sleep(0.2)  # Ajout d'un délai fixe entre les requêtes
                self.request_queue.task_done()
        except asyncio.CancelledError:
            logging.info("process_queue annulée, arrêt en cours...")

    async def reset_counter(self):
        try:
            while True:
                await asyncio.sleep(1)
                self.current_requests = 0
        except asyncio.CancelledError:
            logging.info("reset_counter annulée, arrêt en cours...")

    async def make_request(self, bot_token: str, endpoint: str, method: str = 'GET', data: dict = None):
        if bot_token not in self.bots:
            raise ValueError("Bot non enregistré")

        bot_data = self.bots[bot_token]
        if bot_data['requests_count'] >= (self.global_rate_limit // len(self.bots)):
            logging.warning(f"Bot {bot_token[:10]} atteint sa limite individuelle. Attente d'une seconde.")
            await asyncio.sleep(1)
            return

        bot_data['requests_count'] += 1

        url = f"https://discord.com/api/v10/{endpoint}"
        headers = {
            "Authorization": f"Bot {bot_token}",
            "Content-Type": "application/json"
        }

        await self.request_queue.put({
            'method': method,
            'url': url,
            'headers': headers,
            'data': data,
            'bot_token': bot_token
        })

async def main():
    manager = DiscordBotManager(max_requests_per_second=5)  # Limite réduite pour les tests
    await manager.initialize()

    bots_config = [
        {"token": "bot1_token", "channel": "channel1_id"},
        {"token": "bot2_token", "channel": "channel2_id"}
    ]

    for bot in bots_config:
        await manager.add_bot(bot["token"], bot["channel"])

    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logging.info("Arrêt du gestionnaire...")
    finally:
        await manager.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Script interrompu par l'utilisateur.")

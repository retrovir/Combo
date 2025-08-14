import os
import asyncio
from telethon import events, TelegramClient, Button
from telethon.sessions import StringSession
from telethon.tl.types import PhotoStrippedSize
from telethon.errors.rpcerrorlist import SessionPasswordNeededError, MessageIdInvalidError

# ==============================================================================
# === CONFIGURATION: ADD YOUR ACCOUNTS HERE ===
# ==============================================================================
ACCOUNTS = [
    {
        'NAME': 'Account 1',
        'API_ID': 28589254,
        'API_HASH': '1aff8819e75343aefd318078d1dd60f3',
        'CHAT_ID': -4790971666,
        'SESSION_STRING': '1BVtsOLMBu7VOU-xwIqTxkQblWmreO2OM7eClFJoJ9eVOyXxiwC9OdQ7NOmyuL0hMqA_f4s_-7HGIRpPZPUvtogf0Sw-vXGPXOJTF0CiWuGbuB4sCtVeipT5x1KTd2q856EYxOWFXY0G3YdfYVGk0qSYO29yZl_wFmhf1w8xPKYwp05KLB_8rDxyP7QsBU6I3fJ5R9JFOJ-AJgzz37l5a5l13N63sha_jEjjMHwb_lX57_dRHSxpQM-pD3zWbAmS8Jn_WH_420Y2Br9DBoGXU5xxsPJeaiqBWha4ZXcry19k_BhGRz8GXGyWN-BOkLudm3og5c_zVDTIU4U7RXmPH-URzaalm3bA=',
        'MY_USER_ID': 5834025207
    },
    {
        'NAME': 'Account 2',
        'API_ID': 24433804,
        'API_HASH': 'e7f9cd7182550a68df68718efb4b2d12',
        'CHAT_ID': -1002100889006,
        'SESSION_STRING': '1BVtsOIIBuxEeBDtF9BhLtoZWbbrgpN6D1PTf4t_0Rj3r9sxqE3bvu8lEc64FMzPTC0xdTLV8zwXxAbS9ungt3nPNADJiiuWQbeU_YEtV0VkxspfeTlXqpigiNf-G8LZFl50mhiy1XvWL8PXSld6q1vLdn60C0up2aObfJQfTRD9qLpYlIvzpDpa2nlQUCnRLrh7BGvwn8pqZn_CE0r6g-ZVdQQBjFu_CcQGNDFqsK6Ig8Kch7J0u4ScLItiu3Vbsslinlq96NtjPzACNemopT34nOMHYgvl47ncSUSB153kL7pPVZNYDRFx0S7pnHD8vCI1zGLKSeZTCId9yiTZMcb0OVW1s_Ak=',
        'MY_USER_ID': 5568135871
    },
    {
        'NAME': 'Account 3',
        'API_ID': 29164136,
        'API_HASH': 'f5c25e88de83b6db6fd49e5a8e9eeb74',
        'CHAT_ID': -4754502578,
        'SESSION_STRING': '1BVtsOIYBu3OSacAnT0Qbe2GpXjqhmEd7GrLTtUssyGufTdYKEk4SaizGzk-X8IcdpzjThtFWfI0E_Mu1-iZZQewdYo0Ijg86OWjrtymrrD0k5kFRhiOUMPMmiLIsFSNsFaK1U9z3Zj7Qyvei_UyFiL9AYHhVnSKtHBbmQGTObADtmqPQmdGBWV4naIuTMbksmju6cp6diA2aXjl5WERSvGjN34t7oNpzKGdwfHwYQMK-k4CWQW18mCzZYRq4xugrLDC3Co5QDXI-R9P53LSiA6oUmutJ9ocr7Zy6wcJZgrE9V6D81i4TzfAnPIB4_BEvIy05kx4L7pzojEgBAntTVDpifzzgZKk=',
        'MY_USER_ID': 6967887832
    },
    {
        'NAME': 'Account 4',
        'API_ID': 25071651,
        'API_HASH': '22bf4f762648413ed8357fa90a0e9c69',
        'CHAT_ID': -1002496450450,
        'SESSION_STRING': '1BVtsOMABuxYJVv6kwacbwDt-YO4AEVTyqiQ-L_N06pRIyvQOfGn3uxfGhLDkagXwf1j2rTgls-nlzC0iDfyTFEV0U3OLF7LqqXG1sUzpQtXHvC6xCDL_Qt2YG8qSv8Jmw1CN2ij7cj9Ay1PwP5ldzGB48cIEUarUxFaI385iAtinEPlKgUE4AvIReah1Sx_X2HmskRH8iODcrpWBYeCELQZ-lfgSVVGBIpy2lKQg67tNYKdFs9nVAj0ZwhabmwRcjD2fTcTdrgHAz79CdvqEC6DiaAgXqj4jnInBGCItbAxQIvTk9L---JaKDOXYNkMKZzr0XiYUA9aq2wPedeRDjTWLQ4L5xAw=',
        'MY_USER_ID': 6909083639
    },
]

POKEBOT_ID = 572621020

# ==============================================================================
# === HELPER CLASSES ===
# ==============================================================================

class Counter:
    def __init__(self):
        self.count = 0
    def increment(self):
        self.count += 1
        return self.count

# ==============================================================================
# === MAIN PER-ACCOUNT BOT CLASS ===
# ==============================================================================

class PokebotMultiClient:
    def __init__(self, config):
        self.name = config['NAME']
        self.api_id = config['API_ID']
        self.api_hash = config['API_HASH']
        self.session_string = config['SESSION_STRING']
        self.chat_id = config['CHAT_ID']
        self.my_user_id = config['MY_USER_ID']
        self.client = TelegramClient(StringSession(self.session_string), self.api_id, self.api_hash)

        self.guesser_counter = Counter()
        self.is_guessing = False
        self.pause_flag = False

        self.active = False
        self.last_event_time = None
        self.last_hunt_time = 0

        self.in_battle = False
        self.in_hunt = False

        self.inactivity_task = None

        self.inactivity_timeout = 15
        self.guess_watchdog_task = None

        self._register_handlers()
        print(f"[{self.name}] Instance created for chat ID: {self.chat_id}")

    def _reset_event_timer(self):
        self.last_event_time = asyncio.get_event_loop().time()

    def _reset_guess_inactivity(self):
        if self.is_guessing and not self.pause_flag:
            self.last_activity = asyncio.get_event_loop().time()

    def _register_handlers(self):
        self.client.on(events.NewMessage(pattern=r"\.guess", outgoing=True))(self.start_guess)
        self.client.on(events.NewMessage(pattern=r"\.paus", outgoing=True))(self.pause_guess)
        self.client.on(events.NewMessage(pattern=r"\.bin", outgoing=True))(self.guesser_spam)
        self.client.on(events.NewMessage(from_users=POKEBOT_ID, pattern="Who's that pokemon?", chats=self.chat_id, incoming=True))(self.pokemon_guesser)
        self.client.on(events.NewMessage(from_users=POKEBOT_ID, pattern="The pokemon was ", chats=self.chat_id, incoming=True))(self.cache_updater)
        self.client.on(events.NewMessage(from_users=self.my_user_id, pattern='/kill'))(self.cmd_kill)
        self.client.on(events.NewMessage(from_users=self.my_user_id, pattern='/stop'))(self.cmd_stop)
        self.client.on(events.NewMessage(from_users=POKEBOT_ID))(self.poke_event)
        self.client.on(events.MessageEdited(from_users=POKEBOT_ID))(self.poke_event_edited)

    async def guess_inactivity_watchdog(self):
        while True:
            await asyncio.sleep(1)
            if self.is_guessing and not self.pause_flag and getattr(self, 'last_activity', None) is not None:
                now = asyncio.get_event_loop().time()
                if (now - self.last_activity) > self.inactivity_timeout:
                    print(f"[{self.name}] Inactivity detected (guesser), sending /guess...")
                    try:
                        await self.client.send_message(entity=self.chat_id, message='/guess')
                    except Exception as e:
                        print(f"[{self.name}] Failed to send /guess due to inactivity: {e}")
                    self._reset_guess_inactivity()

    async def auto_hunt_inactivity(self):
        while True:
            await asyncio.sleep(2)
            if not self.active:
                continue
            now = asyncio.get_event_loop().time()
            if not self.in_battle and not self.in_hunt and (now - self.last_hunt_time > 15):
                print(f"[{self.name}][AUTO-HUNT] No battle/hunt, sending /hunt.")
                await self.send_hunt()
            await asyncio.sleep(2)

    # === GUESSER HANDLERS ===

    async def start_guess(self, event):
        self._reset_guess_inactivity()
        self.is_guessing = True
        self.pause_flag = False
        await event.edit(f"✅ **[{self.name}] Guessing started.**")
        await self.client.send_message(entity=self.chat_id, message='/guess')

    async def pause_guess(self, event):
        self._reset_guess_inactivity()
        self.pause_flag = True
        await event.edit(f"⏸️ **[{self.name}] Guessing paused.**")

    async def guesser_spam(self, event):
        self._reset_guess_inactivity()
        if not self.is_guessing:
            return
        await self.client.send_message(entity=self.chat_id, message='/guess')
        while self.is_guessing:
            await asyncio.sleep(300)
            if self.pause_flag or not self.is_guessing:
                break
            await self.client.send_message(entity=self.chat_id, message='/guess')

    async def pokemon_guesser(self, event):
        self._reset_guess_inactivity()
        if not self.is_guessing or self.pause_flag:
            return
        for size in event.message.photo.sizes:
            if isinstance(size, PhotoStrippedSize):
                size_str = str(size)
                for file_name in os.listdir("cache/"):
                    if file_name.endswith(".txt"):
                        with open(os.path.join("cache", file_name), 'r') as f:
                            if f.read() == size_str:
                                count = self.guesser_counter.increment()
                                pokemon_name = file_name.split(".txt")[0]
                                print(f"[{self.name}] Match found! Guessing: {pokemon_name}. (Total for this account: {count})")
                                await self.client.send_message(self.chat_id, pokemon_name)
                                return
                with open(f"cache_{self.name}.tmp", 'w') as temp_cache_file:
                    temp_cache_file.write(size_str)
                print(f"[{self.name}] New Pokémon detected. Awaiting answer to learn...")
                break

    async def cache_updater(self, event):
        self._reset_guess_inactivity()
        if not self.is_guessing:
            return
        pokemon_name = event.message.text.split("The pokemon was ")[1].split(".")[0]
        temp_file_path = f"cache_{self.name}.tmp"
        if os.path.exists(temp_file_path):
            with open(temp_file_path, 'r') as temp_file:
                hash_content = temp_file.read()
            with open(os.path.join("cache", f"{pokemon_name}.txt"), 'w') as file:
                file.write(hash_content)
            os.remove(temp_file_path)
            print(f"[{self.name}] Learned and cached: {pokemon_name}")

        await asyncio.sleep(2)
        if self.is_guessing and not self.pause_flag:
            await self.client.send_message(self.chat_id, "/guess")

    # === AUTO-HUNT HANDLERS ===

    async def cmd_kill(self, event):
        self.active = True
        await event.reply("Auto-hunt started!")
        print(f"[{self.name}] Auto-hunt started!")
        self._reset_event_timer()
        if self.inactivity_task is None or self.inactivity_task.done():
            self.inactivity_task = asyncio.create_task(self.auto_hunt_inactivity())

    async def cmd_stop(self, event):
        self.active = False
        await event.reply("Auto-hunt stopped!")
        print(f"[{self.name}] Auto-hunt stopped!")

    async def send_hunt(self):
        now = asyncio.get_event_loop().time()
        await self.client.send_message(POKEBOT_ID, "/hunt")
        self.last_hunt_time = now
        self.last_event_time = now
        print(f"[{self.name}][HUNT] Sent /hunt command.")

    async def poke_event(self, event):
        text = event.raw_text

        if "shiny" in text.lower():
            await self.client.send_message(self.chat_id, f"✨ SHINY found! Check this message:\n{event.raw_text}")
            print(f"[{self.name}][SHINY] Shiny found! Alert sent, stopping auto-hunt.")
            self.active = False
            return

        if not self.active:
            return

        self._reset_event_timer()

        if "Current turn" in text:
            self.in_battle = True
            if event.buttons:
                print(f"[{self.name}] Battle turn detected: clicking button immediately.")
                try:
                    await event.click(1,1)
                except Exception as e:
                    print(f"[{self.name}] First click failed: {e}")
                await asyncio.sleep(3)
                try:
                    print(f"[{self.name}] Re-clicking battle button after 3s.")
                    await event.click(1,1)
                except Exception as e:
                    print(f"[{self.name}] Second click failed: {e}")
            return

        if any(end_phrase in text for end_phrase in ["fainted", "was caught", "ran away", "disappeared", "You won the battle", "You lost the battle", "fled"]):
            if self.in_battle:
                print(f"[{self.name}] Battle ended.")
            self.in_battle = False
            self.in_hunt = False

        if "appeared" in text and "wild" in text:
            self.in_hunt = True
        if any(end_phrase in text for end_phrase in ["was caught", "ran away", "disappeared", "fled"]):
            self.in_hunt = False

        if "appeared" in text:
            if event.buttons:
                await asyncio.sleep(1)
                print(f"[{self.name}] Clicked on Battle, Battle Begins")
                await event.click(0,0)

        if "Battle begins!" in text:
            if event.buttons:
                await asyncio.sleep(1)
                print(f"[{self.name}] Clicked on First Move")
                await event.click(1,1)
                await asyncio.sleep(1)
                print(f"[{self.name}] Clicked on First Move")
                await event.click(1,1)

        if "An expert trainer has challenged you to a battle." in text:
            if event.buttons:
                await asyncio.sleep(1)
                print(f"[{self.name}] Battle Begins Against Expert Trainer, Clicked On First Move")
                await event.click(1,0)
                await asyncio.sleep(1)
                print(f"[{self.name}] Battle Begins Against Expert Trainer, Clicked On First Move")
                await event.click(0,1)

        if "appeared" in text and event.buttons:
            await asyncio.sleep(0.5)
            print(f"[{self.name}] Clicked On Battle, Battle Begins")
            await event.click(text="Battle")

    async def poke_event_edited(self, event):
        if not self.active:
            return
        self._reset_event_timer()
        text = event.raw_text
        try:
            if "Current turn" in text:
                self.in_battle = True
                if event.buttons:
                    print(f"[{self.name}] [EDITED] Battle turn detected: clicking button immediately.")
                    try:
                        await event.click(1,1)
                    except Exception as e:
                        print(f"[{self.name}] [EDITED] First click failed: {e}")
                    await asyncio.sleep(3)
                    try:
                        print(f"[{self.name}] [EDITED] Re-clicking battle button after 3s.")
                        await event.click(1,1)
                    except Exception as e:
                        print(f"[{self.name}] [EDITED] Second click failed: {e}")
                return

            if any(end_phrase in text for end_phrase in ["fainted", "fled", "was caught", "ran away", "disappeared", "You won the battle", "You lost the battle"]):
                self.in_battle = False
                self.in_hunt = False
                await asyncio.sleep(1.2)
                print(f"[{self.name}] Battle/hunt ended, sending /hunt IMMEDIATELY.")
                await self.send_hunt()
        except (asyncio.TimeoutError, MessageIdInvalidError):
            pass

    # === RUNNER ===

    async def run(self):
        try:
            await self.client.start()
            print(f"✅ [{self.name}] Client started successfully!")
            print(f"   - Use '.guess' to start guessing and '.paus' to pause guessing for this account.")
            print(f"   - Use '/kill' to start auto-hunt and '/stop' to stop auto-hunt for this account.")
            os.makedirs("cache", exist_ok=True)
            if self.guess_watchdog_task is None or self.guess_watchdog_task.done():
                self.guess_watchdog_task = asyncio.create_task(self.guess_inactivity_watchdog())
            await self.client.run_until_disconnected()
        except Exception as e:
            print(f"❌ [{self.name}] An error occurred: {e}")
        finally:
            print(f"🛑 [{self.name}] Client has been disconnected.")

# ==============================================================================
# === MAIN EXECUTION ===
# ==============================================================================

async def main():
    print("--- Multi-Account Pokémon Guesser + Auto-hunt Initializing ---")
    os.makedirs("cache", exist_ok=True)
    tasks = []
    for config in ACCOUNTS:
        try:
            bot = PokebotMultiClient(config)
            tasks.append(bot.run())
        except Exception as e:
            print(f"⚠️  Skipping account {config.get('NAME', 'Unnamed')}: {e}")
    if not tasks:
        print("\nNo valid accounts were configured to run. Please check the `ACCOUNTS` list. Exiting.")
        return
    print(f"\n🚀 Starting {len(tasks)} bot(s) concurrently...")
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Shutting down all bots.")
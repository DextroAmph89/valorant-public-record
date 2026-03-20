import requests, time, os, base64, json, urllib3, re
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ANSI Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

CACHE_FILE = 'identity_cache.json'
MATCH_LOG = 'match_history.log'
MY_NAME = ""

# --- AGENT MAPPING DATA (Updated for 2025/2026) ---
AGENT_MAP = {
    "e370fa57-4757-3604-3648-499e1f642d3f": "Gekko",
    "dade69b4-4f5a-8528-247b-219e5a1facd6": "Fade",
    "5f8d3a7f-467b-97f3-062c-13acf203c006": "Breach",
    "cc8b64c8-4b25-4ff9-6e7f-37b4da43d235": "Deadlock",
    "b444168c-4e35-8076-db47-ef9bf368f384": "Tejo",
    "f94c3b30-42be-e959-889c-5aa313dba261": "Raze",
    "22697a3d-45bf-8dd7-4fec-84a9e28c69d7": "Chamber",
    "601dbbe7-43ce-be57-2a40-4abd24953621": "KAY/O",
    "6f2a04ca-43e0-be17-7f36-b3908627744d": "Skye",
    "117ed9e3-49f3-6512-3ccf-0cada7e3823b": "Cypher",
    "320b2a48-4d9b-a075-30f1-1f93a9b638fa": "Sova",
    "7c8a4701-4de6-9355-b254-e09bc2a34b72": "Miks",
    "1e58de9c-4950-5125-93e9-a0aee9f98746": "Killjoy",
    "95b78ed7-4637-86d9-7e41-71ba8c293152": "Harbor",
    "efba5359-4016-a1e5-7626-b1ae76895940": "Vyse",
    "707eab51-4836-f488-046a-cda6bf494859": "Viper",
    "eb93336a-449b-9c1b-0a54-a891f7921d69": "Phoenix",
    "92eeef5d-43b5-1d4a-8d03-b3927a09034b": "Veto",
    "41fb69c1-4189-7b37-f117-bcaf1e96f1bf": "Astra",
    "9f0d8ba9-4140-b941-57d3-a7ad57c6b417": "Brimstone",
    "0e38b510-41a8-5780-5e8f-568b2a4f2d6c": "Iso",
    "1dbf2edd-4729-0984-3115-daa5eed44993": "Clove",
    "bb2a4828-46eb-8cd1-e765-15848195d751": "Neon",
    "7f94d92c-4234-0a36-9646-3a87eb8b5c89": "Yoru",
    "df1cb487-4902-002e-5c17-d28e83e78588": "Waylay",
    "569fdd95-4d10-43ab-ca70-79becc718b46": "Sage",
    "a3bfb853-43b2-7238-a4f1-ad90e9e46bcc": "Reyna",
    "8e253930-4c05-31dd-1b6c-968525494517": "Omen",
    "add6443a-41bd-e414-f6ad-e58d267f4e95": "Jett"
}

# --- UPDATED MAP MAPPING DATA (With Internal Paths) ---
MAP_MAP = {
    # UUIDs
    "7eaecc1b-4337-bbf6-6ab9-04b8f06b3319": "Ascent",
    "b529448b-4d60-346e-e89e-00a4c527a405": "Fracture",
    "2fb9a4fd-47b8-4e7d-a969-74b4046ebd53": "Breeze",
    "224b0a95-48b9-f703-1bd8-67aca101a61f": "Abyss",
    "2fe4ed3a-450a-948b-6d6b-e89a78e680a9": "Lotus",
    "92584fbe-486a-b1b2-9faa-39b0f486b498": "Sunset",
    "fd267378-4d1d-484f-ff52-77821ed10dc2": "Pearl",
    "e2ad5c54-4114-a870-9641-8ea21279579a": "Icebox",
    "1c18ab1f-420d-0d8b-71d0-77ad3c439115": "Corrode",
    "2bee0dc9-4ffe-519b-1cbd-7fbe763a6047": "Haven",

    # Internal Engine Paths
    "/Game/Maps/Ascent/Ascent": "Ascent",
    "/Game/Maps/Bonsai/Bonsai": "Split",
    "/Game/Maps/Canyon/Canyon": "Fracture",
    "/Game/Maps/Duality/Duality": "Bind",
    "/Game/Maps/Foxtrot/Foxtrot": "Breeze",
    "/Game/Maps/Infinity/Infinity": "Abyss",
    "/Game/Maps/Jam/Jam": "Lotus",
    "/Game/Maps/Juliett/Juliett": "Sunset",
    "/Game/Maps/Pitt/Pitt": "Pearl",
    "/Game/Maps/Port/Port": "Icebox",
    "/Game/Maps/Rook/Rook": "Corrode",
    "/Game/Maps/Triad/Triad": "Haven"
}

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def log_reveal(player_obj):
    """Writes a single entry to the log. Only called once per player on init."""
    if MY_NAME.lower() in player_obj.full_name.lower():
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "REVEALED" if "Hidden" not in player_obj.full_name else "INCOGNITO"
    tracker_name = player_obj.full_name.replace("#", "%23")
    tracker_url = f"https://tracker.gg/valorant/profile/riot/{tracker_name}/overview"

    print(f"[{timestamp}] {status} | Map: {player_obj.map_name} | Agent: {player_obj.agent} | User: {player_obj.full_name}")
    print(f"Tracker: {GREEN}{tracker_url}{RESET}\n")

    log_entry = (
        f"[{timestamp}] {status} | MatchID: {player_obj.match_id} | Map: {player_obj.map_name} | "
        f"Agent: {player_obj.agent} | Side: {player_obj.team} | "
        f"User: {player_obj.full_name} | PUUID: {player_obj.puuid} | Tracker: {tracker_url}\n"
    )
    with open(MATCH_LOG, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def save_to_cache(player_obj):
    """Called once on Player init. Caches real names and writes the initial log entry."""
    if MY_NAME.lower() in player_obj.full_name.lower():
        return
    if "Hidden_Player" not in player_obj.full_name and "???" not in player_obj.full_name:
        cache = load_cache()
        if player_obj.puuid not in cache:
            cache[player_obj.puuid] = player_obj.full_name
            with open(CACHE_FILE, 'w') as f:
                json.dump(cache, f, indent=4)
    log_reveal(player_obj)

class Player:
    def __init__(self, client, puuid, agentID, incognito, team, match_id, mapID):
        self.client = client
        self.puuid = puuid
        self.match_id = match_id
        self.incognito = incognito
        self.group_num = None

        self.agent = AGENT_MAP.get(agentID, f"Unknown ({agentID})")
        self.map_name = MAP_MAP.get(mapID, f"Unknown Map ({mapID})")

        self.team = "Defending" if team == "Blue" else "Attacking"

        # Fetch match history for party detection BEFORE setting name
        self.history = self.fetch_history()

        # Try live API first, then fall back to cache
        self.full_name = self.set_name(puuid)

        # Parse name/tag and build Twitch candidate list
        if "#" in self.full_name:
            name_part, tag_part = self.full_name.split("#", 1)
        else:
            name_part, tag_part = self.full_name, ""
        self.name = self.filter_name(name_part)
        self.tag  = tag_part
        self.possibleNames = self.find_possible_names()

        save_to_cache(self)

    def fetch_history(self):
        """Fetches recent match IDs for this player to enable party detection."""
        try:
            data = self.client.fetch(
                f"/match-history/v1/history/{self.puuid}?startIndex=0&endIndex=10",
                endpoint_type="pd"
            )
            return [m['MatchID'] for m in data.get('History', [])]
        except:
            return []

    def filter_name(self, name):
        """Strip common streamer prefixes so Twitch lookup has a better hit rate."""
        name = name.lower()
        for prefix in ("twitch", "ttv"):
            name = name.replace(prefix, "")
        return name.strip()

    def find_possible_names(self):
        """Build a set of Twitch username candidates from name only — no tag included."""
        if "Hidden_Player" in self.full_name or not self.name:
            return []
        name_u = self.name.replace(" ", "_")
        name_n = self.name.replace(" ", "")
        return list(set(filter(None, [
            name_n,
            name_u,
            f"ttv_{name_n}",
            f"{name_n}_ttv",
            f"ttv_{name_u}",
            f"{name_u}_ttv",
        ])))

    def is_live(self, delay=1.0):
        """Check Twitch for a live broadcast. Returns the channel name or False."""
        if "Hidden_Player" in self.full_name or not self.possibleNames:
            return False
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36"}
        for name in self.possibleNames:
            if not name or len(name) < 3:
                continue
            time.sleep(delay)
            try:
                r = requests.get(f"https://www.twitch.tv/{name}", headers=headers, timeout=4)
                if r.status_code == 200 and "isLiveBroadcast" in r.text:
                    return name
            except:
                continue
        return False

    def _cache_and_return(self, puuid, name, tag, layer):
        """Helper: writes resolved name to cache and returns formatted string."""
        full_name = f"{name}#{tag}"
        cache = load_cache()
        cache[puuid] = full_name
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=4)
        print(f"{GREEN}[{layer}] Resolved: {full_name}{RESET}")
        return full_name

    def _get_local_client(self):
        """Reads the Riot lockfile and returns (local_url, headers) or (None, None)."""
        lockfile_path = os.path.join(
            os.getenv("LOCALAPPDATA", ""),
            r"Riot Games\Riot Client\Config\lockfile"
        )
        if not os.path.exists(lockfile_path):
            return None, None
        try:
            with open(lockfile_path, "r") as f:
                data = f.read().split(":")
            port, password = data[2], data[3]
            auth = base64.b64encode(f"riot:{password}".encode()).decode()
            headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
            return f"https://127.0.0.1:{port}", headers
        except:
            return None, None

    def set_name(self, puuid):
        # 0. Cache first 
        cache = load_cache()
        if puuid in cache:
            return cache[puuid]

        local_url, local_headers = self._get_local_client()

        # Run all layers up to 3 attempts, giving Riot Client time to populate streams
        for attempt in range(3):
            try:
                if local_url and local_headers:
                    # LAYER 1: RMS message stream
                    try:
                        r = requests.get(f"{local_url}/riot-messaging-service/v1/messages",
                                         headers=local_headers, verify=False, timeout=1)
                        if r.status_code == 200:
                            raw = r.text
                            nm = re.search(rf'"{puuid}".*?"game_name"\s*:\s*"([^"]+)"', raw, re.IGNORECASE)
                            if nm and "Hidden" not in nm.group(1):
                                tm = re.search(rf'"{puuid}".*?"tag_line"\s*:\s*"([^"]+)"', raw, re.IGNORECASE)
                                tag = tm.group(1) if tm else "???"
                                return self._cache_and_return(puuid, nm.group(1), tag, "L1_RMS")
                    except: pass

                    # LAYER 2: Player alias endpoint
                    try:
                        r = requests.get(f"{local_url}/player-alias/v1/aliases",
                                         headers=local_headers, verify=False, timeout=1)
                        if r.status_code == 200:
                            for a in r.json():
                                if a.get("puuid") == puuid and a.get("game_name") and "Hidden" not in a.get("game_name", ""):
                                    return self._cache_and_return(puuid, a["game_name"], a.get("tag_line", "???"), "L2_ALIAS")
                    except: pass

                    # LAYER 3: Chat participants
                    try:
                        r = requests.get(f"{local_url}/chat/v5/participants",
                                         headers=local_headers, verify=False, timeout=1)
                        if r.status_code == 200:
                            for p in r.json().get("participants", []):
                                if p.get("puuid") == puuid and p.get("game_name") and "Hidden" not in p.get("game_name", ""):
                                    return self._cache_and_return(puuid, p["game_name"], p.get("tag_line", "???"), "L3_CHAT")
                    except: pass

                    # LAYER 4: Presence stream + private blob decode
                    try:
                        r = requests.get(f"{local_url}/chat/v4/presences",
                                         headers=local_headers, verify=False, timeout=1)
                        if r.status_code == 200:
                            for p in r.json().get("presences", []):
                                if p.get("puuid") == puuid:
                                    if p.get("game_name") and "Hidden" not in p.get("game_name", ""):
                                        return self._cache_and_return(puuid, p["game_name"], p.get("game_tag", "???"), "L4_PRESENCE")
                                    if p.get("private"):
                                        try:
                                            blob = json.loads(base64.b64decode(p["private"]).decode())
                                            if blob.get("game_name") and "Hidden" not in blob.get("game_name", ""):
                                                return self._cache_and_return(puuid, blob["game_name"], blob.get("game_tag", "???"), "L4_BLOB")
                                        except: pass
                    except: pass

                # LAYER 5: PD name service
                try:
                    pd_res = self.client.put(endpoint="/name-service/v2/players", endpoint_type="pd", json_data=[puuid])
                    if pd_res and len(pd_res) > 0:
                        name = pd_res[0].get("GameName")
                        tag  = pd_res[0].get("TagLine")
                        if name and tag and "Hidden" not in name:
                            return self._cache_and_return(puuid, name, tag, "L5_PD")
                        else:
                            print(f"{YELLOW}[L5_PD] Name hidden server-side for {puuid[:8]}...{RESET}")
                except Exception as e:
                    print(f"{YELLOW}[L5_PD ERROR] {e}{RESET}")

            except: pass

            if attempt < 2:
                time.sleep(1.5)

        return "Hidden_Player#???"

def update_log_with_real_names(match_id, player_map):
    """Rewrites INCOGNITO log lines by matching on PUUID so each player gets their own real name."""
    if not os.path.exists(MATCH_LOG):
        return
    with open(MATCH_LOG, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    updated = False
    new_lines = []
    for line in lines:
        if match_id in line and "Hidden_Player" in line:
            # Match by PUUID field so we never stamp the wrong name
            for puuid, real_name in player_map.items():
                if f"PUUID: {puuid}" in line:
                    line = line.replace("Hidden_Player#???", real_name)
                    line = line.replace("INCOGNITO", "REVEALED (POST-MATCH)")
                    updated = True
                    break
        new_lines.append(line)
    if updated:
        with open(MATCH_LOG, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"{GREEN}[OK] Log updated with real names for Match: {match_id}{RESET}")

def resolve_post_match(client, match_id):
    print(f"{YELLOW}Match ended. Fetching final names...{RESET}")
    time.sleep(15)
    try:
        endpoint = f"/match-details/v1/matches/{match_id}"
        data = client.fetch(endpoint, endpoint_type="pd")
        player_map = {
            p['subject']: f"{p['gameName']}#{p['tagLine']}"
            for p in data.get('players', [])
            if "Hidden" not in p.get('gameName', '')
        }
        update_log_with_real_names(match_id, player_map)
    except Exception as e:
        print(f"Post-match resolution failed: {e}")

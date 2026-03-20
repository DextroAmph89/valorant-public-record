import json, time, os
from valclient.client import Client
from player import Player
from game import Game

from colorama import init
init(autoreset=True, convert=True)
# -----------------------------------------

running = True
seenMatches = []

print('Valorant Identity Scanner - High-Speed Mode')

# Load settings for region and interval
try:
    with open('settings.json', 'r') as f:
        data = json.load(f)
        region = data.get('region', 'na')
        stateInterval = data.get('stateInterval', 3)
except FileNotFoundError:
    print("settings.json not found, using defaults (NA, 3s)")
    region = 'na'
    stateInterval = 3

client = Client(region=region)
client.activate()

print(f"Waiting for a match to begin (Scanning every {stateInterval}s)...")

while running:
    time.sleep(stateInterval)
    matchID = None
    is_core = False

    # 1. Look for match (Pregame or Core-Game)
    try:
        pre_data = client.pregame_fetch_player()
        if pre_data and 'MatchID' in pre_data:
            matchID = pre_data['MatchID']
            is_core = False
    except:
        try:
            core_data = client.coregame_fetch_player()
            if core_data and 'MatchID' in core_data:
                matchID = core_data['MatchID']
                is_core = True
        except:
            pass

    # 2. Process detected match
    if matchID and matchID not in seenMatches:
        try:
            print('\n' + '='*55)
            print(f"MATCH DETECTED!")

            # Fetch match info based on current state
            matchInfo = client.coregame_fetch_match(matchID) if is_core else client.pregame_fetch_match(matchID)

            # Extract Map ID/Path for player initialization
            mapID = matchInfo.get('MapID') or matchInfo.get('mapId')

            # Fallback for 'Players' vs 'players' key mismatch across different API endpoints
            players_raw = matchInfo.get('Players') or matchInfo.get('players')

            if not players_raw:
                print("Match data found, but player list is currently empty. Retrying...")
                continue

            seenMatches.append(matchID)
            localPlayer = None
            players = []

            for player in players_raw:
                try:
                    p_obj = Player(
                        client=client,
                        puuid=player['Subject'].lower(),
                        agentID=player.get('CharacterID', '').lower(),
                        incognito=player.get('PlayerIdentity', {}).get('Incognito', False),
                        team=player.get('TeamID', 'Unknown'),
                        match_id=matchID,
                        mapID=mapID
                    )

                    time.sleep(0.1)  # Prevent rate limiting

                    if client.puuid == player['Subject']:
                        localPlayer = p_obj
                    else:
                        players.append(p_obj)
                except Exception as p_err:
                    print(f"Skipping a player due to data error: {p_err}")

            # Initialize Game logic
            currentGame = Game(
                party=client.fetch_party(),
                matchID=matchID,
                players=players,
                localPlayer=localPlayer
            )

            print("--- Resolving Identities ---")
            currentGame.find_hidden_names(players)

            print('='*55 + '\n')

            # 3. Post-Scan Interaction Logic
            while True:
                print("\nOptions: ENTER = re-scan | twitch = check for live streamers | done = end match")
                choice = input("> ").strip().lower()

                if choice == 'done':
                    print("\nInitiating final post-match unmasking...")
                    currentGame.post_match_reveal(client)
                    break

                elif choice == 'twitch':
                    RED    = '\033[91m'
                    GREEN  = '\033[92m'
                    CYAN   = '\033[96m'
                    YELLOW = '\033[93m'
                    RESET  = '\033[0m'
                    BOLD   = '\033[1m'
                    print(f"\n{CYAN}[TWITCH] Scanning {len(players)} players for live streams...{RESET}\n")
                    found_any = False
                    for p in players:
                        if "Hidden_Player" in p.full_name:
                            continue
                        live_channel = p.is_live(delay=twitchDelay)
                        if live_channel:
                            print(f"{GREEN}{BOLD}[LIVE]{RESET} {p.full_name} | Agent: {p.agent} | https://twitch.tv/{live_channel}")
                            found_any = True
                        else:
                            print(f"{YELLOW}[OFFLINE]{RESET} {p.full_name} | Agent: {p.agent}")
                    if not found_any:
                        print(f"\n{YELLOW}[TWITCH] No live streamers found in this lobby.{RESET}")

                else:
                    print("\n--- Re-scanning Identities ---")
                    # Re-run full identity resolution so live API hits and cache updates apply
                    for p in players:
                        p.full_name = p.set_name(p.puuid)
                        if "#" in p.full_name:
                            name_part, tag_part = p.full_name.split("#", 1)
                        else:
                            name_part, tag_part = p.full_name, ""
                        p.name = p.filter_name(name_part)
                        p.tag  = tag_part
                        p.possibleNames = p.find_possible_names()
                    currentGame.find_hidden_names(players)

            print("\nWaiting for next match...")

        except Exception as e:
            print(f"Error processing match: {e}")
            if 'matchInfo' in locals():
                print(f"Available Data Keys: {list(matchInfo.keys())}")

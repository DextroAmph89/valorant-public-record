import time
import os
import json
from player import save_to_cache, load_cache, update_log_with_real_names

# ANSI Colors
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
CYAN = '\033[96m'
YELLOW = "\033[93m"
RESET = '\033[0m'

CACHE_FILE = 'identity_cache.json'

class Game:
    def __init__(self, party, matchID, players, localPlayer):
        self.matchID = matchID
        self.players = players
        self.localPlayer = localPlayer

        # Link players by match history IDs to find "Traveling Shadows"
        self.identify_parties(self.players)

        self.teamPlayers = self.find_team_players(self.localPlayer, self.players)
        self.partyPlayers = self.find_party_members(party)

    def identify_parties(self, players):
        """Identifies groups by comparing shared match history IDs."""
        group_counter = 1
        for i, p1 in enumerate(players):
            if getattr(p1, 'group_num', None) is not None:
                continue
            for j, p2 in enumerate(players):
                if i == j:
                    continue

                history1 = getattr(p1, 'history', [])
                history2 = getattr(p2, 'history', [])
                common = set(history1) & set(history2)

                if len(common) >= 2:
                    if getattr(p1, 'group_num', None) is None:
                        p1.group_num = group_counter
                    p2.group_num = group_counter

            if getattr(p1, 'group_num', None) is not None:
                group_counter += 1

    def find_hidden_names(self, players):
        print(f"{'='*20} IDENTITY RESOLUTION {'='*19}")

        # Load the cache to cross-reference PUUIDs from previous sessions
        cache = load_cache()

        for player in players:
            # 1. Check if we have this specific PUUID in our database
            is_known = player.puuid in cache

            # 2. Check current visibility status
            is_incognito = getattr(player, 'incognito', False)
            is_hidden = "Hidden_Player" in player.full_name

            display_name = player.full_name
            display_agent = player.agent
            status_text = f"{RED}[HIDDEN]{RESET}" if is_incognito else f"{RESET}[PUBLIC]{RESET}"

            # 3. Create the "Future Match" detection tag
            encounter_tag = f"{CYAN}[KNOWN]{RESET} " if is_known else "        "

            group_id = getattr(player, 'group_num', None)
            party_tag = f"{BLUE}[Party {group_id}]{RESET}" if group_id else "         "

            # 4. Logic for unmasking 'Hidden' players using the cache
            if is_hidden and is_known:
                real_name = cache[player.puuid]
                display_name = f"{CYAN}{real_name} (Shadow Detected){RESET}"
                status_text = f"{CYAN}[RE-HIT]{RESET}"
            elif not is_hidden and is_incognito:
                # Incognito but name was resolved via live API
                display_name = f"{GREEN}{display_name}{RESET}"
                display_agent = f"{GREEN}{display_agent}{RESET}"
                status_text = f"{GREEN}[REVEALED]{RESET}"
            elif is_hidden:
                display_name = f"{RED}{display_name}{RESET}"
                display_agent = f"{RED}{display_agent}{RESET}"

            print(f"{status_text} {encounter_tag}{party_tag} {display_name} | Agent: {display_agent} | Team: {player.team}")

        print(f"{'='*55}")

    def post_match_reveal(self, client):
        """Pulls the final scoreboard to unmask players for future encounters."""
        print(f"\n{YELLOW}[SYSTEM] Match ended. Parsing final scoreboard...{RESET}")
        try:
            # Single consistent fetch - no wrapper fallback needed
            match_details = client.fetch(
                f"/match-details/v1/matches/{self.matchID}",
                endpoint_type="pd"
            )

            if not match_details or 'players' not in match_details:
                print(f"{RED}[!] Could not retrieve post-game match details.{RESET}")
                return

            reveals = 0
            cache = load_cache()

            for p_data in match_details.get('players', []):
                puuid = p_data.get('subject', '').lower()
                name = p_data.get('gameName')
                tag = p_data.get('tagLine')

                if name and tag and "Hidden" not in name:
                    full_name = f"{name}#{tag}"
                    if puuid and puuid not in cache:
                        cache[puuid] = full_name
                        reveals += 1

            if reveals > 0:
                with open(CACHE_FILE, 'w') as f:
                    json.dump(cache, f, indent=4)
                print(f"{GREEN}[SUCCESS] Added {reveals} new identities to the database.{RESET}")
                # Build a name map and rewrite INCOGNITO entries in the log
                player_map = {}
                for p_data in match_details.get('players', []):
                    puuid = p_data.get('subject', '').lower()
                    name = p_data.get('gameName')
                    tag = p_data.get('tagLine')
                    if puuid and name and tag and "Hidden" not in name:
                        player_map[puuid] = f"{name}#{tag}"
                update_log_with_real_names(self.matchID, player_map)
            else:
                print(f"{YELLOW}[IDLE] No new unmasked players found.{RESET}")

        except Exception as e:
            print(f"{RED}[ERROR] Post-match reveal failed: {e}{RESET}")

    def find_team_players(self, localPlayer, players):
        team_players = []
        if not localPlayer:
            return []
        for player in players:
            if player.team == localPlayer.team:
                team_players.append(player)
        return team_players

    def find_party_members(self, party):
        members = []
        if party and 'Members' in party:
            for member in party['Members']:
                members.append(member['Subject'].lower())
        return members

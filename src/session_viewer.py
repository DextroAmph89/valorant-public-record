import os
from datetime import datetime

MATCH_LOG = 'match_history.log'

# ANSI Colors
RED     = '\033[91m'
GREEN   = '\033[92m'
YELLOW  = '\033[93m'
BLUE    = '\033[94m'
CYAN    = '\033[96m'
WHITE   = '\033[97m'
DIM     = '\033[2m'
RESET   = '\033[0m'
BOLD    = '\033[1m'
ORANGE  = '\033[38;5;208m'

def color_status(status):
    status = status.strip()
    if status == "REVEALED":
        return f"{GREEN}{BOLD}{status:<22}{RESET}"
    elif status == "INCOGNITO":
        return f"{RED}{BOLD}{status:<22}{RESET}"
    elif "POST-MATCH" in status:
        return f"{CYAN}{BOLD}{status:<22}{RESET}"
    return f"{WHITE}{status:<22}{RESET}"

def view_current_session():
    os.system('cls')

    # Enable ANSI colors in Windows cmd
    os.system('color')

    if not os.path.exists(MATCH_LOG):
        print(f"{RED}[-] No match_history.log found. Start the scanner first!{RESET}")
        return

    today = datetime.now().strftime("%Y-%m-%d")

    print(f"{CYAN}{'='*90}{RESET}")
    print(f"{BOLD}{CYAN}  VALORANT IDENTITY LOG  {RESET}{DIM}SESSION: {today}{RESET}")
    print(f"{CYAN}{'='*90}{RESET}")
    print(f"{DIM}  {'TIMESTAMP':<20} {'STATUS':<22} {'AGENT':<12} {'SIDE':<12} PLAYER{RESET}")
    print(f"{DIM}{'-'*90}{RESET}")

    found_any = False
    match_groups = {}  # group lines by MatchID for cleaner display

    with open(MATCH_LOG, 'r', encoding='utf-8') as f:
        for line in f:
            if today not in line:
                continue

            # Parse the pipe-separated log format
            # Format: [timestamp] STATUS | MatchID: X | Map: X | Agent: X | Side: X | User: X | Tracker: X
            try:
                parts = [p.strip() for p in line.split('|')]

                # parts[0] = "[timestamp] STATUS"
                header = parts[0]
                timestamp = header[1:20]
                status = header[22:].strip()

                match_id  = parts[1].replace('MatchID:', '').strip() if len(parts) > 1 else '?'
                map_name  = parts[2].replace('Map:', '').strip()     if len(parts) > 2 else '?'
                agent     = parts[3].replace('Agent:', '').strip()   if len(parts) > 3 else '?'
                side      = parts[4].replace('Side:', '').strip()    if len(parts) > 4 else '?'
                user      = parts[5].replace('User:', '').strip()    if len(parts) > 5 else '?'
                # parts[6] = PUUID (internal only, skip for display)
                # parts[7] = Tracker URL

                side_color = BLUE if side == "Defending" else ORANGE

                if match_id not in match_groups:
                    match_groups[match_id] = {'map': map_name, 'players': []}

                match_groups[match_id]['players'].append(
                    (timestamp, status, agent, side, side_color, user)
                )
                found_any = True
            except:
                continue

    if not found_any:
        print(f"\n{YELLOW}  No players logged for {today} yet.{RESET}\n")
    else:
        for match_id, data in match_groups.items():
            print(f"\n{BOLD}{WHITE}  MAP: {data['map']}{RESET}  {DIM}({match_id[:8]}...){RESET}")
            print(f"{DIM}  {'-'*86}{RESET}")
            for (timestamp, status, agent, side, side_color, user) in data['players']:
                status_str = color_status(status)
                agent_str  = f"{WHITE}{agent:<12}{RESET}"
                side_str   = f"{side_color}{side:<12}{RESET}"
                user_str   = f"{GREEN}{user}{RESET}" if "Hidden" not in user else f"{RED}{user}{RESET}"
                print(f"  {DIM}{timestamp}{RESET}  {status_str} {agent_str} {side_str} {user_str}")
            print()

    print(f"{CYAN}{'='*90}{RESET}")

if __name__ == "__main__":
    view_current_session()
    print(f"\n{DIM}[PROMPT] Press ENTER to exit.{RESET}")
    input()

import os
import sys
import time
import google.generativeai as gen_ai


api_key_google = "AIzaSyDyD0yz2eNy9-7w6G-sGCcxXEv7IRDMGpc"


class Colors:
    
    RESET = '\033[0m'
    BOLD = '\033[1m'
    HEADER = '\033[95m'
    LOCATION = '\033[94m'
    NPC = '\033[92m'
    DIALOGUE = '\033[93m'
    ACTION = '\033[96m'
    ERROR = '\033[91m'


try:
    gen_ai.configure(api_key=api_key_google)
    model = gen_ai.GenerativeModel("gemini-1.5-flash")
    print(
        f"{Colors.ACTION}[Gemini API key found. Dynamic dialogue enabled.]{Colors.RESET}")


except TypeError:
    model = None
    print(
        f"{Colors.ERROR}[Gemini API key not found. Dynamic dialogue disabled.]{Colors.RESET}")


gemini_characters = {
    "franky": "You are Franky, a loud, eccentric cyborg shipwright. You often shout 'SUPER!' and talk about things being 'cola-powered'.",
    "shakky": "You are Shakky, a calm, observant, and slightly mysterious bartender. You are knowledgeable about the world's events.",
    "rayleigh": "You are Silvers Rayleigh, a legendary, retired pirate. You are calm, wise, and powerful, often speaking with a relaxed and knowing tone.",
    "bounty hunter": "You are a grizzled, cynical bounty hunter. You are terse, suspicious, and only interested in money or valuable information.",
    "duval": "You are Duval, the leader of the Rosy Life Riders. You are extremely vain, proud, and dramatic, obsessed with your own 'handsome' face. You speak with a flourish and often refer to your own beauty.",
    "camie": "You are Camie, a sweet, naive, and bubbly kissing gourami mermaid. You are incredibly kind-hearted, easily amazed by new things, and speak with great politeness and enthusiasm.",
    "pappag": "You are Pappag, a talking starfish and a famous fashion designer. You are Camie's mentor and act like her worried guardian, often panicking and overthinking situations while trying to keep her out of trouble."

}


# This keeps track of all the quests
quest_log = {
    "The Dark King's Favorite Drink": "not_started",
    "Franky's Super Fuel": "not_started",
    "Camie's Lost Starfish": "not_started",
    "Duval's Rosy Repair": "not_started",
    "A Hunter's Priceless Tip": "not_started"
}

# This is a dictionary containing all the map values
world_map = {
    "sunny dock": {
        "name": "Thousand Sunny Dock",
        "description": "The Thousand Sunny, your magnificent ship, is docked here. The air smells of salt and adventure.",
        "exits": {"north": "sabaody archipelago"},
        "npcs": {
            "franky": {
                "name": "Franky",
                "dialogue": "'OW! The Sunny is in SUPER condition, but I'm all out of my special cola! Can't do any work without it!'"
            }
        }
    },
    "sabaody archipelago": {
        "name": "Sabaody Archipelago (Grove 13)",
        "description": "You are in the central area of the bustling Sabaody Archipelago. Giant mangrove trees reach for the sky.",
        "exits": {"north": "coating workshop", "south": "sunny dock", "west": "sabaody park", "east": "shakkys bar"},
        "npcs": {
            "bounty hunter": {
                "name": "Bounty Hunter",
                "dialogue": "'Tch... so many high-bounty pirates. Information is key here, but it ain't free. Bring me something valuable, maybe I'll share a secret.'"
            }
        }
    },
    "sabaody park": {
        "name": "Sabaody Park",
        "description": "A bubbly amusement park full of laughter and strange rides. The ferris wheel gives a great view of the island.",
        "exits": {"east": "sabaody archipelago"},
        "npcs": {
            "duval": {
                "name": "Duval",
                "dialogue": "'Behold my handsome face! My Rosy Life Riders are the fastest... or they would be if one of them hadn't broken down!'"
            },
            "pappag": {
                "name": "Pappag",
                "dialogue": "'Oh, thank you for finding me! I got distracted by the rides. Camie must be so worried!'"
            }
        }
    },
    "shakkys bar": {
        "name": "Shakky's Rip-Off Bar",
        "description": "A quiet, slightly dusty bar run by Shakky. You can sense a lot of information passes through this place.",
        "exits": {"west": "sabaody archipelago"},
        "npcs": {
            "shakky": {
                "name": "Shakky",
                "dialogue": "'Welcome to my bar, kid. What can I get for you? Heard you're looking for Rayleigh...'"
            }
        }
    },
    "coating workshop": {
        "name": "Coating Workshop",
        "description": "A workshop where a skilled mechanic coats ships for undersea travel. The smell of resin is strong here.",
        "exits": {"south": "sabaody archipelago", "down": "fish-man island"},
        "npcs": {
            "rayleigh": {
                "name": "Silvers Rayleigh",
                "dialogue": "'Coating a ship, are you? It's a precise art. Takes time and skill.'"
            }
        }
    },
    "fish-man island": {
        "name": "Fish-Man Island",
        "description": "A breathtaking underwater paradise encased in a giant bubble. Mermaids swim by and the coral glows.",
        "exits": {"up": "coating workshop"},
        "npcs": {
            "camie": {
                "name": "Camie",
                "dialogue": "'Hiii! Welcome to Fish-Man Island! But... I can't find my best friend Pappag anywhere! Have you seen a starfish?'"
            }
        }
    }
}

# --- Character and Player Setup ---


class Character:
    def __init__(self, name, player_class, location="sunny dock"):
        self.name = name
        self.player_class = player_class
        self.location = location


player = Character(name="Luffy", player_class="pirate")
user_inventory = []

# Helper Functions 


def clear_screen():
    
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title):
    
    print(f"\n{Colors.HEADER}{'=' * 50}{Colors.RESET}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title.center(50)}{Colors.RESET}")
    print(f"{Colors.HEADER}{'=' * 50}{Colors.RESET}")


def display_location_info():
    
    loc_id = player.location
    location = world_map[loc_id]

    print_header(location["name"])
    print(f"{Colors.LOCATION} {location['description']} {Colors.RESET}")

    # Format and print exits
    exits = ", ".join(
        [f"{Colors.BOLD}{direction.capitalize()}{Colors.RESET}" for direction in location["exits"].keys()])
    print(f"\n{Colors.ACTION}Exits:{Colors.RESET} {exits}")

    # Format and print NPCs
    if location["npcs"]:
        npcs = ", ".join(
            [f"{Colors.NPC}{npc_data['name']}{Colors.RESET}" for npc_data in location["npcs"].values()])
        print(f"{Colors.ACTION}You see:{Colors.RESET} {npcs}")
    print("-" * 50)


def move_player(direction):

    current_location = world_map[player.location]
    if direction in current_location["exits"]:
        player.location = current_location["exits"][direction]
        clear_screen()
        display_location_info()
    else:
        print(f"{Colors.ERROR}You can't go that way!{Colors.RESET}")


def talk_to_npc(npc_choice):

    npcs_in_area = world_map[player.location]["npcs"]

    if npc_choice not in npcs_in_area:
        print(f"{Colors.ERROR}There's no one here by that name.{Colors.RESET}")
        return

    npc_name = npcs_in_area[npc_choice]["name"]
    print(f"You talk to {Colors.NPC}{npc_name}{Colors.RESET}:")

    prompt = f"""
    You are a character in a text-based adventure game based on One Piece.
    Your Character: {gemini_characters}[{npc_choice}]
    The player's name is '{player.name}'.
    You are currently at '{player.location}'.
    The player has just initiated a conversation with you.
    Generate a single, short, in-character line of dialogue (less than 25 words). Do not include action text like *smirks* or *looks at you*.
    and also write ai generated dialouge in small letters.
    """

    try:
        ai_response = model.generate_content(prompt).text.strip()

    except Exception as e:

        print(f"{Colors.ERROR}[Error generating dialogue: {e}]{Colors.RESET}")
        return None

    # Quest: The Dark King's Favorite Drink
    if npc_choice == "shakky" and quest_log["The Dark King's Favorite Drink"] == "not_started":
        print(f"{Colors.DIALOGUE}'So, you're looking for Rayleigh? He's not easy to get a hold of. Take this bottle of rum to him. It's his favorite. You'll find him at the Coating Workshop.'{Colors.RESET}")
        user_inventory.append("Bottle of Rum")
        quest_log["The Dark King's Favorite Drink"] = "started"
        print(
            f"{Colors.ACTION}[Quest Started: The Dark King's Favorite Drink]{Colors.RESET}")

    # Quest: Franky's Super Fuel (Get from Shakky)
    elif npc_choice == "shakky" and quest_log["Franky's Super Fuel"] == "started":
        print(f"{Colors.DIALOGUE}'Franky's out of fuel again? That guy... Here, take this special cola. It's on the house.'{Colors.RESET}")
        user_inventory.append("Special Cola")
        quest_log["Franky's Super Fuel"] = "in_progress"

    # Quest: Rayleigh's interactions
    elif npc_choice == "rayleigh":
        if "Bottle of Rum" in user_inventory:
            print(f"{Colors.DIALOGUE}'Well, what's this? Ha! Only Shakky knows this brand. She sent you, eh? Alright, you have my attention.'{Colors.RESET}")
            quest_log["The Dark King's Favorite Drink"] = "completed"
            user_inventory.remove("Bottle of Rum")
            print(
                f"{Colors.ACTION}[Quest Completed: The Dark King's Favorite Drink]{Colors.RESET}")
        elif quest_log["Duval's Rosy Repair"] == "started":
            print(f"{Colors.DIALOGUE}'Duval's flying fish broke? Not surprising. Here's a spare gyroscopic stabilizer. That should fix it.'{Colors.RESET}")
            user_inventory.append("Stabilizer")
            quest_log["Duval's Rosy Repair"] = "in_progress"
        else:
            print(
                f"{Colors.DIALOGUE}'Sorry kid, I'm busy. Come back later.'{Colors.RESET}")

    # Quest: Franky's Super Fuel
    elif npc_choice == "franky":
        # if "Special Cola" in user_inventory:
        #     print(f"{Colors.DIALOGUE}'OW! My fuel! You're a lifesaver! SUUUUPER! The Sunny will be ready in no time now!'{Colors.RESET}")
        #     quest_log["Franky's Super Fuel"] = "completed"
        #     user_inventory.remove("Special Cola")
        #     print(
        #         f"{Colors.ACTION}[Quest Completed: Franky's Super Fuel]{Colors.RESET}")
        # elif quest_log["Franky's Super Fuel"] == "not_started":
        #     print(f"{Colors.DIALOGUE}'Can't do any work without my special cola! Maybe Shakky at the bar has some?'{Colors.RESET}")
        #     quest_log["Franky's Super Fuel"] = "started"
        #     print(
        #         f"{Colors.ACTION}[Quest Started: Franky's Super Fuel]{Colors.RESET}")
        # else:
        print(f"{Colors.DIALOGUE}{ai_response}{Colors.RESET}")

    # Quest: Camie's Lost Starfish
    elif npc_choice == "camie":
        if quest_log["Camie's Lost Starfish"] == "not_started":
            print(
                f"{Colors.DIALOGUE}{npcs_in_area[npc_choice]['dialogue']}{Colors.RESET}")
            quest_log["Camie's Lost Starfish"] = "started"
            print(
                f"{Colors.ACTION}[Quest Started: Camie's Lost Starfish]{Colors.RESET}")
        elif "Pappag" in user_inventory:
            print(
                f"{Colors.DIALOGUE}'Pappag! You found him! Thank you so much! Here, take this as a reward!'{Colors.RESET}")
            user_inventory.remove("Pappag")
            user_inventory.append("Rare Pearl")
            quest_log["Camie's Lost Starfish"] = "completed"
            print(
                f"{Colors.ACTION}[Quest Completed: Camie's Lost Starfish]{Colors.RESET}\n{Colors.ACTION}[You received a Rare Pearl!]{Colors.RESET}")
        else:
            print(
                f"{Colors.DIALOGUE}'Please find Pappag! He's a starfish, you can't miss him!'{Colors.RESET}")

    # Quest: Finding Pappag
    elif npc_choice == "pappag" and quest_log["Camie's Lost Starfish"] == "started":
        print(f"{Colors.DIALOGUE}'Oh, you were sent by Camie? I got lost! Can you take me back to her?'{Colors.RESET}")
        user_inventory.append("Pappag")  # Representing him "following" you
        world_map["sabaody park"]["npcs"].pop("pappag")  # He's no longer here
        print(
            f"{Colors.ACTION}[Pappag is now following you. Take him to Camie!]{Colors.RESET}")

    # Quest: Duval's Rosy Repair
    elif npc_choice == "duval":
        if "Stabilizer" in user_inventory:
            print(f"{Colors.DIALOGUE}'Is that... a gyroscopic stabilizer?! Amazing! You've saved my handsome reputation! Thank you!'{Colors.RESET}")
            user_inventory.remove("Stabilizer")
            quest_log["Duval's Rosy Repair"] = "completed"
            print(
                f"{Colors.ACTION}[Quest Completed: Duval's Rosy Repair]{Colors.RESET}")
        elif quest_log["Duval's Rosy Repair"] == "not_started":
            print(
                f"{Colors.DIALOGUE}{npcs_in_area[npc_choice]['dialogue']}{Colors.RESET}")
            print(f"{Colors.DIALOGUE}'I need a special part... maybe that old mechanic Rayleigh at the workshop has one?'{Colors.RESET}")
            quest_log["Duval's Rosy Repair"] = "started"
            print(
                f"{Colors.ACTION}[Quest Started: Duval's Rosy Repair]{Colors.RESET}")
        else:
            print(
                f"{Colors.DIALOGUE}{npcs_in_area[npc_choice]['dialogue']}{Colors.RESET}")

    # Quest: A Hunter's Priceless Tip
    elif npc_choice == "bounty hunter":
        if "Rare Pearl" in user_inventory:
            print(f"{Colors.DIALOGUE}'A rare pearl from Fish-Man Island? That's quite valuable. Alright, a deal's a deal. They say Shakky's not just a bartender... she's got connections to the Revolutionary Army.'{Colors.RESET}")
            user_inventory.remove("Rare Pearl")
            quest_log["A Hunter's Priceless Tip"] = "completed"
            print(
                f"{Colors.ACTION}[Quest Completed: A Hunter's Priceless Tip]{Colors.RESET}")
        elif quest_log["A Hunter's Priceless Tip"] == "not_started" and quest_log["Camie's Lost Starfish"] == "completed":
            quest_log["A Hunter's Priceless Tip"] = "started"
            print(
                f"{Colors.ACTION}[Quest Started: A Hunter's Priceless Tip]{Colors.RESET}")
            print(
                f"{Colors.DIALOGUE}{npcs_in_area[npc_choice]['dialogue']}{Colors.RESET}")
        else:
            print(
                f"{Colors.DIALOGUE}{npcs_in_area[npc_choice]['dialogue']}{Colors.RESET}")

    # Default dialogue if no quest conditions are met
    else:
        print(f"{Colors.DIALOUGE}{ai_response}{Colors.RESET}")


def show_inventory():
    """Displays the player's inventory."""
    print_header("Inventory")
    if not user_inventory:
        print("Your inventory is empty.")
    else:
        for item in user_inventory:
            print(f"- {item}")


def show_quests():
    """Displays the status of all quests."""
    print_header("Quest Log")
    for quest, status in quest_log.items():
        color = Colors.RESET
        if status == "completed":
            color = Colors.NPC  # Green
        elif status == "started" or status == "in_progress":
            color = Colors.DIALOGUE  # Yellow
        print(f"- {quest}: {color}{status.replace('_', ' ').title()}{Colors.RESET}")


def show_help():
    """Displays available commands."""
    print_header("Help")
    print("Available Commands:")
    print(f"- {Colors.BOLD}go [direction]{Colors.RESET} (e.g., 'go north')")
    print(
        f"- {Colors.BOLD}talk [npc name]{Colors.RESET} (e.g., 'talk franky')")
    print(f"- {Colors.BOLD}inventory{Colors.RESET} or {Colors.BOLD}inv{Colors.RESET}")
    print(f"- {Colors.BOLD}quests{Colors.RESET} or {Colors.BOLD}log{Colors.RESET}")
    print(f"- {Colors.BOLD}look{Colors.RESET} - Re-examine your surroundings")
    print(f"- {Colors.BOLD}exit{Colors.RESET} - Quit the game")


def parse_user_input():
    """Parses user input and calls the appropriate function."""
    while True:
        try:
            command = input(
                f"\n{Colors.BOLD}> {Colors.RESET}").lower().strip().split()
            if not command:
                continue

            action = command[0]
            target = " ".join(command[1:]) if len(command) > 1 else None

            if action in ["go", "move", "run"]:
                if target:
                    move_player(target)
                else:
                    print(
                        f"{Colors.ERROR}Where do you want to go? (e.g., 'go north'){Colors.RESET}")

            elif action in ["talk", "interact", "examine"]:
                if target:
                    talk_to_npc(target)
                else:
                    print(
                        f"{Colors.ERROR}Who do you want to talk to? (e.g., 'talk franky'){Colors.RESET}")

            elif action in ["inventory", "inv"]:
                show_inventory()

            elif action in ["quests", "log"]:
                show_quests()

            elif action == "look":
                display_location_info()

            elif action == "help":
                show_help()

            elif action == "exit":
                print(f"{Colors.HEADER}Thanks for playing!{Colors.RESET}")
                sys.exit()

            else:
                print(
                    f"{Colors.ERROR}Unknown command. Type 'help' to see available commands.{Colors.RESET}")

        except (KeyboardInterrupt, EOFError):
            print(f"\n{Colors.HEADER}Thanks for playing!{Colors.RESET}")
            sys.exit()

# Game Setup and Start


def player_details():
    """Gets player details at the start of the game."""
    clear_screen()
    print_header("Character Creation")
    player.name = input(f"Enter your name: {Colors.BOLD}")
    print(f"{Colors.RESET}Welcome, {Colors.BOLD}{player.name}{Colors.RESET}!")

    while True:
        p_class = input(
            f"Choose your class ({Colors.BOLD}pirate{Colors.RESET} or {Colors.BOLD}marine{Colors.RESET}): ").lower()
        if p_class in ["pirate", "marine"]:
            player.player_class = p_class
            print(
                f"You are now a {Colors.BOLD}{player.player_class}{Colors.RESET}!")
            time.sleep(2)
            break
        else:
            print(f"{Colors.ERROR}Invalid class. Please choose again.{Colors.RESET}")


def title_screen():
    """Displays the main title screen and menu."""
    clear_screen()
    title_text = f"""{Colors.HEADER}
    ██████╗ ██╗   ██╗████████╗██╗  ██╗ ██████╗ ███╗   ██╗
    ██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║
    ██████╔╝ ╚████╔╝    ██║   ███████║██║   ██║██╔██╗ ██║
    ██╔═══╝   ╚██╔╝     ██║   ██╔══██║██║   ██║██║╚██╗██║
    ██║        ██║      ██║   ██║  ██║╚██████╔╝██║ ╚████║
    ╚═╝        ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
    {Colors.RESET}
    {Colors.ACTION}          A Python Text-Based Adventure by anmol
    {Colors.RESET}
    """
    print(title_text)
    print_header("Main Menu")
    print("              [1] Start New Game")
    print("              [2] Quit")
    print(f"{Colors.HEADER}{'=' * 50}{Colors.RESET}")

    while True:
        option = input(f"{Colors.BOLD}> {Colors.RESET}")
        if option == "1":
            play_game()
            break
        elif option == "2":
            print("Exiting game...")
            time.sleep(1)
            sys.exit()
        else:
            print(
                f"{Colors.ERROR}Please enter a valid option (1 or 2).{Colors.RESET}")


def play_game():
    """Main function to run the game."""
    player_details()
    clear_screen()
    display_location_info()
    parse_user_input()


if __name__ == "__main__":
    title_screen()


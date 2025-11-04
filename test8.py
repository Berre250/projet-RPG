import random
from collections import Counter

# Classes 
class Player:
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.xp = 0
        self.max_hp = 100
        self.hp = self.max_hp
        self.base_attack = 10
        self.base_defense = 5
        self.inventory = ["Couteau"]  # couteau = arme de départ
        # buffs actifs uniquement pendant un combat (réinitialisés après)
        self.temp_attack = 0
        self.temp_defense = 0

    @property
    def attack(self):
        return self.base_attack + self.temp_attack

    @property
    def defense(self):
        return self.base_defense + self.temp_defense

    def is_alive(self):
        return self.hp > 0

    def gain_xp(self, amount):
        self.xp += amount
        print(f"→ {self.name} gagne {amount} XP (total: {self.xp}).")
        # seuil simple : 50 * niveau
        while self.xp >= self.level * 50:
            self.xp -= self.level * 50
            self.level_up()

    def level_up(self):
        self.level += 1
        self.max_hp += 20
        self.base_attack += 5
        self.base_defense += 3
        self.hp = self.max_hp
        print(f"*** {self.name} passe au niveau {self.level} ! HP, attaque et défense augmentés. ***")

    def reset_combat_buffs(self):
        self.temp_attack = 0
        self.temp_defense = 0

class Monster:
    def __init__(self, name, level):
        self.name = name
        self.level = level
        self.max_hp = 30 + 10 * level
        self.hp = self.max_hp
        self.attack = 5 + 2 * level
        self.defense = 2 + level

    def is_alive(self):
        return self.hp > 0

# Objets et utilisation 
def use_item(player, item_name, monster=None):
    """
    Return True if an action was performed (item used), False otherwise.
    Effects:
    - Potion: soigne 30 HP (ne dépasse pas max_hp)
    - Attack Boost: +10 attack pendant le combat
    - Defense Boost: +10 defense pendant le combat
    """
    if item_name not in player.inventory:
        print("Vous n'avez pas cet objet.")
        return False

    if item_name == "Potion":
        heal = 30
        player.hp = min(player.max_hp, player.hp + heal)
        player.inventory.remove("Potion")
        print(f"Vous buvez une Potion et récupérez {heal} HP (HP: {player.hp}/{player.max_hp}).")
        return True
    
    if item_name == "Couteau":
        player.temp_attack += 15
        player.inventory.remove("Couteau")
        print("Vous utilisez le Couteau : +15 attaques pendant le combat.")
        return True
    
    if item_name == "Attack Boost":
        player.temp_attack += 10
        player.inventory.remove("Attack Boost")
        print("Vous utilisez Attack Boost : +10 attaque pendant le combat.")
        return True

    if item_name == "Defense Boost":
        player.temp_defense += 10
        player.inventory.remove("Defense Boost")
        print("Vous utilisez Defense Boost : +10 défense pendant le combat.")
        return True

    print("Objet inconnu.")
    return False

#  Combat 
def battle(player, monster):
    print(f"\n⚔️  Un {monster.name} (niveau {monster.level}) apparaît ! ⚔️")
    player.reset_combat_buffs()  # s'assure que les buffs sont propres
    while player.is_alive() and monster.is_alive():
        print(f"\n-- Tour --\n{player.name} HP: {player.hp}/{player.max_hp}  |  {monster.name} HP: {monster.hp}/{monster.max_hp}")
        print("Actions : 1) Attaquer  2) Utiliser un objet  3) Fuir")
        choice = input("> ").strip()
        if choice == "1":
            # Calcul dégât : prise en compte d'un léger aléa pour critiques ou échec
            miss = random.random() < 0.05  # 5% 
            crit = random.random() < 0.10  # 10% 
            if miss:
                print("Ton attaque a raté !")
            else:
                base_damage = max(0, player.attack - monster.defense)
                damage = base_damage * (2 if crit else 1)
                monster.hp -= damage
                if crit:
                    print(f"Coup critique ! Tu infliges {damage} dégâts.")
                else:
                    print(f"Tu infliges {damage} dégâts.")
            # vérif si monstre mort avant sa riposte
        elif choice == "2":
            if not player.inventory:
                print("Inventaire vide.")
                continue
            print("Inventaire :", player.inventory)
            item_choice = input("Quel objet utiliser ? (nom exact ou 'annuler')\n> ").strip()
            if item_choice.lower() == "annuler":
                continue
            used = use_item(player, item_choice, monster)
            if not used:
                continue
        elif choice == "3":
            print("Tu fuis le combat et échappes à la récompense.")
            return False
        else:
            print("Choix invalide.")
            continue

        # Si monstre encore vivant, il attaque
        if monster.is_alive():
            miss = random.random() < 0.05
            crit = random.random() < 0.05
            if miss:
                print(f"Le {monster.name} rate son attaque !")
            else:
                base_damage = max(0, monster.attack - player.defense)
                damage = base_damage * (2 if crit else 1)
                player.hp -= damage
                if crit:
                    print(f"Le {monster.name} fait un coup critique et t'inflige {damage} dégâts !")
                else:
                    print(f"Le {monster.name} t'inflige {damage} dégâts.")
        # fin boucle

    # Résultat
    if player.is_alive():
        print(f"\n🎉 Tu as vaincu le {monster.name} !")
        xp_reward = monster.level * 20
        player.gain_xp(xp_reward)
        player.reset_combat_buffs()
        return True
    else:
        print("\n💀 Tu es mort...")
        return False

#  Carte et discriptions 
MAP = [
    ["Forêt", "Clairière", "Grotte"],
    ["Rivière", "Départ",   "Marais"],
    ["Cabane", "Canyon",    "Boss"]
]
MAP_DESCRIPTIONS = {
    "Forêt": "Des arbres denses, l'ombre est partout.",
    "Clairière": "Un endroit calme, des fleurs parsèment le sol.",
    "Grotte": "L'entrée d'une grotte sombre, une odeur de pierre humide.",
    "Rivière": "Une rivière qui coule lentement. L'eau scintille.",
    "Départ": "Ici tu t'es réveillé. Ton sac n'a qu'un couteau.",
    "Marais": "Le sol est boueux et glissant.",
    "Cabane": "Une petite cabane abandonnée.",
    "Canyon": "Des parois élevées. On entend le vent.",
    "Boss": "Un endroit sinistre... on sent la présence du boss."
}
# Position de départ (ligne, colonne)
START_POS = (1, 1)
BOSS_POS = (2, 2)

def random_event(player):
    """Retourne 'monster' ou 'item' aléatoirement, et crée l'entité correspondante."""
    if random.choice([True, False]):
        # Monstre : niveau dépend du joueur + -1..+1
        m_level = max(1, player.level + random.randint(-1, 1))
        monster = Monster("Monstre", m_level)
        return ("monster", monster)
    else:
        item = random.choice(["Potion", "Attack Boost", "Defense Boost"])
        return ("item", item)

def find_item(player, item):
    player.inventory.append(item)
    print(f"🎁 Tu trouves un objet : {item} !")

#  Déplacements 
def move(position, direction):
    x, y = position
    direction = direction.lower()
    if direction in ("n", "north", "go north", "go_north"):
        nx, ny = x - 1, y
    elif direction in ("s", "south", "go south", "go_south"):
        nx, ny = x + 1, y
    elif direction in ("w", "west", "go west", "go_west"):
        nx, ny = x, y - 1
    elif direction in ("e", "east", "go east", "go_east"):
        nx, ny = x, y + 1
    else:
        return position  # commande inconnue  pas de mouvement

    # Vérifie limites
    if 0 <= nx < len(MAP) and 0 <= ny < len(MAP[0]):
        return (nx, ny)
    else:
        print("Tu ne peux pas aller dans cette direction (bord de la carte).")
        return position

#  Menu 
def start_game():
    name = input("Entrez votre nom : ").strip() or "Hero" #strip() pour éviter les espaces vides
    player = Player(name)
    position = START_POS
    print(f"\nBienvenue {player.name} ! {MAP_DESCRIPTIONS['Départ']}")
    print("Tape 'help' pour les commandes.\n")

    while True:
        if not player.is_alive():
            print("Tu es mort. Retour au menu principal.")
            break

        cmd = input("Action (n/s/e/w, look, inventory, quit) > ").strip().lower()
        if cmd in ("quit", "q"):
            print("Retour au menu principal.")
            break
        if cmd in ("help",):
            print("Commandes : n/north, s/south, e/east, w/west, look, inventory, stats, quit")
            continue
        if cmd in ("inventory", "inv"):
            print("Inventaire :", player.inventory)
            continue
        if cmd in ("stats",):
            print(f"{player.name} — Niveau {player.level} — XP: {player.xp} — HP: {player.hp}/{player.max_hp} — Att: {player.base_attack} — Def: {player.base_defense}")
            continue
        if cmd in ("look",):
            place = MAP[position[0]][position[1]]
            print(place, ":", MAP_DESCRIPTIONS.get(place, "Aucune description."))
            continue

        # déplacement
        new_pos = move(position, cmd)
        if new_pos == position:
            # soit commande inconnue, soit tentative hors carte
            continue

        position = new_pos
        place = MAP[position[0]][position[1]]
        print(f"\n🌍 Tu arrives à : {place}")
        print(MAP_DESCRIPTIONS.get(place, ""))

        # Aucun aléa sur Départ ni sur Boss
        if position == START_POS:
            print("C'est le point de départ. Rien d'intéressant ici.")
            continue

        if position == BOSS_POS:
            print("!!! Tu rencontres le Boss final !!!")
            boss = Monster("Boss final", max(6, player.level + 4))
            fought = battle(player, boss)
            if fought and player.is_alive():
                print("\n🏆 FELICITATIONS ! Tu as vaincu le boss et sors de la forêt !")
            else:
                print("\nLe boss t'a vaincu ou tu as fui. Fin de la partie.")
            break

        # Événement aléatoire sur autres cases
        event_type, payload = random_event(player)
        if event_type == "monster":
            fought = battle(player, payload)
            if not fought and not player.is_alive():
                # Si mort, sortie de la boucle principale 
                pass
        elif event_type == "item":
            find_item(player, payload)

#  Menu principal 
def main_menu():
    while True:
        print("\n=== MENU PRINCIPAL ===")
        print("1) Nouvelle Partie")
        print("2) Charger (non disponible)")
        print("3) Quitter")
        choix = input("> ").strip()
        if choix == "1":
            start_game()
        elif choix == "2":
            print("Chargement non disponible ici.")
        elif choix == "3":
            print("À bientôt !")
            break
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    main_menu()


# test8.py
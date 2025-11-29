import random

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

#  Combat 
import tkinter as tk
from tkinter import ttk
import random

# ---------------------------
# FONCTION battle (UI riche)
# ---------------------------
def battle(root, player, monster, callback_end):
    """
    Fenêtre de combat riche : barres HP, sprites (emoji/fichiers), animations,
    log coloré, boutons stylés.
    Signature compatible avec ton RPGApp.
    """

    # Top-level
    win = tk.Toplevel(root)
    win.title(f"Combat : {player.name} vs {monster.name}")

    # ✅ Taille suffisante dès l'ouverture pour voir les boutons
    win.geometry("1200x650")
    win.minsize(1100, 600)

# ✅ Centrage automatique
    x = (win.winfo_screenwidth() // 2) - (1200 // 2)
    y = (win.winfo_screenheight() // 2) - (650 // 2)
    win.geometry(f"+{x}+{y}")


    # Styles
    FONT_BOLD = ("Consolas", 11, "bold")
    FONT_REG = ("Consolas", 11)
    ACCENT = "#ffd166"
    BG = "#0b0f12"
    FG = "#eaf6ff"
    BTN_BG = "#1f6f5d"
    BTN_FG = "#fff"

    # Main frames
    top_frame = tk.Frame(win, bg=BG, bd=0, highlightthickness=0)
    top_frame.pack(fill="x", padx=12, pady=0)

    center_frame = tk.Frame(win, bg=BG, bd=0, highlightthickness=0)
    center_frame.pack(fill="both", expand=True, padx=12, pady=0)

    bottom_frame = tk.Frame(win, bg=BG, bd=0, highlightthickness=0)
    bottom_frame.pack(fill="x", padx=12, pady=0)


    # ---------------------------
    # Top: title + HP bars
    # ---------------------------
    title_lbl = tk.Label(top_frame, text=f"⚔️ Combat : {player.name}  —  {monster.name}",
                        font=("Montserrat", 14, "bold"), bg=BG, fg=ACCENT)
    title_lbl.pack(side="left")

    # Player stats box (left)
    p_frame = tk.Frame(top_frame, bg=BG)
    p_frame.pack(side="left", padx=18)

    p_name = tk.Label(p_frame, text=player.name, font=FONT_BOLD, bg=BG, fg="#b7ffc9")
    p_name.pack(anchor="w")
    p_hp_label = tk.Label(p_frame, text=f"HP: {player.hp}/{player.max_hp}", font=FONT_REG, bg=BG, fg=FG)
    p_hp_label.pack(anchor="w")
    p_hp_bar = ttk.Progressbar(p_frame, length=180, maximum=player.max_hp)
    p_hp_bar['value'] = player.hp
    p_hp_bar.pack(anchor="w", pady=(4,0))

    # Monster stats box (right)
    m_frame = tk.Frame(top_frame, bg=BG)
    m_frame.pack(side="right", padx=18)

    m_name = tk.Label(m_frame, text=monster.name, font=FONT_BOLD, bg=BG, fg="#ffd2d2")
    m_name.pack(anchor="e")
    m_hp_label = tk.Label(m_frame, text=f"HP: {monster.hp}/{monster.max_hp}", font=FONT_REG, bg=BG, fg=FG)
    m_hp_label.pack(anchor="e")
    m_hp_bar = ttk.Progressbar(m_frame, length=180, maximum=monster.max_hp)
    m_hp_bar['value'] = monster.hp
    m_hp_bar.pack(anchor="e", pady=(4,0))

    # ---------------------------
    # Center: sprites + log
    # ---------------------------
    left_center = tk.Frame(center_frame, bg=BG)
    left_center.pack(side="left", fill="y", padx=(0,12))

    center_center = tk.Frame(center_frame, bg=BG)
    center_center.pack(side="left", fill="both", expand=True)

    right_center = tk.Frame(center_frame, bg=BG)
    right_center.pack(side="right", fill="y", padx=(12,0))


    # Sprite area (left)
    sprite_canvas = tk.Canvas(left_center, width=220, height=220, bg="#071011", highlightthickness=0)
    sprite_canvas.pack(pady=6)

    # Try load images if object provided (player.sprite_path / monster.sprite_path)
    player_img = None
    monster_img = None
    if hasattr(player, "sprite_path"):
        player_img = try_load_image(getattr(player, "sprite_path"))
    if hasattr(monster, "sprite_path"):
        monster_img = try_load_image(getattr(monster, "sprite_path"))

    # Fallback emoji
    player_emoji = getattr(player, "emoji", "🧍")
    monster_emoji = getattr(monster, "emoji", "👾")

    # Draw placeholders (we will keep references)
    sprite_items = {}
    # player at left
    if player_img:
        p_img_obj = sprite_canvas.create_image(60, 110, image=player_img)
        sprite_items['p_img'] = p_img_obj
    else:
        p_text = sprite_canvas.create_text(60, 110, text=player_emoji, font=("Segoe UI Emoji", 48))
        sprite_items['p_text'] = p_text

    # monster at right
    if monster_img:
        m_img_obj = sprite_canvas.create_image(160, 110, image=monster_img)
        sprite_items['m_img'] = m_img_obj
    else:
        m_text = sprite_canvas.create_text(160, 110, text=monster_emoji, font=("Segoe UI Emoji", 56))
        sprite_items['m_text'] = m_text

    # Center log
    log_label = tk.Label(center_center, text="Journal de combat", font=FONT_BOLD, bg=BG, fg=ACCENT)
    log_label.pack(anchor="w")
    log = tk.Text(center_center, height=10, bg="#071018", fg="#dfefff", font=("Consolas", 11), wrap="word")
    log.pack(fill="both", expand=True, pady=6)

    # Color tags
    log.tag_configure("player", foreground="#b7ffc9")
    log.tag_configure("monster", foreground="#ffd2d2")
    log.tag_configure("crit", foreground="#ffdd57", font=("Consolas", 11, "bold"))
    log.tag_configure("info", foreground="#9ecbff")
    log.tag_configure("warn", foreground="#ff9b9b")

    def log_msg(msg, tag="info"):
        log.insert("end", msg + "\n", tag)
        log.see("end")

    # Forcer une largeur pour que les boutons ne disparaissent pas
    right_center.pack_propagate(False)
    right_center.config(width=200)

    info_label = tk.Label(
        right_center,
        text="Actions",
        font=FONT_BOLD,
        bg=BG,
        fg=ACCENT
    )
    info_label.pack(pady=(12, 8))

    btn_frame = tk.Frame(right_center, bg=BG)
    btn_frame.pack(pady=6)

    btn_cfg = {
        "width": 16,
        "height": 1,
        "bg": BTN_BG,
        "fg": BTN_FG,
        "font": ("Arial", 11, "bold"),
        "bd": 0
    }

    attack_btn = tk.Button(btn_frame, text="⚔️ Attaquer", **btn_cfg)
    item_btn   = tk.Button(btn_frame, text="🎒 Objet", **btn_cfg)
    flee_btn   = tk.Button(btn_frame, text="🏃 Fuir", **btn_cfg)

    attack_btn.pack(pady=8)
    item_btn.pack(pady=8)
    flee_btn.pack(pady=8)


    # Disable/enable helper
    def set_buttons(state: bool):
        s = "normal" if state else "disabled"
        attack_btn.config(state=s)
        item_btn.config(state=s)
        flee_btn.config(state=s)

    # ---------------------------
    # Update UI helpers
    # ---------------------------
    def update_bars():
        p_hp_label.config(text=f"HP: {player.hp}/{player.max_hp}")
        p_hp_bar['maximum'] = max(1, player.max_hp)
        p_hp_bar['value'] = max(0, player.hp)

        m_hp_label.config(text=f"HP: {monster.hp}/{monster.max_hp}")
        m_hp_bar['maximum'] = max(1, monster.max_hp)
        m_hp_bar['value'] = max(0, monster.hp)

    def flash_text(txt, color="#ffdd57", duration=600):
        # temporaire : affiche un texte au centre qui disparait
        x = sprite_canvas.winfo_width()//2
        y = 20
        t = sprite_canvas.create_text(x, y, text=txt, font=("Consolas", 14, "bold"), fill=color)
        def _del():
            sprite_canvas.delete(t)
        win.after(duration, _del)

    # Simple shake animation for an item (player/monster) on canvas
    def shake(item_key, intensity=6, steps=6, delay=30):
        if item_key not in sprite_items:
            return
        idx = sprite_items[item_key]
        orig = sprite_canvas.coords(idx)
        if not orig:
            return
        ox, oy = orig if len(orig) >= 2 else (orig[0], orig[1])
        def _shake_step(i):
            if i >= steps:
                sprite_canvas.coords(idx, ox, oy)
                return
            dx = random.randint(-intensity, intensity)
            dy = random.randint(-intensity, intensity)
            sprite_canvas.coords(idx, ox+dx, oy+dy)
            win.after(delay, lambda: _shake_step(i+1))
        _shake_step(0)

    # ---------------------------
    # Combat logic & animation sequence
    # ---------------------------
    def compute_damage(attacker, defender):
        miss = random.random() < 0.05
        crit = random.random() < 0.10
        if miss:
            return 0, miss, crit
        base = max(0, getattr(attacker, "attack", getattr(attacker, "base_attack", 1)) - getattr(defender, "defense", getattr(defender, "base_defense", 0)))
        dmg = base * (2 if crit else 1)
        return int(dmg), miss, crit

    # Attack sequence: disable buttons, animate player, apply dmg, animate monster retaliate...
    def on_attack():
        set_buttons(False)
        # player attack animation: move player sprite slightly forward and back
        # determine damage first
        dmg, miss, crit = compute_damage(player, monster)
        if miss:
            log_msg(f"Tu rates ton attaque !", "warn")
            flash_text("MISS", color="#ff6b6b")
        else:
            if crit:
                log_msg(f"COUP CRITIQUE ! Tu infliges {dmg} dégâts.", "crit")
                flash_text("CRITIQUE !", color="#ffdd57")
            else:
                log_msg(f"Tu infliges {dmg} dégâts.", "player")
            monster.hp = max(0, monster.hp - dmg)

        update_bars()
        # animate monster shake when hit
        if dmg > 0:
            shake('m_text' if 'm_text' in sprite_items else 'm_img', intensity=8, steps=8, delay=25)

        # check monster death with short delay to allow animation
        win.after(350, lambda: after_player_attack(dmg, miss, crit))

    def after_player_attack(dmg, miss, crit):
        if monster.hp <= 0:
            log_msg(f"🎉 Tu as vaincu {monster.name} !", "info")
            # award xp
            try:
                player.gain_xp(monster.level * 20)
            except Exception:
                pass
            update_bars()
            win.after(400, lambda: [win.destroy(), callback_end(True, False)])
            return
        # Monster retaliates after small delay
        win.after(300, monster_retaliate)

    def monster_retaliate():
        dmg, miss, crit = compute_damage(monster, player)
        if miss:
            log_msg(f"{monster.name} rate son attaque !", "info")
        else:
            if crit:
                log_msg(f"{monster.name} inflige {dmg} dégâts (CRITIQUE) !", "crit")
                flash_text("CRITIQUE !", color="#ff6b6b")
            else:
                log_msg(f"{monster.name} inflige {dmg} dégâts.", "monster")
            player.hp = max(0, player.hp - dmg)
            shake('p_text' if 'p_text' in sprite_items else 'p_img', intensity=5, steps=6, delay=25)
        update_bars()
        # check player death
        if player.hp <= 0:
            log_msg("💀 Tu es mort...", "warn")
            win.after(400, lambda: [win.destroy(), callback_end(False, False)])
            return
        set_buttons(True)

    def on_items():
        if not getattr(player, "inventory", None):
            log_msg("Inventaire vide.", "warn")
            return
        
        # Fenêtre popup
        inv_win = tk.Toplevel(win)
        inv_win.title("Inventaire")
        inv_win.geometry("280x300")
        inv_win.configure(bg="#0b0f12")
        inv_win.transient(win)
        inv_win.grab_set()

        lbl = tk.Label(inv_win, text="Choisissez un objet :", 
                    bg="#0b0f12", fg="#ffd166", font=("Consolas", 12, "bold"))
        lbl.pack(pady=5)

        # Zone liste
        listbox = tk.Listbox(inv_win, bg="#071018", fg="#dfefff", 
                            selectmode="single", font=("Consolas", 11))
        listbox.pack(fill="both", expand=True, padx=10, pady=10)

        # Remplir liste
        for it in player.inventory:
            listbox.insert("end", it)

        # Boutons
        btn_frame = tk.Frame(inv_win, bg="#0b0f12")
        btn_frame.pack(pady=10)

        def use_selected():
            sel = listbox.curselection()
            if not sel:
                return
            item = listbox.get(sel[0])

            # ============================
            # 🎒 OBJETS UTILISABLES
            # ============================
            
            # 1) Potion — soigne
            if item == "Potion":
                heal = 30
                player.hp = min(player.max_hp, player.hp + heal)
                log_msg(f"Tu utilises une Potion : +{heal} HP.", "player")
                player.inventory.remove(item)
                update_bars()

            # 2) Couteau — inflige 10 dégâts au monstre
            elif item == "Couteau":
                dmg = 10
                monster.hp = max(0, monster.hp - dmg)
                log_msg(f"Tu lances un Couteau : {dmg} dégâts infligés au monstre !", "player")
                player.inventory.remove(item)
                update_bars()
                # Animation du monstre frappé
                shake('m_text' if 'm_text' in sprite_items else 'm_img', intensity=8)

            # 3) Hache — inflige 30 dégâts
            elif item == "Hache":
                dmg = 30
                monster.hp = max(0, monster.hp - dmg)
                log_msg(f"Tu frappes avec une Hache : {dmg} dégâts infligés !", "player")
                player.inventory.remove(item)
                update_bars()
                shake('m_text' if 'm_text' in sprite_items else 'm_img', intensity=10)    

            # 3) Sabre — inflige 20 dégâts
            elif item == "Sabre":
                dmg = 20
                monster.hp = max(0, monster.hp - dmg)
                log_msg(f"Tu frappes avec un Sabre : {dmg} dégâts infligés !", "player")
                player.inventory.remove(item)
                update_bars()
                shake('m_text' if 'm_text' in sprite_items else 'm_img', intensity=10)

            # 3) Epee — inflige 20 dégâts
            elif item == "Epee":
                dmg = 25
                monster.hp = max(0, monster.hp - dmg)
                log_msg(f"Tu frappes avec un Sabre : {dmg} dégâts infligés !", "player")
                player.inventory.remove(item)
                update_bars()
                shake('m_text' if 'm_text' in sprite_items else 'm_img', intensity=10)    

            # 4) Arc — inflige 15 dégâts
            elif item == "Arc":
                dmg = 15
                monster.hp = max(0, monster.hp - dmg)
                log_msg(f"Tu tires une flèche : {dmg} dégâts infligés !", "player")
                player.inventory.remove(item)
                update_bars()
                shake('m_text' if 'm_text' in sprite_items else 'm_img', intensity=10)

            # 5) Attack Boost — augmente attack pour tout le combat
            elif item == "Attack Boost":
                player.temp_attack += 5
                log_msg("Ton attaque augmente de +5 ⚔️ (temporaire)", "player")
                player.inventory.remove(item)

            # 6) Defense Boost — augmente defense pour tout le combat
            elif item == "Defense Boost":
                player.temp_defense += 5
                log_msg("Ta défense augmente de +5 🛡️ (temporaire)", "player")
                player.inventory.remove(item)

            # 7) Si objet inconnu
            else:
                log_msg(f"Objet '{item}' non utilisable pour le moment.", "warn")

            # Si le monstre meurt à cause d'un objet offensif
            if monster.hp <= 0:
                log_msg(f"🎉 Tu as vaincu {monster.name} grâce à {item} !", "player")
                win.after(400, lambda: [inv_win.destroy(), win.destroy(), callback_end(True, False)])
                return

            inv_win.destroy()
            update_bars()


        use_btn = tk.Button(btn_frame, text="Utiliser", width=10, bg="#1f6f5d", fg="white",
                            font=("Arial", 10, "bold"), command=use_selected)
        cancel_btn = tk.Button(btn_frame, text="Annuler", width=10, bg="#555", fg="white",
                            font=("Arial", 10, "bold"), command=inv_win.destroy)

        use_btn.grid(row=0, column=0, padx=6)
        cancel_btn.grid(row=0, column=1, padx=6)


    def on_flee():
        # attempt flee chance
        success = random.random() < 0.6
        if success:
            log_msg("✅ Tu réussis à fuir.", "info")
            win.destroy()
            callback_end(False, True)
        else:
            log_msg("❌ Fuite échouée ! Le monstre attaque.", "warn")
            set_buttons(False)
            win.after(300, monster_retaliate)

    # Bind actions
    attack_btn.config(command=on_attack)
    item_btn.config(command=on_items)
    flee_btn.config(command=on_flee)

    # initial log + focus
    log_msg(f"Un {monster.name} apparaît ! Niveau {monster.level}", "info")
    update_bars()
    set_buttons(True)

    # Ensure window closes cleanly
    def on_close():
        # If user closes window, treat as flee
        try:
            win.destroy()
        except:
            pass
        callback_end(False, True)

    win.update_idletasks()
    
    win.protocol("WM_DELETE_WINDOW", on_close)

    # Keep references to images so tkinter doesn't GC them
    win._player_img = player_img
    win._monster_img = monster_img


#  Carte et discriptions 
MAP = [
    ["Forêt", "Clairière", "Grotte", "Montagne", "Lac"],
    ["Rivière", "Départ", "Marais", "Plaines", "Temple"],
    ["Cabane", "Canyon", "Chateau", "Village", "Colline"],
    ["Désert", "Ruines", "Mine", "Fort", "Tour"],
    ["Port", "Forêt ancienne", "Caverne", "Prairie", "Boss"] ]
MAP_DESCRIPTIONS = {
    "Forêt": "Des arbres denses, l'ombre est partout.",
    "Clairière": "Un endroit calme, des fleurs parsèment le sol.",
    "Grotte": "L'entrée d'une grotte sombre, une odeur de pierre humide.",
    "Rivière": "Une rivière qui coule lentement. L'eau scintille.",
    "Départ": "Ici tu t'es réveillé. Ton sac n'a qu'un couteau.",
    "Marais": "Le sol est boueux et glissant.",
    "Cabane": "Une petite cabane abandonnée.",
    "Canyon": "Des parois élevées. On entend le vent.",
    "Boss": "Un endroit sinistre... on sent la présence du boss.",
    "Montagne": "Des sommets enneigés dominent le paysage.",
    "Lac": "Un grand lac paisible aux reflets argentés.",
    "Village": "Un petit village avec des habitants amicaux.",
    "Temple": "Un ancien temple oublié par le temps.",
    "Château": "Le château du roi, majestueux et protégé."
}
# Position de départ (ligne, colonne)
START_POS = (1, 1)
BOSS_POS = (4, 4)

def random_event(player):
    """Retourne 'monster' ou 'item' aléatoirement, et crée l'entité correspondante."""
    if random.choice([True, False]):
        # Monstre : niveau dépend du joueur + -1..+1
        m_level = max(1, player.level + random.randint(-1, 1))
        monster = Monster("Monstre", m_level)
        return ("monster", monster)
    else:
        item = random.choice(["Potion", "Attack Boost", "Defense Boost", "Épée", "Hache", "Arc"])

        return ("item", item)



if __name__ == "__main__":
    main()


# test8.py
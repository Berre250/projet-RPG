import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import copy
from test8 import *

# =======================
# Application principale
# =======================
class RPGApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Forest RPG - Enhanced (5x5)")
        self.geometry("1024x640")
        self.resizable(False, False)
        self.configure(bg="#111213")

        self.player = None
        self.position = START_POS

        self._build_menu_screen()

    # -----------------------
    # Menu principal
    # -----------------------
    def _build_menu_screen(self):
        for w in self.winfo_children():
            w.destroy()
        frame = tk.Frame(self, bg="#0f1720")
        frame.pack(fill="both", expand=True)

        title = tk.Label(frame, text="🌲 Forest RPG", font=("Montserrat", 38, "bold"), fg="#b9ffd6", bg="#0f1720")
        title.pack(pady=24)

        btn_new = tk.Button(frame, text="Nouvelle Partie", font=("Arial", 16), width=22, bg="#2ecc71", fg="#062b12", command=self.new_game)
        btn_load = tk.Button(frame, text="Charger Partie", font=("Arial", 16), width=22, bg="#f6c85f", fg="#3a2b00", command=self.load_game)
        btn_quit = tk.Button(frame, text="Quitter", font=("Arial", 16), width=22, bg="#ff6b6b", fg="#2b0a0a", command=self.quit)

        btn_new.pack(pady=10)
        btn_load.pack(pady=10)
        btn_quit.pack(pady=10)

        hint = tk.Label(frame, text="(Sauvegarde temporaire — disparaît à la fermeture)", bg="#0f1720", fg="#cbd5ce")
        hint.pack(pady=8)

    def new_game(self):
        name = simpledialog.askstring("Nom du joueur", "Entrez votre nom :", parent=self)
        if name is None:
            return
        name = name.strip() or "Héros"
        self.player = Player(name)
        self.position = START_POS
        self._build_game_screen()

    def load_game(self):
        global saved_game
        if saved_game is None:
            messagebox.showwarning("Charger", "Aucune sauvegarde disponible.")
            return
        self.player, self.position = copy.deepcopy(saved_game)
        self._build_game_screen()

    # -----------------------
    # Écran de jeu
    # -----------------------
    def _build_game_screen(self):
        for w in self.winfo_children():
            w.destroy()

        # top: titre + minimap
        top = tk.Frame(self, bg="#0f1720")
        top.pack(fill="x", padx=12, pady=10)

        title = tk.Label(top, text=f"🌲 Forest RPG — Joueur: {self.player.name} (Nv {self.player.level})",
                        font=("Arial", 16, "bold"), bg="#0f1720", fg="#eafff0")
        title.pack(side="left", padx=8)

        # mini-map dynamique (adaptée à taille MAP)
        map_side = 220
        self.map_canvas = tk.Canvas(top, width=map_side, height=map_side, bg="#0b0c0d", highlightthickness=0)
        self.map_canvas.pack(side="right", padx=18)
        self._draw_minimap()

        # center: description + log + right panel
        center = tk.Frame(self, bg="#0b0f10")
        center.pack(fill="both", expand=True, padx=12, pady=6)

        # left center: description (top) + log (below)
        left_center = tk.Frame(center, bg="#0b0f10")
        left_center.pack(side="left", fill="both", expand=True)

        self.desc_label = tk.Label(left_center, text="", font=("Arial", 13), wraplength=540, justify="left", bg="#0b0f10", fg="#f3fff5")
        self.desc_label.pack(anchor="nw", pady=6, padx=6)

        self.info_text = tk.Text(left_center, width=68, height=22, bg="#051014", fg="#cfe8c6", font=("Consolas", 11))
        self.info_text.pack(padx=6, pady=6)

        # right panel: stats + controls
        right = tk.Frame(center, bg="#0c1313", width=260)
        right.pack(side="right", fill="y", padx=6, pady=6)

        self.stats_label = tk.Label(right, text=self._stats_text(), font=("Consolas", 11), bg="#0c1313", fg="#dff6e0", justify="left")
        self.stats_label.pack(pady=12, padx=8)

        # movement buttons (grid)
        mv_frame = tk.Frame(right, bg="#0c1313")
        mv_frame.pack(pady=8)
        btn_cfg = {"width": 12, "height": 1, "bg": "#164e63", "fg": "#e6fff9", "font": ("Arial", 10, "bold")}
        tk.Button(mv_frame, text="↑ Nord", command=lambda: self.move_player("north"), **btn_cfg).grid(row=0, column=1, padx=4, pady=4)
        tk.Button(mv_frame, text="← Ouest", command=lambda: self.move_player("west"), **btn_cfg).grid(row=1, column=0, padx=4, pady=4)
        tk.Button(mv_frame, text="→ Est", command=lambda: self.move_player("east"), **btn_cfg).grid(row=1, column=2, padx=4, pady=4)
        tk.Button(mv_frame, text="↓ Sud", command=lambda: self.move_player("south"), **btn_cfg).grid(row=2, column=1, padx=4, pady=4)

        # actions
        act_cfg = {"width": 24, "bg": "#2b6f4a", "fg": "#fff", "font": ("Arial", 11, "bold")}
        tk.Button(right, text="Inventaire", command=self.show_inventory, **act_cfg).pack(pady=6)
        tk.Button(right, text="Sauvegarder (mémoire)", command=self.save_game, **act_cfg).pack(pady=6)
        tk.Button(right, text="Retour au menu", command=self._on_return_menu, **act_cfg).pack(pady=6)

        # initial update
        self._update_location_ui(initial=True)

    def _draw_minimap(self):
        # dessine grille NxM en fonction de MAP (adaptable)
        self.map_canvas.delete("all")
        rows = len(MAP)
        cols = len(MAP[0])
        w = int(self.map_canvas["width"])
        h = int(self.map_canvas["height"])
        cw = w / cols
        ch = h / rows

        for i in range(rows):
            for j in range(cols):
                x0 = j * cw
                y0 = i * ch
                x1 = x0 + cw
                y1 = y0 + ch
                place = MAP[i][j]
                # couleur selon type (quelques règles simples)
                if place in ("Boss",):
                    bg = "#4a0f0f"
                elif "Forêt" in place:
                    bg = "#1e3d2b"
                elif place in ("Désert",):
                    bg = "#cfa96a"
                elif place in ("Lac", "Rivière", "Port"):
                    bg = "#114b63"
                elif place in ("Montagne", "Canyon"):
                    bg = "#4f4f4f"
                elif place in ("Temple", "Ruines", "Mine", "Château"):
                    bg = "#5a3e36"
                else:
                    bg = "#22332a"
                self.map_canvas.create_rectangle(x0, y0, x1, y1, fill=bg, outline="#081010")
                label = place if len(place) <= 8 else place[:7] + "…"
                self.map_canvas.create_text(x0 + cw/2, y0 + ch/2, text=label, fill="#eaf6ea", font=("Arial", 8))

        # marqueur joueur
        i, j = self.position
        cx = j * cw + cw/2
        cy = i * ch + ch/2
        r = min(cw, ch) * 0.18
        self.map_canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#ffd166", outline="#b37f00")
        self.map_canvas.create_text(cx, cy, text="🧍", font=("Arial", int(r)), anchor="center")

    def _stats_text(self):
        p = self.player
        return f"Nom: {p.name}\nNv: {p.level}  XP: {p.xp}\nHP: {p.hp}/{p.max_hp}\nAtt: {p.base_attack}\nDef: {p.base_defense}\nInv: {len(p.inventory)} items"

    def _update_location_ui(self, initial=False):
        # met à jour description, log, stats, minimap ; déclenche éventuellement un événement
        place = MAP[self.position[0]][self.position[1]]
        self.desc_label.config(text=f"📍 {place}\n\n{MAP_DESCRIPTIONS.get(place,'')}")
        self.info_text.insert("end", f"\n➡️ Tu es maintenant à {place}.\n")
        self.info_text.see("end")
        self.stats_label.config(text=self._stats_text())
        self._draw_minimap()

        if not initial:
            if self.position == START_POS:
                self.info_text.insert("end", "C'est le point de départ. Rien d'intéressant ici.\n")
            elif self.position == BOSS_POS:
                self.info_text.insert("end", "!!! Tu rencontres le Boss final !!!\n")
                self.info_text.see("end")
                self.after(200, self._trigger_boss)
            else:
                # événement aléatoire
                self.after(200, self._trigger_random_event)
        self.info_text.see("end")

    def move_player(self, direction):
        x, y = self.position
        rows = len(MAP); cols = len(MAP[0])
        if direction == "north" and x > 0:
            x -= 1
        elif direction == "south" and x < rows - 1:
            x += 1
        elif direction == "west" and y > 0:
            y -= 1
        elif direction == "east" and y < cols - 1:
            y += 1
        else:
            self.info_text.insert("end", "🚫 Impossible d'aller par là (bord de la carte).\n")
            self.info_text.see("end")
            return
        self.position = (x, y)
        self._update_location_ui()

    def _trigger_random_event(self):
        event, payload = random_event(self.player)
        if event == "item":
            self.player.inventory.append(payload)
            self.info_text.insert("end", f"🎁 Tu trouves un objet : {payload} !\n")
            self.info_text.see("end")
            self.stats_label.config(text=self._stats_text())
        else:
            self.info_text.insert("end", f"⚔️ Un {payload.name} (Nv {payload.level}) apparaît !\n")
            self.info_text.see("end")
            self.after(100, lambda: self._open_combat(payload, is_boss=False))

    def _trigger_boss(self):
        boss = Monster("Boss final", max(6, self.player.level + 4))
        self.info_text.insert("end", f"👑 Boss : {boss.name} (Nv {boss.level}) ! Prépare-toi.\n")
        self.info_text.see("end")
        self.after(200, lambda: self._open_combat(boss, is_boss=True))

    def _open_combat(self, monster: Monster, is_boss: bool):
        def combat_end(victory, fled):
            if victory:
                self.player.gain_xp(monster.level * 20)
                self.info_text.insert("end", f"🎉 Vous avez vaincu {monster.name} ! XP gagné.\n")
                if is_boss:
                    messagebox.showinfo("Victoire", "🏆 Tu as vaincu le boss et gagné le jeu !")
                    self._build_menu_screen()
                    return
            elif fled:
                self.info_text.insert("end", "🏃 Vous avez fui le combat.\n")
            else:
                if not self.player.is_alive():
                    messagebox.showerror("Défaite", "💀 Tu as été vaincu...")
                    self._build_menu_screen()
                    return
            self.stats_label.config(text=self._stats_text())
            self.info_text.see("end")
            self._draw_minimap()

        battle(self, self.player, monster, callback_end=combat_end)

    def show_inventory(self):
        inv = "\n".join(self.player.inventory) if self.player.inventory else "Inventaire vide."
        choice = messagebox.askquestion("Inventaire", f"{inv}\n\nSouhaitez-vous utiliser un objet maintenant ?")
        if choice == "yes":
            item = simpledialog.askstring("Utiliser objet", f"Entrez le nom exact de l'objet à utiliser:", parent=self)
            if item:
                item = item.strip()
                used = self._use_item_global(item)
                if used:
                    self.info_text.insert("end", f"✅ Vous avez utilisé {item}.\n")
                else:
                    self.info_text.insert("end", f"❌ Impossible d'utiliser {item}.\n")
                self.info_text.see("end")
                self.stats_label.config(text=self._stats_text())

    def _use_item_global(self, item_name):
        # utilisation hors-combat : Potion soigne, boosts donnent petit bonus permanent
        if item_name not in self.player.inventory:
            return False
        if item_name == "Potion":
            heal = 30
            self.player.hp = min(self.player.max_hp, self.player.hp + heal)
            self.player.inventory.remove("Potion")
            return True
        if item_name == "Attack Boost":
            self.player.base_attack += 2
            self.player.inventory.remove("Attack Boost")
            return True
        if item_name == "Defense Boost":
            self.player.base_defense += 2
            self.player.inventory.remove("Defense Boost")
            return True
        return False

    def save_game(self):
        global saved_game
        saved_game = (copy.deepcopy(self.player), copy.deepcopy(self.position))
        messagebox.showinfo("Sauvegarde", "💾 Partie sauvegardée en mémoire (temporaire).")

    def _on_return_menu(self):
        if messagebox.askyesno("Retour menu", "Revenir au menu principal ? (La partie est conservée en mémoire)"):
            self._build_menu_screen()

# =======================
# Lancer le jeu
# =======================
def main():
    app = RPGApp()
    app.mainloop()

if __name__ == "__main__":
    main()
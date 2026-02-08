import random
import time

# ==============================
# 角色类 Player
# ==============================

class Player:
    def __init__(self):
        self.max_hp = 100
        self.hp = 100

        self.max_mp = 100
        self.mp = 100

        self.potions = 3
        self.attribute_marks = []  # 属性痕列表

        self.defense = 0
        self.free_mp = False  # 魔力帷幕：攻击不耗蓝

    def restore_full(self):
        """击败精英怪后恢复"""
        self.hp = self.max_hp
        self.mp = self.max_mp
        self.potions = 3
        self.attribute_marks = []
        self.defense = 0
        self.free_mp = False

    def take_damage(self, dmg):
        """受到伤害"""
        dmg = max(0, dmg - self.defense)
        self.hp -= dmg
        print(f"💥 你受到 {dmg} 点伤害！（当前HP={self.hp}）")

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def recover_mp(self, amount):
        self.mp = min(self.max_mp, self.mp + amount)


# ==============================
# 敌人类 Enemy
# ==============================

class Enemy:
    def __init__(self, name, hp, atk):
        self.name = name
        self.hp = hp
        self.atk = atk

    def take_damage(self, dmg):
        self.hp -= dmg
        print(f"🔥 敌人 {self.name} 受到 {dmg} 点伤害！（HP={self.hp}）")


# ==============================
# 基础法术表（掉落武器）
# ==============================

basic_spells = {
    "火": {"mp": 15, "time": 1.0, "damage": 50, "prob": 0.30},
    "雷": {"mp": 15, "time": 1.0, "damage": 65, "prob": 0.10},
    "圣": {"mp": 10, "time": 2.0, "damage": 0,  "prob": 0.10},
    "魔": {"mp": 15, "time": 1.0, "damage": 50, "prob": 0.50},
}
# ==============================
# 强力法术判定表
# ==============================

power_spells = {
    ("火","火","火"): ("爆炸火焰", lambda p,e: e.take_damage(100)),
    ("雷","雷","雷"): ("闪电步伐", lambda p,e: print("⚡ 5秒内闪避升级！")),
    ("圣","圣","圣"): ("圣光庇护", lambda p,e: setattr(p, "defense", p.defense + 40)),
    ("魔","魔","魔"): ("魔光爆炸", lambda p,e: magic_boom(e)),

    ("火","雷"): ("火电闪", lambda p,e: e.take_damage(100)),
    ("火","圣"): ("温热祝福", lambda p,e: warm_bless(p)),
    ("圣","雷"): ("格挡盾", lambda p,e: print("🛡️ 5秒免疫一次伤害！")),

    ("魔","火"): ("鬼火", lambda p,e: dot_damage(e, 20, 5)),
    ("魔","雷"): ("魔力刃", lambda p,e: e.take_damage(125)),
    ("魔","圣"): ("魔力帷幕", lambda p,e: setattr(p, "free_mp", True)),

    ("魔","圣","火"): ("混合吐息", lambda p,e: mix_breath(p,e)),
    ("魔","雷","火"): ("重力球", lambda p,e: e.take_damage(125)),
    ("魔","圣","雷"): ("冰风暴", lambda p,e: print("❄️ 3秒免疫所有伤害！")),
    ("雷","圣","火"): ("白雷", lambda p,e: delayed_damage(e, 200)),
}


# ==============================
# 强力法术效果函数
# ==============================

def dot_damage(enemy, dmg, sec):
    print(f"🔥 持续灼烧 {sec} 秒！")
    for _ in range(sec):
        enemy.take_damage(dmg)

def magic_boom(enemy):
    print("💥 魔光爆炸持续3秒！")
    for _ in range(3):
        enemy.take_damage(30)

def warm_bless(player):
    print("✨ 温热祝福：上限提升至150！")
    player.max_hp = 150
    player.max_mp = 150
    player.hp = 150
    player.mp = 150

def mix_breath(player, enemy):
    enemy.take_damage(50)
    player.heal(50)
    player.recover_mp(50)
    print("🌈 恢复50血量+50蓝量！")

def delayed_damage(enemy, dmg):
    print("⏳ 白雷蓄力5秒后爆发！")
    enemy.take_damage(dmg)


# ==============================
# 判断属性痕组合
# ==============================

def cast_power_spell(player, enemy):
    marks = player.attribute_marks

    if len(marks) < 3:
        print("❌ 属性痕不足3个！")
        return

    key3 = tuple(sorted(marks))
    key2 = tuple(sorted(set(marks)))

    spell = None

    if key3 in power_spells:
        spell = power_spells[key3]
    elif key2 in power_spells:
        spell = power_spells[key2]

    if spell:
        name, effect = spell
        print(f"🌟 释放强力法术：【{name}】！！！")
        effect(player, enemy)
    else:
        print("⚠️ 未识别的组合，没有强力法术触发。")

    player.attribute_marks.clear()
# ==============================
# 动作执行（可被打断）
# ==============================

def perform_action(player, enemy, action):
    """
    action:
    1=基础法术
    2=收集属性痕
    3=释放强力法术
    4=喝药水
    5=闪避
    """

    # 敌人攻击间隔随机
    enemy_attack_time = random.uniform(2, 3)

    def interrupted(duration):
        """判断动作是否会被打断"""
        return duration > enemy_attack_time

    # ========================
    # 1. 基础法术
    # ========================
    if action == 1:
        spell = random.choice(list(basic_spells.keys()))
        data = basic_spells[spell]

        mp_cost = 0 if player.free_mp else data["mp"]
        cast_time = data["time"]
        dmg = data["damage"]

        print(f"你准备释放【{spell}】法术（耗时{cast_time}s）...")

        if interrupted(cast_time):
            print("💥 动作被敌人打断！法术失败！")
            player.take_damage(enemy.atk)
            return

        if player.mp < mp_cost:
            print("❌ 蓝量不足！")
            return

        player.mp -= mp_cost
        enemy.take_damage(dmg)

        # 挂属性痕
        player.attribute_marks.append(spell)
        print(f"✨ 敌人获得属性痕：{spell}")

    # ========================
    # 2. 收集属性痕
    # ========================
    elif action == 2:
        print("你正在收集属性痕（3s）...")

        if interrupted(3):
            print("💥 收集被打断，失败！")
            player.take_damage(enemy.atk)
            return

        player.recover_mp(20)
        print("🔵 回蓝20点！")

    # ========================
    # 3. 强力法术
    # ========================
    elif action == 3:
        cast_power_spell(player, enemy)

    # ========================
    # 4. 喝药水
    # ========================
    elif action == 4:
        if player.potions <= 0:
            print("❌ 药水已用完！")
            return

        print("你正在喝药水（2s）...")

        if interrupted(2):
            print("💥 喝药被打断！")
            player.take_damage(enemy.atk)
            return

        player.potions -= 1
        player.heal(80)
        print(f"🧪 回复80HP！（剩余药水={player.potions}）")

    # ========================
    # 5. 闪避（免疫）
    # ========================
    elif action == 5:
        print("🌀 闪避成功！0.5秒免疫攻击！")
        return
# ==============================
# 主游戏循环
# ==============================

def battle(player, enemy):
    print(f"\n⚔️ 遭遇敌人：{enemy.name}！（HP={enemy.hp}）")

    while enemy.hp > 0 and player.hp > 0:
        print("\n======================")
        print(f"你HP={player.hp}/{player.max_hp} MP={player.mp}/{player.max_mp}")
        print(f"属性痕：{player.attribute_marks}")
        print("行动：1法术 2收集 3强力 4药水 5闪避")

        action = int(input("请选择行动："))

        perform_action(player, enemy, action)

        if enemy.hp <= 0:
            print(f"🎉 你击败了 {enemy.name}！")
            return True

    print("💀 你被击败了...")
    return False


def main():
    player = Player()

    # 5次精英怪
    for i in range(1, 6):
        elite = Enemy(f"精英怪{i}", 500, 30)
        win = battle(player, elite)

        if not win:
            return

        print("🌟 精英怪击败，恢复满状态！")
        player.restore_full()

    # Boss战
    boss = Enemy("Boss1", 1000, 60)
    win = battle(player, boss)

    if win:
        print("🏆 恭喜通关！你击败了最终Boss！")


if __name__ == "__main__":
    main()

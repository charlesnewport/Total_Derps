import pandas as pd
import json

df = pd.read_csv("data_cleaned.csv")

#ensure new unit weapons accounted for
nations = {}

print(df.shape[0])

england_counter = 0

for i in range(df.shape[0]):

	current_unit = df.loc[i]

	#ensure country exists
	if df.loc[i]["Country"] not in nations:

		nations[df.loc[i]["Country"]] = {}

	if current_unit["Category"] in ["Seige", "Ship"]:

		continue

	temp_unit = {

		"unit_size": int(current_unit["Soldiers"]),
		"unit_morale": int(current_unit["Morale"]),
		"unit_discipline": current_unit["Discipline"],

		"unit_class": current_unit["Class"],

		"unit_type": current_unit["Primary weapon"],

		"unit_image": current_unit["Primary weapon"] if not current_unit["Primary weapon"] == "cavalry" else "cavalry" + "_" + current_unit["Class"].lower(),

		"melee_weapon": {

			"attack_skill": int(current_unit["Secondary_Attack"] if current_unit["Class"] == "Missile" else current_unit["Primary_Attack"]),
			"armour_piercing": bool(current_unit["melee_armour_piercing"]),
			"charge_bonus": int(current_unit["Charge bonus"]),
			"bonus_against_cavalry": int(current_unit["bonus_against_cavalry"])

		},

		"has_ranged_weapon": bool(current_unit["Class"] == "Missile"),

		"ranged_weapon": {

			"range": int(current_unit["Range"]),
			"attack_skill": int(current_unit["Primary_Attack"] if current_unit["Class"] == "Missile" else current_unit["Secondary_Attack"]),
			"armour_piercing": bool(current_unit["ranged_armour_piercing"]),
			"ammunition": current_unit["Ammunition"]
		},

		"defence": {

			"defence_skill": int(current_unit["Defence skill"]),
			"armour": int(current_unit["Armour"]),
			"shield": int(current_unit["Shield"]),
			"hitpoints": int(current_unit["Hit points"])

		}

	}

	nations[df.loc[i]["Country"]][current_unit["Name"]] = temp_unit

	json.dump(nations, open("nations.json", "w"))

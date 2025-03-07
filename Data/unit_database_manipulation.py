import pandas as pd
import numpy as np

# print(df["Primary weapon"].unique())

# exit()

nations = {}

main_weapon_dict = {
"Farm implement (Melee)": "peasant",
"Long spear (Melee)": "billman",
"Sword (Melee)": "knight",
"Two-handed axe (Melee)": "axeman",
"Self bow (Missile)": "archer",
"Composite bow (Missile)": "archer",
"Cavalry spear (Melee)": "cavalry",
"Cavalry light lance (Melee)": "cavalry",
"Cavalry heavy lance (Melee)": "cavalry",
"Knife (Melee)": "peasant",
"Melee": "peasant",
"Halberd (Melee)": "axe",
"Poleaxe (Melee)": "axe",
"Bill (Melee)": "billman",
"Longbow (Missile)": "archer",
"Halberd pike (Melee)": "billman",
"Crossbow (Missile)": "crossbow",
"Cavalry weak sword (Melee)": "cavalry",
"Light spear (Melee)": "spearman",
"Steel crossbow (Missile)": "crossbow",
"Pike (Melee)": "pikes"
}#strip all text

def clean_df():

	df = pd.read_csv("units.csv")

	column_headings = df.columns

	rows, columns = df.shape

	for i in range(rows):

		for j in range(columns):

			if type(df.iloc[i, j]) == str:

				df.iloc[i, j] = df.iloc[i, j].strip()

	df = df.fillna(0)

	# df = df.drop_duplicates()

	#remove duplicate peasants - unsure where this error comes from

	df["Primary weapon"] = df.apply(lambda row: "Naval" if row["Category"] == "Ship" else row["Primary weapon"], axis=1)
	df[["Category", "Primary weapon", "Secondary weapon"]] = df.apply(lambda row: (row["Category"], row["Secondary weapon"], row["Primary weapon"]) if row["Category"] == "Siege" else (row["Category"], row["Primary weapon"], row["Secondary weapon"]), axis=1).tolist()

	df["Weapon attributes"] = df["Weapon attributes"].fillna("")

	df["melee_armour_piercing"] = df["Weapon attributes"].map(lambda x: True if str(x).lower().find("armour") else False)
	df["Weapon attributes"] = df["Weapon attributes"].map(lambda x: "" if x == 0 else x)
	df["melee_armour_piercing"] = df["Weapon attributes"].map(lambda x: True if x.lower().find("armour") != -1 else False) & df["Class"].map(lambda x: x != "Missile")
	df["ranged_armour_piercing"] = df["Weapon attributes"].map(lambda x: True if x.lower().find("armour") != -1 else False) & df["Class"].map(lambda x: x == "Missile")
	df["bonus_against_cavalry"] = df["Weapon attributes"].map(lambda x: 0 if str(x).lower().find("=") == -1 else int(x.split("= ")[1]))

	df = df[df["Primary weapon"].map(lambda x: x in main_weapon_dict.keys())]

	df["Primary weapon"] = df["Primary weapon"].map(lambda x: main_weapon_dict[x])

	df.to_csv("data_cleaned.csv", index=False)

clean_df()

exit()

df = pd.read_csv("data_cleaned.csv")

nations = {}

for i in range(df.shape[0]):

	current_unit = df.loc[i]

	if current_unit["Category"] in ["Seige", "Ship"]:

		continue

	if current_unit["Primary weapon"] not in main_weapon_dict:

		continue

	temp_unit = {

		current_unit["Name"]: {

			"unit_size": current_unit["Soldiers"],
			"unit_morale": current_unit["Morale"],
			"unit_discipline": current_unit["Discipline"],

			"unit_class": current_unit["Class"],

			"unit_type": main_weapon_dict[current_unit["Primary weapon"]],

			"melee_weapon": {

				"attack_skill": current_unit["Secondary_Attack"] if current_unit["Class"] == "Missile" else current_unit["Primary_Attack"],
				"armour_piercing": current_unit["Class"] == "Spearmen",
				"charge_bonus": current_unit[0]

			},

			"has_ranged_weapon": True,

			"ranged_weapon": {

				"range": 0,
				"attack_skill": current_unit["Primary_Attack"] if current_unit["Class"] == "Missile" else current_unit["Secondary_Attack"],
				"armour_piercing": True

			},

			"defence": {

				"defence_skill": 0,
				"armour": 0,
				"shield": 0,
				"hitpoints": 0

			}

		}

	}
import pandas as pd
import json
import random

# Load the GeoJSON file into a Python dictionary
with open("output.geojson") as f:
    data = json.load(f)

# Create empty lists to store the properties and geometries
properties = []
geometries = []

# Loop through each feature in the GeoJSON file
for feature in data["features"]:
    # Get the properties and geometry of the feature
    properties.append(feature["properties"])
    geometries.append(feature["geometry"])

# Convert the lists of properties and geometries to dataframes
properties_df = pd.DataFrame(properties)
geometries_df = pd.DataFrame(geometries)

df = pd.concat([properties_df, geometries_df], axis=1)

# Rename the columns "state" to "Kingdom" and "province" to "County"
df.rename(columns={'state': 'Kingdom', 'province': 'County', 'religion': 'Religion', 'culture': 'Culture'}, inplace=True)

def hex_to_rgb(hex_color):
    if not hex_color.startswith("#") or len(hex_color) != 7:
        return None
    return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))


df["color"] = df["color"].astype(str)
df[["red", "green", "blue"]] = df["color"].apply(hex_to_rgb).apply(pd.Series)
df = df.drop("color", axis=1)

names = ['Abingdon','Albrighton', 'Alcester', 'Almondbury', 'Altrincham', 'Amersham', 'Andover', 'Appleby', 'Ashboume', 'Atherstone', 'Aveton', 'Axbridge', 'Aylesbury', 'Baldock', 'Bamburgh', 'Barton', 'Basingstoke', 'Berden', 'Bere', 'Berkeley', 'Berwick', 'Betley', 'Bideford', 'Bingley', 'Birmingham', 'Blandford', 'Blechingley', 'Bodmin', 'Bolton', 'Bootham', 'Boroughbridge', 'Boscastle', 'Bossinney', 'Bramber', 'Brampton', 'Brasted', 'Bretford', 'Bridgetown', 'Bridlington', 'Bromyard', 'Bruton', 'Buckingham', 'Bungay', 'Burton', 'Calne', 'Cambridge', 'Canterbury', 'Carlisle', 'Castleton', 'Caus', 'Charmouth', 'Chawleigh', 'Chichester', 'Chillington', 'Chinnor', 'Chipping', 'Chisbury', 'Cleobury', 'Clifford', 'Clifton', 'Clitheroe', 'Cockermouth', 'Coleshill', 'Combe', 'Congleton', 'Crafthole', 'Crediton', 'Cuddenbeck', 'Dalton', 'Darlington', 'Dodbrooke', 'Drax', 'Dudley', 'Dunstable', 'Dunster', 'Dunwich', 'Durham', 'Dymock', 'Exeter', 'Exning', 'Faringdon', 'Felton', 'Fenny', 'Finedon', 'Flookburgh', 'Fowey', 'Frampton', 'Gateshead', 'Gatton', 'Godmanchester', 'Grampound', 'Grantham', 'Guildford', 'Halesowen', 'Halton', 'Harbottle', 'Harlow', 'Hatfield', 'Hatherleigh', 'Haydon', 'Helston', 'Henley', 'Hertford', 'Heytesbury', 'Hinckley', 'Hitchin', 'Holme', 'Hornby', 'Horsham', 'Kendal', 'Kenilworth', 'Kilkhampton', 'Kineton', 'Kington', 'Kinver', 'Kirby', 'Knaresborough', 'Knutsford', 'Launceston', 'Leighton', 'Lewes', 'Linton', 'Louth', 'Luton', 'Lyme', 'Lympstone', 'Macclesfield', 'Madeley', 'Malborough', 'Maldon', 'Manchester', 'Manningtree', 'Marazion', 'Marlborough', 'Marshfield', 'Mere', 'Merryfield', 'Middlewich', 'Midhurst', 'Milborne', 'Mitford', 'Modbury', 'Montacute', 'Mousehole', 'Newbiggin', 'Newborough', 'Newbury', 'Newenden', 'Newent', 'Norham', 'Northleach', 'Noss', 'Oakham', 'Olney', 'Orford', 'Ormskirk', 'Oswestry', 'Padstow', 'Paignton', 'Penkneth', 'Penrith', 'Penzance', 'Pershore', 'Petersfield', 'Pevensey', 'Pickering', 'Pilton', 'Pontefract', 'Portsmouth', 'Preston', 'Quatford', 'Reading', 'Redcliff', 'Retford', 'Rockingham', 'Romney', 'Rothbury', 'Rothwell', 'Salisbury', 'Saltash', 'Seaford', 'Seasalter', 'Sherston', 'Shifnal', 'Shoreham', 'Sidmouth', 'Skipsea', 'Skipton', 'Solihull', 'Somerton', 'Southam', 'Southwark', 'Standon', 'Stansted', 'Stapleton', 'Stottesdon', 'Sudbury', 'Swavesey', 'Tamerton', 'Tarporley', 'Tetbury', 'Thatcham', 'Thaxted', 'Thetford', 'Thornbury', 'Tintagel', 'Tiverton', 'Torksey', 'Totnes', 'Towcester', 'Tregoney', 'Trematon', 'Tutbury', 'Uxbridge', 'Wallingford', 'Wareham', 'Warenmouth', 'Wargrave', 'Warton', 'Watchet', 'Watford', 'Wendover', 'Westbury', 'Westcheap', 'Weymouth', 'Whitford', 'Wickwar', 'Wigan', 'Wigmore', 'Winchelsea', 'Winkleigh', 'Wiscombe', 'Witham', 'Witheridge', 'Wiveliscombe', 'Woodbury', 'Yeovil'
]
df['Barony'] = [random.choice(names) + random.choice(names) for i in range(len(df))]

# Save the dataframe to an XLS spreadsheet
df.to_excel("cellsData.xlsx", index=False)
# Merge the two dataframes on their index

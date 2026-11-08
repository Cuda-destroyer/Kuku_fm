"""
Synthetic screenplay test fixtures for unit and integration testing.
Contains zero confidential material.
"""

SYNTHETIC_EPISODE_1 = """EPISODE NUMBER: Episode 1
EPISODE LOGLINE: A betrayed heiress uncovers her husband's secret conspiracy at the gala.
CONTINUITY NOTES: First synthetic test episode.

--- SCRIPT START ---

SCENE 01
Scene heading: INT. GRAND BALLROOM – NIGHT
Scene start: 00:00.00
Scene end: 01:45.00

Actions and dialogue:

**CAMERA:**
Start: (00:00.00) | End: (00:02.00)
Wide tracking shot across the glittering chandeliers as guests mingle in black tie.

**LADY ELENA (Cold, Accusing):**
Start: (00:02.00) | End: (00:05.50)
"You signed the deed before you even asked for my hand in marriage!"

**ACTION:**
Start: (00:05.50) | End: (00:08.00)
Lord Marcus drops his champagne glass, shattering crystal against the marble floor.

**LORD MARCUS (Panicked):**
Start: (00:08.00) | End: (00:11.00)
"Who showed you that contract?"

**LADY ELENA (Furious, Unyielding):**
Start: (00:11.50) | End: (00:15.00)
"Your mistress sent it to me with her congratulations."

**ACTION:**
Start: (00:15.00) | End: (00:18.00)
The entire ballroom gasps as Lord Marcus steps toward her, fist clenched in rage.

**LORD MARCUS (Threatening):**
Start: (00:18.00) | End: (00:22.00)
"You will never leave this estate alive with that proof."

**LADY ELENA (Defiant, Whispering):**
Start: (00:22.50) | End: (00:26.00)
"Then you had better kill me right now in front of everyone."

**SOUND FX:**
Start: (00:26.00) | End: (00:28.00)
Ominous bass drone swells.

**CAMERA:**
Start: (00:28.00) | End: (00:30.00)
Cut to black.

--- SCRIPT END ---
"""

SYNTHETIC_EPISODE_WEAK = """EPISODE NUMBER: Episode 2
EPISODE LOGLINE: Two servants discuss the weather and afternoon tea.
CONTINUITY NOTES: Synthetic episode with low emotional intensity and weak hooks.

--- SCRIPT START ---

SCENE 01
Scene heading: INT. KITCHEN – DAY
Scene start: 00:00.00
Scene end: 01:10.00

Actions and dialogue:

**SERVANT JOHN (Calm):**
Start: (00:00.00) | End: (00:04.00)
"It looks like rain outside today."

**SERVANT MARY (Indifferent):**
Start: (00:04.50) | End: (00:08.00)
"Yes, we should bring in the laundry soon."

**SERVANT JOHN (Friendly):**
Start: (00:08.50) | End: (00:12.00)
"I will help you after I finish peeling these potatoes."

**ACTION:**
Start: (00:12.00) | End: (00:16.00)
Mary smiles gently and puts the kettle onto the iron stove.

--- SCRIPT END ---
"""

SYNTHETIC_MALFORMED_TIMESTAMPS = """EPISODE NUMBER: Episode 3
EPISODE LOGLINE: Test script with invalid inverted timestamps.

--- SCRIPT START ---

SCENE 01
Scene heading: INT. OFFICE – NIGHT
Scene start: 01:00.00
Scene end: 00:10.00

Actions and dialogue:

**DETECTIVE COLE:**
Start: (00:50.00) | End: (00:20.00)
"This timestamp is completely backward."

--- SCRIPT END ---
"""

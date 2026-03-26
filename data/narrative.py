"""Narrative text templates for atmospheric flavor and combat descriptions."""

EXPLORATION_AMBIENT = [
    "A cold draft whispers through the corridor...",
    "You hear distant echoes of something moving...",
    "Water drips steadily from the ceiling above.",
    "The air grows thick and stale. Something died here recently.",
    "Your torch flickers, casting dancing shadows on the walls.",
    "A faint scratching sound comes from behind the wall.",
    "The ground is slick with moisture. Watch your step.",
    "You smell sulfur and ash. Something burns ahead.",
    "Ancient runes on the wall glow faintly, then fade.",
    "Cobwebs brush your face as you push through the passage.",
    "A rat scurries past your feet and vanishes into a crack.",
    "The silence here is deafening. Too quiet.",
    "You notice claw marks gouged deep into the stone floor.",
    "A broken weapon lies discarded in the corner, rusted beyond use.",
    "The faint sound of chanting drifts from somewhere below.",
    "Your footsteps echo endlessly down the empty hall.",
    "A chill runs down your spine. You are being watched.",
    "Old bloodstains darken the floor. Whatever happened here was violent.",
    "The walls are damp and covered in a thin layer of slime.",
    "You step on something that crunches. Best not to look down.",
    "A distant roar reverberates through the stone. Something big lurks below.",
    "Torchlight reveals crude drawings scratched into the wall by a previous explorer.",
    "The passage narrows. Claustrophobia sets in.",
    "A gust of warm air carries the scent of decay.",
    "You find a discarded journal. The last entry reads: 'They are coming.'",
]

COMBAT_FLAVOR = {
    "attack": [
        "{attacker} strikes {target} with a mighty blow!",
        "{attacker} lunges forward, weapon flashing at {target}!",
        "{attacker} slashes at {target} with vicious intent!",
        "{attacker} hammers {target} with a crushing strike!",
        "{attacker} catches {target} with a swift attack!",
        "{attacker} delivers a precise strike to {target}!",
        "{attacker} swings hard, connecting solidly with {target}!",
    ],
    "critical": [
        "{attacker} finds a gap in {target}'s defense! Critical hit!",
        "A devastating blow! {attacker} strikes {target}'s weak point!",
        "{attacker} lands a perfect strike on {target}! The impact echoes!",
        "Time seems to slow as {attacker} delivers a masterful critical blow to {target}!",
        "{attacker} strikes true! {target} staggers from the critical hit!",
    ],
    "miss": [
        "{attacker} swings wildly and misses {target}!",
        "{target} sidesteps {attacker}'s clumsy attack!",
        "{attacker}'s blow glances harmlessly off {target}'s guard!",
        "{attacker} overextends and whiffs completely!",
        "{target} ducks under {attacker}'s swing at the last moment!",
        "{attacker} stumbles, the attack sailing wide of {target}!",
    ],
    "kill": [
        "{target} crumbles to the ground, defeated!",
        "{target} lets out a final gasp and collapses!",
        "With a sickening thud, {target} falls lifeless!",
        "{target} shatters into pieces, vanquished!",
        "The light fades from {target}'s eyes. It is done.",
        "{target} dissolves into shadow and dust.",
    ],
    "dodge": [
        "{target} nimbly dodges {attacker}'s attack!",
        "{target} rolls aside, avoiding the blow entirely!",
        "{attacker} strikes empty air as {target} evades!",
        "{target} dances out of reach at the last second!",
    ],
    "block": [
        "{target} raises a shield, absorbing the impact!",
        "{target} deflects the blow with practiced ease!",
        "Steel rings on steel as {target} parries {attacker}'s strike!",
        "{target} braces and absorbs the force of the attack!",
    ],
    "heal": [
        "Warm light envelops {target}, mending wounds!",
        "Divine energy flows into {target}, restoring vitality!",
        "{target} feels strength return as healing magic takes hold!",
        "Glowing runes surround {target} as flesh knits back together!",
    ],
    "buff": [
        "Power surges through {target}'s body!",
        "{target} glows with newfound strength!",
        "A shimmering aura surrounds {target}!",
        "{target} feels invigorated and ready for battle!",
    ],
    "debuff": [
        "{target} feels their strength sapped away!",
        "A dark curse settles over {target}!",
        "{target} is weakened by dark magic!",
        "Shadows cling to {target}, draining their power!",
    ],
    "poison": [
        "Venom courses through {target}'s veins!",
        "{target} winces as poison burns through their blood!",
        "The toxin eats away at {target}'s health!",
    ],
    "burn": [
        "Flames lick at {target}'s body!",
        "{target} is scorched by searing fire!",
        "The burning intensifies, charring {target}!",
    ],
    "stun": [
        "{target} is stunned and cannot act!",
        "{target} staggers, dazed and disoriented!",
        "Stars fill {target}'s vision. They can't move!",
    ],
}

LEVEL_UP_MESSAGES = [
    "Power surges through your body! You have reached level {level}!",
    "Experience crystallizes into raw power! Level {level} achieved!",
    "You feel yourself growing stronger. Welcome to level {level}!",
    "The lessons of battle forge you anew. You are now level {level}!",
    "A burst of golden light! You have ascended to level {level}!",
    "Your skills sharpen, your resolve hardens. Level {level}!",
    "The crucible of combat has tempered you. Level {level} attained!",
    "With each victory, you grow. Level {level} is yours!",
]

DEATH_MESSAGES = [
    "Darkness closes in around you...",
    "Your vision fades as you collapse to the cold stone floor...",
    "The dungeon claims another soul...",
    "You fought bravely, but the darkness was stronger...",
    "Your journey ends here, in the depths below...",
    "The last thing you see is your weapon clattering to the ground...",
    "Pain gives way to numbness, and numbness to nothing...",
    "The torch gutters out. So does your flame...",
]

VICTORY_MESSAGES = [
    "The battle is won! You stand victorious!",
    "Your enemies lie defeated at your feet!",
    "Victory! The dungeon trembles before your might!",
    "The threat is vanquished. You may rest... for now.",
    "Triumph! Your blade drips with the blood of the fallen!",
    "The echoes of battle fade, replaced by the silence of victory.",
]

BOSS_INTRO_MESSAGES = {
    "Goblin King": [
        "A corpulent goblin sits atop a throne of garbage and gold.",
        "'You dare enter MY domain?' he squeals, rising with surprising speed.",
        "The Goblin King hefts his golden scepter like a war club!",
    ],
    "Spider Queen": [
        "The cavern opens into a vast chamber draped in webs.",
        "Eight enormous eyes gleam from the darkness above.",
        "The Spider Queen descends, venom dripping from mandibles as long as swords!",
    ],
    "Bone Dragon": [
        "The chamber is vast beyond measure, filled with mountains of bone.",
        "The bones begin to stir, assembling themselves with terrible purpose.",
        "An undead dragon rises from the ossuary, unholy fire blazing in its skull!",
    ],
    "Demon Lord": [
        "Reality tears apart as you enter the final chamber.",
        "Heat and darkness pour from the rift like a wound in the world.",
        "The Demon Lord steps through, his mere presence making the air scream!",
    ],
}

CHEST_MESSAGES = [
    "You discover a dusty chest half-buried in rubble!",
    "A treasure chest gleams in the torchlight!",
    "Hidden behind a loose stone, you find a locked chest!",
    "An ornate chest sits in the center of the room, suspiciously inviting...",
    "You spot a chest tucked into an alcove, its lock long rusted away.",
]

REST_MESSAGES = [
    "You find a sheltered corner and rest briefly, recovering your strength.",
    "Leaning against the wall, you catch your breath and tend to your wounds.",
    "A moment of peace in the darkness. You feel somewhat restored.",
    "You sit on a fallen pillar and rest. The silence is almost peaceful.",
]

SHOP_GREETING = [
    "'Welcome, adventurer! Browse my wares, if you've the coin.'",
    "'Ah, a customer! Come, come, I have just what you need.'",
    "'You look like you've been through hell. Lucky for you, I sell solutions.'",
    "'Step right up! Everything's for sale, and everything's a bargain!'",
    "'Brave soul! Let me outfit you for the dangers ahead.'",
]

FLOOR_TRANSITION = [
    "You descend deeper into the dungeon. The air grows colder.",
    "Stone steps lead you down to the next level. No turning back.",
    "The passage slopes downward. You are going deeper.",
    "A spiral staircase takes you further into the earth.",
    "You squeeze through a narrow gap into a new area of the dungeon.",
]


# ======================================================================
# INTRO CINEMATIC - shown after character creation
# ======================================================================

INTRO_CINEMATIC = [
    {
        "type": "text",
        "text": (
            "The iron gate slams shut behind you with a finality that echoes through your bones. "
            "Above, the last sliver of grey sky vanishes as the mechanism grinds home. "
            "You stand at the mouth of a stone throat that descends into absolute darkness. "
            "The Binding Consortium has spoken. You are the next to be sent down."
        ),
    },
    {
        "type": "text",
        "text": (
            "The stairway spirals downward, carved by hands long dead and forgotten. "
            "Torches gutter in iron sconces, their oil ancient and foul-smelling. "
            "Each step takes you further from the world you knew. "
            "Somewhere far below, something vast and patient stirs in its prison — "
            "the thing the Consortium calls The Unraveling."
        ),
    },
    {
        "type": "choice",
        "text": (
            "A guard stands at the final landing before the true descent begins. "
            "His face is hollow, eyes ringed with sleeplessness. He looks at you "
            "the way a gravedigger looks at the terminally ill."
        ),
        "choices": [
            {
                "label": "Ask about The Depths",
                "response": (
                    "'The Depths?' He laughs — a thin, brittle sound. "
                    "'Fifteen floors of everything that crawled out of the dark when the Binding cracked. "
                    "Goblins on top. Things without names at the bottom. "
                    "Every expedition sends fewer people back. Last one sent none.'"
                ),
                "flag": None,
            },
            {
                "label": "Demand to know why you were chosen",
                "response": (
                    "He looks at you with something between pity and contempt. "
                    "'Chosen? Nobody chooses this. The Consortium draws lots from the condemned, "
                    "the indebted, and the foolish. You must be one of the three. "
                    "Which one doesn't matter down here.'"
                ),
                "flag": None,
            },
            {
                "label": "Say nothing. Descend.",
                "response": (
                    "The guard watches you pass without a word. "
                    "For a moment, something like respect flickers across his ruined face. "
                    "'Quiet ones last longest,' he mutters to your back. "
                    "'The Depths don't care about bravery. Only stubbornness.'"
                ),
                "flag": "stoic_start",
            },
        ],
    },
    {
        "type": "text",
        "text": (
            "The stairway ends. You step through an archway of black stone into a corridor "
            "that smells of damp earth and old blood. The walls are scratched with hundreds "
            "of tally marks — previous delvers counting their days, or their kills, "
            "or the hours until madness took them. Most tallies end abruptly."
        ),
    },
    {
        "type": "choice",
        "text": (
            "At the base of the stairs, a crude shrine has been erected from broken weapons "
            "and shattered shields. A candle burns before it, still fresh. Someone was here recently. "
            "Scratched into the stone beneath the shrine: 'LEAVE SOMETHING BEHIND OR TAKE NOTHING FORWARD.'"
        ),
        "choices": [
            {
                "label": "Leave a coin at the shrine",
                "response": (
                    "You place a single coin among the offerings. The candle flickers, "
                    "and for an instant the corridor feels warmer — as if the stone itself "
                    "exhaled in gratitude. A good omen, perhaps. Or a trick of exhaustion."
                ),
                "flag": "shrine_offering",
            },
            {
                "label": "Take the candle — you need it more than the dead",
                "response": (
                    "You pluck the candle from the shrine. The flame doesn't waver. "
                    "But something in the air changes — a subtle wrongness, like a held breath. "
                    "Somewhere in the dark, something noticed."
                ),
                "flag": "shrine_desecrated",
            },
            {
                "label": "Ignore the shrine entirely",
                "response": (
                    "Superstition is a luxury for those with time. You walk past without slowing. "
                    "The candle gutters in your wake, but you don't look back."
                ),
                "flag": None,
            },
        ],
    },
    {
        "type": "text",
        "text": (
            "The corridor opens into a wider chamber — the first of many. "
            "Your torch illuminates rubble, old bones, and the faint outline of doors "
            "leading in three directions. The air tastes of copper and mildew. "
            "This is Floor One. The Upper Depths. Where the easy things live. "
            "If anything in this place can be called easy."
        ),
    },
    {
        "type": "text",
        "text": (
            "You grip your weapon. You check your supplies. You breathe. "
            "Somewhere far below, the Binding weakens and the Unraveling waits. "
            "Fifteen floors between you and the truth of what the Consortium buried here. "
            "The only way out is down."
        ),
    },
]


# ======================================================================
# FLOOR NARRATIVES - triggered on first visit to each floor tier
# ======================================================================

FLOOR_NARRATIVES = {
    1: {
        "pages": [
            {
                "type": "text",
                "text": (
                    "The Upper Depths. The walls here are still recognizably man-made — "
                    "quarried stone, iron brackets, the remnants of a supply route "
                    "that once fed the Binding Consortium's research teams. "
                    "Now the corridors belong to goblins, rats, and things that scuttle "
                    "just beyond the reach of your torchlight."
                ),
            },
            {
                "type": "text",
                "text": (
                    "Somewhere on this floor, previous delvers scratched a warning into the wall: "
                    "'THE GOBLIN KING HOARDS MORE THAN GOLD.' "
                    "You don't know what that means yet. You will."
                ),
            },
        ],
    },
    4: {
        "pages": [
            {
                "type": "text",
                "text": (
                    "The stone gives way to something organic. The walls pulse with a faint "
                    "bioluminescence — vast fungal networks that have colonized the rock itself. "
                    "The air is thick with spores that taste sweet on the tongue and burn in the lungs. "
                    "Welcome to the Fungal Caves. Nothing here is what it seems."
                ),
            },
            {
                "type": "text",
                "text": (
                    "Enormous mushroom stalks rise like pillars, their caps brushing a ceiling "
                    "you can no longer see. Webs stretch between them — not spider silk, "
                    "but mycelial threads as thick as rope. Things move within the fungal canopy. "
                    "Large things. Patient things."
                ),
            },
            {
                "type": "choice",
                "text": (
                    "A pool of luminous liquid blocks the passage ahead. "
                    "It smells of honey and ammonia. Tiny organisms drift within it, "
                    "pulsing with soft blue light. The liquid might be drinkable. "
                    "It might also dissolve your stomach lining."
                ),
                "choices": [
                    {
                        "label": "Drink from the pool",
                        "response": (
                            "The liquid burns going down, then blooms into warmth. "
                            "Your vision sharpens. Colors you've never seen before "
                            "bleed from the walls. For a few terrible seconds, "
                            "you can see the mycelial network stretching for miles in every direction — "
                            "and the vast intelligence that watches through it."
                        ),
                        "flag": "fungal_sight",
                    },
                    {
                        "label": "Wade through carefully",
                        "response": (
                            "You push through the pool, keeping your mouth shut and eyes forward. "
                            "The liquid clings to your legs like something alive, "
                            "reluctant to release you. When you emerge on the other side, "
                            "faint luminous handprints mark your skin. They'll fade. Probably."
                        ),
                        "flag": None,
                    },
                ],
            },
        ],
    },
    7: {
        "pages": [
            {
                "type": "text",
                "text": (
                    "The fungal growth recedes, replaced by something far worse. "
                    "Bones. Millions of them. The walls, floor, and ceiling are constructed "
                    "entirely from skeletal remains — fused together by some dark craft "
                    "into architecture that should not stand but does. "
                    "You have entered the Bone Warrens."
                ),
            },
            {
                "type": "text",
                "text": (
                    "Not all the bones are human. Some are too large, too strangely shaped, "
                    "belonging to creatures that have no name in any bestiary you've read. "
                    "Occasionally a skull turns to watch you pass, empty sockets tracking "
                    "your movement with malevolent attention. The dead here are not at rest. "
                    "They are waiting."
                ),
            },
            {
                "type": "choice",
                "text": (
                    "A skeleton sits propped against the wall, still wearing the tattered robes "
                    "of a Consortium researcher. A journal rests in its lap, "
                    "its pages miraculously intact. The skeleton's jaw hangs open "
                    "as if frozen mid-scream."
                ),
                "choices": [
                    {
                        "label": "Read the journal",
                        "response": (
                            "The final entry reads: 'The Bone Dragon is not a creature. "
                            "It is a memory — the Depths remembering what it was before "
                            "the Consortium carved it open. We didn't build a prison. "
                            "We built a wound. And wounds remember.' "
                            "You pocket the journal. This changes things."
                        ),
                        "flag": "bone_journal",
                    },
                    {
                        "label": "Leave it — the dead keep their secrets",
                        "response": (
                            "Some knowledge is a trap. You walk past the skeleton without touching it. "
                            "As you pass, you could swear its jaw closes slowly, "
                            "as if disappointed."
                        ),
                        "flag": None,
                    },
                ],
            },
        ],
    },
    10: {
        "pages": [
            {
                "type": "text",
                "text": (
                    "The bones end at the edge of a chasm that should not exist this far underground. "
                    "A rift splits the earth — not downward, but inward, as if reality itself "
                    "has been torn open. The air here tastes of ozone and despair. "
                    "Heat rises from the depths in waves that distort your vision. "
                    "This is the Abyssal Rift."
                ),
            },
            {
                "type": "text",
                "text": (
                    "Bridges of fused obsidian span the void, connecting chambers carved "
                    "into the rift walls. Below, something glows — not fire, not magma, "
                    "but a light that seems to come from nowhere and everywhere. "
                    "The Unraveling is close now. You can feel it in the way the air vibrates, "
                    "in the way your thoughts occasionally finish themselves before you think them."
                ),
            },
            {
                "type": "choice",
                "text": (
                    "At the edge of the rift, a stone obelisk bears an inscription in a language "
                    "that shifts and reforms as you read it. One moment it warns, "
                    "the next it invites. Your head aches with the contradiction."
                ),
                "choices": [
                    {
                        "label": "Focus and decipher the warning",
                        "response": (
                            "You force the shifting symbols into meaning through sheer will. "
                            "'THE BINDING IS A LIE. THE PRISON IS A CRADLE. "
                            "WHAT THEY SEALED WAS NOT EVIL — IT WAS UNFINISHED.' "
                            "The words sear themselves into your memory. "
                            "The obelisk cracks and goes dark."
                        ),
                        "flag": "obelisk_truth",
                    },
                    {
                        "label": "Smash the obelisk — nothing good speaks in riddles",
                        "response": (
                            "Your weapon strikes the stone and it shatters like glass. "
                            "A shockwave of silence expands outward — not sound, but the absence of it. "
                            "For three heartbeats, the rift stops glowing. "
                            "Then it resumes, brighter than before. Something noticed."
                        ),
                        "flag": "obelisk_destroyed",
                    },
                    {
                        "label": "Turn away — you came to fight, not to read",
                        "response": (
                            "You leave the obelisk behind. Its shifting text reflects off the obsidian "
                            "at your feet as you walk — following you, insistent, unread. "
                            "Some doors, once seen, cannot be fully ignored."
                        ),
                        "flag": None,
                    },
                ],
            },
        ],
    },
    13: {
        "pages": [
            {
                "type": "text",
                "text": (
                    "The rift narrows to a single corridor of fused crystal and blackened iron. "
                    "Every surface hums with contained energy. This is the Binding Chamber — "
                    "the deepest point of the Consortium's great work, where they chained "
                    "the Unraveling fifteen years ago. The chains are still here. "
                    "They are screaming."
                ),
            },
            {
                "type": "text",
                "text": (
                    "Massive iron links, each inscribed with thousands of containment glyphs, "
                    "stretch from wall to wall in patterns that hurt to follow with your eyes. "
                    "Some links have shattered. Others glow white-hot, bearing the strain "
                    "of holding what remains. The air itself bleeds — thin red lines "
                    "appearing and vanishing like wounds in the fabric of the world."
                ),
            },
            {
                "type": "text",
                "text": (
                    "And beneath it all, a voice. Not heard — felt. "
                    "A pressure behind your eyes, a thought that is not yours: "
                    "'You are the last. You are the only. Will you finish what they started, "
                    "or will you understand what they could not?' "
                    "The Demon Lord guards the final seal. Beyond that, the choice is yours."
                ),
            },
        ],
    },
}


# ======================================================================
# BOSS LORE - extended encounter text
# ======================================================================

BOSS_ENCOUNTER_TEXT = {
    "Goblin King": {
        "intro_pages": [
            {
                "type": "text",
                "text": (
                    "The tunnel widens into a grotesque throne room. Stolen tapestries hang from "
                    "the walls, stained and torn. Piles of looted goods — coins, weapons, armor, "
                    "bones of previous delvers — form crude ramparts. Goblin sentries watch from "
                    "elevated perches, their yellow eyes tracking your every step."
                ),
            },
            {
                "type": "text",
                "text": (
                    "At the chamber's heart, the Goblin King sits upon a throne welded together "
                    "from a hundred stolen swords. He is grotesquely fat, his green skin stretched "
                    "tight over rolls of muscle and excess. A crown of bent iron sits askew on his "
                    "massive skull. He grins, revealing filed teeth, and rises with the fluid grace "
                    "of something far more dangerous than he appears."
                ),
            },
        ],
        "mid_fight_dialogue": [
            "'You think you're the first? I've eaten HEROES, little thing!'",
            "'My kingdom! MY kingdom! I'll wear your ribs as a necklace!'",
            "'The deeper things promised me this floor! It's MINE by right of TEETH!'",
        ],
        "epilogue_pages": [
            {
                "type": "text",
                "text": (
                    "The Goblin King crashes to the floor, his stolen crown rolling away into the filth. "
                    "His court scatters — goblins fleeing into cracks and tunnels, "
                    "their loyalty evaporating with their king's blood. "
                    "The throne room is yours, if you want it. You don't."
                ),
            },
            {
                "type": "choice",
                "text": (
                    "The Goblin King lies broken at your feet, wheezing through shattered teeth. "
                    "One hand reaches toward his fallen crown. 'Mercy,' he gurgles. "
                    "'I can tell you... what's below. What they're afraid of. "
                    "I've heard them whispering through the stone...'"
                ),
                "choices": [
                    {
                        "label": "End him.",
                        "response": (
                            "Your weapon falls one final time. The Goblin King shudders and goes still. "
                            "Whatever secrets he carried die with him. "
                            "The goblins watching from the shadows shriek and scatter. "
                            "You feel nothing. This is what the Depths require."
                        ),
                        "flag": None,
                    },
                    {
                        "label": "Show mercy. Hear what he knows.",
                        "response": (
                            "'The Spider... she knows the old paths,' he wheezes. "
                            "'And the Bone Dragon... it remembers what this place was BEFORE. "
                            "Before the Consortium. Before the chains. Something older. "
                            "Something that wants to be whole again.' "
                            "He crawls away into the dark, leaving a trail of black blood. "
                            "You let him go."
                        ),
                        "flag": "mercy_goblin_king",
                    },
                ],
            },
        ],
    },
    "Spider Queen": {
        "intro_pages": [
            {
                "type": "text",
                "text": (
                    "The passage opens into a cathedral of silk. Webs stretch from floor to ceiling "
                    "in geometric patterns too precise for instinct alone — this is architecture, "
                    "deliberate and alien. Cocooned shapes hang at intervals, some still twitching. "
                    "The light from your torch refracts through the silk, casting prismatic shadows."
                ),
            },
            {
                "type": "text",
                "text": (
                    "She descends from above without sound — a nightmare of chitin and silk, "
                    "eight legs spanning the width of the chamber. Her eyes — all eight of them — "
                    "hold an intelligence that no beast should possess. She was not always this. "
                    "The Consortium's records speak of a researcher named Thessaly, "
                    "who ventured into the Fungal Caves and never returned as herself. "
                    "The Spider Queen tilts her massive head and makes a sound like laughter."
                ),
            },
        ],
        "mid_fight_dialogue": [
            "'I was human once. I remember hands. I remember... warmth. Do you know what the spores showed me?'",
            "'The web connects everything — every floor, every creature, every secret. I SEE it all!'",
            "'You fight what you do not understand. The Unraveling is not a monster. It is an ANSWER.'",
        ],
        "epilogue_pages": [
            {
                "type": "text",
                "text": (
                    "The Spider Queen crumples, her massive legs folding beneath her like a dying flower. "
                    "As the light fades from her eight eyes, something shifts in her face — "
                    "for a moment, behind the chitin and the mandibles, you see something almost human. "
                    "Almost sorrowful."
                ),
            },
            {
                "type": "choice",
                "text": (
                    "She lies still, her vast body slowly deflating. But her spinnerets twitch, "
                    "and from them, a final thread of silk emerges — not a weapon, "
                    "but a pattern. A map. The layout of the floors below, woven in silver. "
                    "Her last gift, or her last trap."
                ),
                "choices": [
                    {
                        "label": "End her. Destroy the map.",
                        "response": (
                            "You drive your weapon through the silk and into what remains of Thessaly. "
                            "The map-web tears and dissolves. Whatever she knew dies here. "
                            "The webs throughout the chamber begin to unravel, "
                            "and the Fungal Caves feel suddenly, terribly empty."
                        ),
                        "flag": None,
                    },
                    {
                        "label": "Take the silk map. Let her rest.",
                        "response": (
                            "You carefully gather the woven map. It is warm to the touch "
                            "and hums faintly, as if alive. The Spider Queen's eyes dim, "
                            "and the last sound she makes is almost a word — 'Thessaly.' "
                            "Her own name, remembered at the end."
                        ),
                        "flag": "mercy_spider_queen",
                    },
                ],
            },
        ],
    },
    "Bone Dragon": {
        "intro_pages": [
            {
                "type": "text",
                "text": (
                    "The ossuary opens into a cavern so vast your torchlight cannot find its walls. "
                    "The floor is a sea of bones — millions of them, shifting and clicking "
                    "like a living carpet. The air vibrates with a subsonic hum that makes your "
                    "teeth ache and your vision swim."
                ),
            },
            {
                "type": "text",
                "text": (
                    "It assembles itself from the bone-sea with terrible deliberation. "
                    "Femurs lock into place as ribs. Skulls of a dozen species fuse into "
                    "a single draconic head. Wings of fused vertebrae spread wide, "
                    "blotting out what little light exists. Unholy fire — not orange but "
                    "a deep, grieving violet — blooms in the hollow of its chest. "
                    "The Bone Dragon is not a creature. It is a memory of what the Depths lost."
                ),
            },
        ],
        "mid_fight_dialogue": [
            "'I am the shape of what was buried. I am the Depths remembering itself.'",
            "'The Consortium broke this place open like an egg. I am the scar tissue.'",
            "'Every bone that falls, I rebuild. Every delver who dies here becomes part of me. You will too.'",
        ],
        "epilogue_pages": [
            {
                "type": "text",
                "text": (
                    "The Bone Dragon collapses — not shattering, but gently disassembling. "
                    "Each bone settles back into the floor with care, as if being laid to rest "
                    "by invisible hands. The violet fire in its chest gutters "
                    "and reduces to a single flickering ember hovering in the air."
                ),
            },
            {
                "type": "choice",
                "text": (
                    "The ember floats before you, pulsing slowly like a heartbeat. "
                    "It radiates warmth and an immense sadness — the grief of a place "
                    "that was hollowed out and filled with suffering. "
                    "It drifts toward your hand, waiting."
                ),
                "choices": [
                    {
                        "label": "Crush the ember. End the memory.",
                        "response": (
                            "You close your fist around the ember and squeeze. "
                            "It resists for a moment — a flash of violet, a whisper of sorrow — "
                            "then it dies. The bones around you go still, truly still, "
                            "for the first time in centuries. The Warrens are just bones now. "
                            "Nothing more."
                        ),
                        "flag": None,
                    },
                    {
                        "label": "Accept the ember. Carry the memory forward.",
                        "response": (
                            "The ember sinks into your palm and settles somewhere behind your sternum. "
                            "You gasp as a flood of images washes over you — the Depths before the Consortium, "
                            "before the Binding, when this place was something else entirely. "
                            "Not a dungeon. A sanctuary. The memory burns, but it illuminates."
                        ),
                        "flag": "mercy_bone_dragon",
                    },
                ],
            },
        ],
    },
    "Demon Lord": {
        "intro_pages": [
            {
                "type": "text",
                "text": (
                    "The final seal groans under impossible pressure. The containment glyphs carved "
                    "into every surface flare and die in sequence, a cascade of failing magic. "
                    "Beyond the seal, the air itself is wrong — not dark, not light, "
                    "but something your eyes refuse to categorize. Reality here is thin, "
                    "worn through by fifteen years of strain."
                ),
            },
            {
                "type": "text",
                "text": (
                    "The Demon Lord stands at the heart of the Binding Chamber, "
                    "not as a conqueror but as a guardian. Its form shifts constantly — "
                    "now towering and horned, now a roiling mass of shadow and light, "
                    "now almost human. It is the Unraveling's final defense, "
                    "or perhaps its warden. Even it does not seem certain which."
                ),
            },
            {
                "type": "text",
                "text": (
                    "'You have come far, mortal,' it speaks in a voice that is every voice — "
                    "the Goblin King's snarl, the Spider Queen's whisper, the Bone Dragon's grief. "
                    "'Far enough to earn the truth, or far enough to die ignorant. "
                    "The choice was always yours. It was always the only thing that was.'"
                ),
            },
        ],
        "mid_fight_dialogue": [
            "'Do you understand yet? I am not the enemy. I am the LOCK.'",
            "'Break me, and the Unraveling is free. Spare me, and nothing changes. Choose WISELY.'",
            "'Every blow you strike echoes through the Binding. Can you not HEAR it screaming?'",
        ],
        "epilogue_pages": [
            {
                "type": "text",
                "text": (
                    "The Demon Lord falls to one knee, its shifting form stabilizing for the first time. "
                    "Behind it, the final seal pulses — cracked but holding, a hairline fracture "
                    "between the world and whatever lies beyond. "
                    "The chamber is silent except for the sound of chains still singing under tension."
                ),
            },
            {
                "type": "text",
                "text": (
                    "Three paths lie before you. The Binding can be restored — seal the Unraveling "
                    "for another generation and walk away. The seal can be studied — "
                    "if you have gathered enough truth, you may understand what the Consortium "
                    "truly imprisoned here. Or the seal can be broken — and whatever the Unraveling is, "
                    "it will be free. The Demon Lord watches you with ancient, exhausted eyes, "
                    "and waits for the only thing that matters: your choice."
                ),
            },
        ],
    },
}


# ======================================================================
# LORE COLLECTIBLE DISCOVERY TEXT - shown when picking up lore items
# ======================================================================

LORE_DISCOVERY_MESSAGES = [
    "You find a crumbling parchment wedged between the stones...",
    "A journal lies open on a dusty shelf, its pages yellowed with age...",
    "Strange symbols glow faintly on the wall. As you touch them, knowledge floods your mind...",
    "A dying explorer's final message is carved into the floor...",
    "An ancient stone tablet bears inscriptions in a language you shouldn't understand... but do.",
    "A vial of preserved ink and a scrap of vellum, the handwriting frantic and uneven...",
    "Scratched into the back of a broken shield: a confession no one was meant to read...",
    "A crystal embedded in the wall hums when you approach. Images flash behind your eyes...",
    "Folded into the lining of a dead delver's boot — a letter never sent...",
    "The wall here is smooth and carved with deliberate precision. Someone took days to write this...",
]


# ======================================================================
# NPC LORE DIALOGUE - keyed by floor tier
# ======================================================================

NPC_LORE_DIALOGUE = {
    "upper_depths": {
        "merchant": [
            "'Fresh meat, eh? Don't take it personal — everyone's fresh meat on floor one. "
            "I've been running this post for six months. Longest anyone's managed.'",
            "'The Consortium sends supplies down once a month. Or they used to. "
            "Last shipment was two months late. I supplement with what the goblins drop.'",
            "'Buy something or move along. Every second you stand here gawking "
            "is a second something's creeping closer.'",
            "'Word of advice, free of charge: the goblins aren't the problem down here. "
            "They're what the REAL problems don't bother eating.'",
            "'I don't ask where the gold comes from, you don't ask where the goods come from. "
            "That's the only honest trade in the Depths.'",
        ],
        "quest_giver": [
            "'The Consortium pays bounties for cleared rooms. Don't ask me why — "
            "I just pass along the orders and collect my cut.'",
            "'There's a nest of something foul three chambers east. "
            "Clear it out and I'll make it worth your while.'",
            "'Every goblin you kill is one fewer to swarm the trade route. "
            "I call that a public service. The Consortium calls it a contract.'",
            "'Bring me proof of kills. Ears, teeth, whatever. "
            "I don't need trophies, just confirmation.'",
        ],
        "healer": [
            "'Hold still. This will sting, but infection down here kills more than monsters do.'",
            "'I trained as a field surgeon topside. Got sent down here as punishment. "
            "Funny — I've saved more lives in the Depths than I ever did above.'",
            "'The wounds I see... they're getting stranger. Bite marks from things "
            "I can't identify. Burns from fires that leave no ash.'",
            "'Rest when you can. The Depths have a way of wearing you down — "
            "not all at once, but steadily, like water on stone.'",
        ],
    },
    "fungal_caves": {
        "merchant": [
            "'Welcome to my little corner of the mycelium. Mind the spores — "
            "the blue ones make you see things, the red ones stop your heart.'",
            "'I used to sell torches. Down here they attract the wrong kind of attention. "
            "Now I sell bioluminescent fungi. Dimmer, but you live longer.'",
            "'The caves change. Passages close, new ones open. I move my stall "
            "every three days just to stay on a trade route that still exists.'",
            "'Something in these caves is intelligent. Not the spiders — something IN the fungus. "
            "I've seen the mycelium rearrange itself around sleeping delvers. Gently, almost.'",
        ],
        "quest_giver": [
            "'The spider nests are spreading. Cut them back or we'll be overrun within the week.'",
            "'There's a Consortium research cache sealed behind a fungal wall three chambers north. "
            "The supplies inside could keep us alive for a month. Interested?'",
            "'I need venom sacs. Don't look at me like that — diluted spider venom "
            "is the only thing that cuts through the fungal infections.'",
        ],
        "healer": [
            "'The spore sickness is getting worse. I've lost four people this week — "
            "not to monsters, just to breathing the air.'",
            "'I've started using the fungus itself as medicine. Ironic, isn't it? "
            "The thing that's killing us is also the only cure.'",
            "'Your lungs sound like a bellows full of mud. Let me help, "
            "or you won't make it three more chambers.'",
            "'I see things now. In the dark, when the spores are thick. "
            "I see the caves as they were before all this. They were beautiful.'",
        ],
    },
    "bone_warrens": {
        "merchant": [
            "'Keep your voice down. The bones LISTEN. I'm not being dramatic — "
            "I've watched them rearrange around loud noises.'",
            "'My prices are higher here. Supply chains don't reach this deep. "
            "Everything I sell, I scavenged from the dead. No offense to the dead.'",
            "'I should have turned back at the Fungal Caves. But the money's better here. "
            "And there's something about this place that makes leaving feel... wrong.'",
        ],
        "quest_giver": [
            "'The undead don't stay dead down here. Whatever you kill, burn the remains. "
            "Or they get back up stronger. I'll pay extra for confirmed burns.'",
            "'There's a necromancer somewhere on this floor. Not human — something that was here "
            "before the Consortium. Find it, kill it, and maybe the dead will stay put.'",
            "'I need someone to scout the path to Floor 10. The last three scouts didn't come back. "
            "I'd go myself, but I'm not brave. I'm a coward who pays brave people.'",
        ],
        "healer": [
            "'I've stopped sleeping. Every time I close my eyes, I hear them — "
            "voices in the bones, speaking in languages that predate the Consortium.'",
            "'The wounds here don't heal right. Flesh knits, but it knits WRONG. "
            "I've seen scars move. I've seen healed skin open again for no reason.'",
            "'Let me look at you. ...You're still alive in there, yes? "
            "Good. Good. I have to check. Some of them walk and talk but they're not... "
            "they're not in there anymore.'",
        ],
    },
    "abyssal_rift": {
        "merchant": [
            "'I'm the last merchant. No one sells below me. No one CAN — "
            "the rift does things to goods. Metal corrodes, food rots, potions curdle. "
            "What I've got is treated with Consortium wards. It'll hold. Probably.'",
            "'Don't look down. I know the rift is fascinating, but don't. Look. Down. "
            "The things you see in there aren't real. Unless they are. I can't tell anymore.'",
            "'Prices? You want to haggle HERE? Fine. Everything costs everything. "
            "How much have you got? That's what it costs.'",
        ],
        "quest_giver": [
            "'The bridges are failing. Something is eating the obsidian from below. "
            "I need someone to reinforce the main crossing before we're all cut off.'",
            "'There are Consortium machines still running down here — containment pylons. "
            "Most are failing. Find the ones that still work and activate them. "
            "It might buy us time.'",
        ],
        "healer": [
            "'I don't sleep. I don't eat. I still heal. I don't know what that means. "
            "Don't ask me what that means.'",
            "'The rift changes you. Not fast — slow, like erosion. "
            "I've been here too long. My hands are translucent now. "
            "I can still heal. But for how long?'",
            "'Come here. Let me fix what I can. I'm sorry about the rest — "
            "some of what the rift does, I can't undo. No one can.'",
        ],
    },
    "binding_chamber": {
        "merchant": [
            "'No one should be selling anything this deep. No one should BE this deep. "
            "But you need supplies and I need to believe this means something. So. What'll it be.'",
            "'I was part of the original Consortium expedition. Fifteen years ago. "
            "I'm the only one left. Not because I'm strong. Because I'm too afraid to go deeper "
            "and too afraid to go back.'",
        ],
        "quest_giver": [
            "'There's nothing left to quest for. There's only the seal and what's behind it. "
            "Everything else was distraction. Everything else was delay.'",
            "'If you've made it this far, you don't need me to tell you what to do. "
            "But I'll say it anyway: be certain. Whatever you choose at the seal, be CERTAIN. "
            "There are no second chances at the bottom of the world.'",
        ],
        "healer": [
            "'I can patch your body. I cannot patch what the Binding Chamber does to your mind. "
            "The voice you're hearing — yes, I know about the voice — it isn't lying. "
            "That's the worst part.'",
            "'This is the last time I can help you. Beyond this point, healing magic "
            "doesn't work right. The seal interferes. You'll be on your own.'",
            "'You're the last one. Did you know that? The last delver. "
            "If you don't end this — the Binding, the Unraveling, all of it — "
            "no one will. The Consortium has given up. This is it.'",
        ],
    },
}


# ======================================================================
# ENDING NARRATIVES - based on ending type from NarrativeManager
# ======================================================================

ENDING_NARRATIVES = {
    "binding_restored": {
        "title": "The Binding Restored",
        "pages": [
            {
                "type": "text",
                "text": (
                    "You pour everything you have into the seal. Your blood, your strength, "
                    "the last reserves of will that carried you through fifteen floors of horror. "
                    "The containment glyphs flare back to life — white-hot, blinding — "
                    "and the cracks in the Binding close with a sound like a thunderclap in reverse."
                ),
            },
            {
                "type": "text",
                "text": (
                    "The Unraveling screams. Not in anger — in despair. Whatever it is, "
                    "whatever it wanted to become, you have denied it for another generation. "
                    "The chains hold. The seal endures. The Consortium's work continues, "
                    "built on foundations you now know are lies."
                ),
            },
            {
                "type": "text",
                "text": (
                    "You climb the fifteen floors alone. Nothing attacks you — the creatures "
                    "of the Depths shrink from your path as if repelled by what you carry. "
                    "When you emerge into daylight for the first time in weeks, "
                    "the Consortium is waiting. They call you a hero. They give you gold "
                    "and a pardon and a title. They do not give you answers."
                ),
            },
            {
                "type": "text",
                "text": (
                    "At night, you still hear it. Faint, far below, patient as stone: "
                    "the Unraveling, waiting. The Binding holds, but it will crack again. "
                    "It always does. And when it does, someone else will descend. "
                    "Someone else will choose. You saved the world, after a fashion. "
                    "Whether it was worth saving this way, you will never be certain."
                ),
            },
        ],
    },
    "truth_seeker": {
        "title": "The Truth Seeker",
        "pages": [
            {
                "type": "text",
                "text": (
                    "The lore you gathered — the journal, the obelisk, the Bone Dragon's memory, "
                    "the whispered secrets of every boss who begged for mercy — it all coalesces "
                    "in this moment. You understand now what the Consortium buried. "
                    "The Unraveling is not a demon. It is not a curse. "
                    "It is the Depths themselves trying to heal."
                ),
            },
            {
                "type": "text",
                "text": (
                    "The Consortium mined too deep and too greedily, tearing open a wound "
                    "in the world's foundation. The Unraveling is scar tissue — "
                    "a natural process of restoration that the Consortium, in their arrogance, "
                    "mistook for a threat and chained. Every creature in the Depths, "
                    "every horror you fought, was a symptom of the infection "
                    "caused by the Binding itself."
                ),
            },
            {
                "type": "text",
                "text": (
                    "You do not restore the seal. You do not break it. "
                    "You rewrite it — using the knowledge you gathered, the patterns you learned, "
                    "the truth the Consortium tried to bury. The new seal does not imprison. "
                    "It guides. It allows the Depths to heal on their own terms, slowly, "
                    "over centuries, without the violent unraveling the old seal prevented."
                ),
            },
            {
                "type": "text",
                "text": (
                    "When you emerge, the Consortium does not call you a hero. "
                    "They call you a traitor. But the earthquakes stop. "
                    "The creatures of the Depths begin to recede. "
                    "The wound in the world, for the first time in fifteen years, "
                    "begins to close. You may never be forgiven for what you did. "
                    "But you will be right. And in the end, that matters more."
                ),
            },
        ],
    },
    "liberator": {
        "title": "The Liberator",
        "pages": [
            {
                "type": "text",
                "text": (
                    "You break the seal. It is easier than it should be — a single strike "
                    "at the weakest chain, and the whole edifice of containment shatters "
                    "like a house of cards. Fifteen years of Consortium engineering, "
                    "undone in a heartbeat."
                ),
            },
            {
                "type": "text",
                "text": (
                    "The Unraveling pours through the breach like water through a broken dam. "
                    "It is not what you expected. It is not monstrous, not demonic — "
                    "it is raw, undifferentiated potential. Creation and destruction "
                    "woven together in a force that remakes everything it touches."
                ),
            },
            {
                "type": "text",
                "text": (
                    "The Depths transform. Stone becomes crystal becomes wood becomes stone again. "
                    "The dead rise, but not as undead — as something new, neither alive nor dead. "
                    "The goblins sing. The spiders weave impossible geometries. "
                    "The bones dance. It is beautiful. It is terrifying. "
                    "It is utterly, irrevocably beyond your control."
                ),
            },
            {
                "type": "text",
                "text": (
                    "You emerge into a world that is changing. The sky ripples. "
                    "The earth breathes. The Consortium's tower is already crumbling, "
                    "consumed by growth that is neither plant nor mineral. "
                    "You freed something ancient and vast and indifferent to human concerns. "
                    "Whether this is salvation or apocalypse depends entirely on your definition. "
                    "The Unraveling does not care about definitions. It simply IS."
                ),
            },
        ],
    },
    "hollow_victory": {
        "title": "The Hollow Victory",
        "pages": [
            {
                "type": "text",
                "text": (
                    "You defeat the Demon Lord, but the victory tastes like ash. "
                    "You are too weak, too uninformed, too broken by the descent "
                    "to understand the choice before you. The seal, the Unraveling, "
                    "the Consortium's lies — they blur together into noise."
                ),
            },
            {
                "type": "text",
                "text": (
                    "You leave the Binding Chamber without choosing. "
                    "The seal holds — barely, temporarily — and you climb back toward daylight "
                    "with empty hands and a head full of questions you will never answer. "
                    "The Depths remain. The Unraveling remains. Nothing is resolved."
                ),
            },
            {
                "type": "text",
                "text": (
                    "The Consortium takes your report and files it away. "
                    "Another inconclusive expedition. Another delver returned with nothing to show "
                    "but scars and nightmares. They will send another. And another after that. "
                    "The cycle continues. The Binding frays. The world inches toward a reckoning "
                    "that you could not prevent and cannot forget."
                ),
            },
            {
                "type": "text",
                "text": (
                    "Sometimes, in the small hours of the night, you think about going back. "
                    "About descending again, stronger this time, wiser, ready to make the choice "
                    "you couldn't make before. But the iron gate is closed to you now. "
                    "The Consortium does not send the same delver twice. "
                    "You had your chance. The Depths remember."
                ),
            },
        ],
    },
}


# ======================================================================
# CYOA RANDOM EVENTS - triggered during exploration
# ======================================================================

EXPLORATION_EVENTS = [
    {
        "trigger_floors": (1, 5),
        "chance": 0.05,
        "pages": [
            {
                "type": "text",
                "text": (
                    "You stumble into a small alcove where a dying adventurer "
                    "leans against the wall, clutching a blood-soaked satchel. "
                    "'Take it,' they rasp. 'It won't save me. Might save you.'"
                ),
            },
            {
                "type": "choice",
                "text": (
                    "The adventurer's eyes are glassy. They don't have long. "
                    "The satchel is heavy — could be supplies, could be cursed relics. "
                    "Their other hand rests on a shortsword that still looks serviceable."
                ),
                "choices": [
                    {
                        "label": "Take the satchel and offer comfort",
                        "response": (
                            "You ease the satchel from their grip and sit with them. "
                            "They whisper a name — someone topside, someone waiting — "
                            "and then they are gone. Inside the satchel: dried meat, "
                            "a healing salve, and a letter you'll carry to the surface. If you make it."
                        ),
                        "effect": {"type": "heal", "value": 25},
                    },
                    {
                        "label": "Take everything — they won't need it",
                        "response": (
                            "You take the satchel and the sword and the boots and the belt pouch. "
                            "The adventurer watches you strip them with dying eyes "
                            "but says nothing. There's gold in the pouch. "
                            "You tell yourself they'd have done the same."
                        ),
                        "effect": {"type": "gold", "value": 30},
                    },
                    {
                        "label": "Use your supplies to try saving them",
                        "response": (
                            "You burn through your own healing supplies trying to stabilize them. "
                            "It's not enough. The wounds are too deep, the blood loss too great. "
                            "They die anyway, and now you're lighter on supplies. "
                            "But their last expression was gratitude, not abandonment. "
                            "That has to count for something."
                        ),
                        "effect": {"type": "damage", "value": 10},
                    },
                ],
            },
        ],
    },
    {
        "trigger_floors": (1, 4),
        "chance": 0.04,
        "pages": [
            {
                "type": "text",
                "text": (
                    "A section of wall has collapsed, revealing a hidden room. "
                    "Inside, a Consortium supply cache — crates stamped with official seals, "
                    "most of them smashed and looted. But one remains intact."
                ),
            },
            {
                "type": "choice",
                "text": "The sealed crate hums faintly. Something inside is still active.",
                "choices": [
                    {
                        "label": "Open it carefully",
                        "response": (
                            "Inside: three vials of military-grade healing tonic, "
                            "still glowing faintly. Consortium surplus. "
                            "You pocket them with quiet gratitude."
                        ),
                        "effect": {"type": "heal", "value": 30},
                    },
                    {
                        "label": "Smash it open quickly",
                        "response": (
                            "The crate shatters and one of the vials inside ruptures, "
                            "spraying alchemical fluid across your hands. It burns. "
                            "You salvage what you can — some coins "
                            "and a single intact healing vial."
                        ),
                        "effect": {"type": "damage", "value": 8},
                    },
                ],
            },
        ],
    },
    {
        "trigger_floors": (2, 6),
        "chance": 0.04,
        "pages": [
            {
                "type": "text",
                "text": (
                    "A goblin sits alone by a sputtering fire, separated from its pack. "
                    "It sees you and freezes. It's small — younger than the others, "
                    "barely armed. It makes no move to attack."
                ),
            },
            {
                "type": "choice",
                "text": (
                    "The goblin raises its hands, palms out. "
                    "A universal gesture, even in the Depths."
                ),
                "choices": [
                    {
                        "label": "Kill it — a goblin is a goblin",
                        "response": (
                            "It's over quickly. The goblin barely resists. "
                            "You find a few coins in its threadbare pouch "
                            "and a crudely drawn map of the next two chambers. Useful."
                        ),
                        "effect": {"type": "gold", "value": 15},
                    },
                    {
                        "label": "Leave it alone and move on",
                        "response": (
                            "You lower your weapon and step around the goblin's fire. "
                            "It watches you go with wide, disbelieving eyes. "
                            "Three chambers later, you find a small bundle of mushrooms "
                            "left in the middle of the corridor. Edible ones. A thank-you, perhaps."
                        ),
                        "effect": {"type": "heal", "value": 15},
                    },
                    {
                        "label": "Try to communicate",
                        "response": (
                            "You crouch by the fire and make slow, non-threatening gestures. "
                            "The goblin studies you for a long moment, then reaches into a crack "
                            "in the wall and produces a tarnished silver locket. "
                            "Inside: a faded portrait of a human woman. "
                            "It pushes the locket toward you and points deeper into the dungeon. "
                            "A message to deliver? A memory to carry? You take it."
                        ),
                        "effect": {"type": "xp", "value": 15},
                    },
                ],
            },
        ],
    },
    {
        "trigger_floors": (3, 7),
        "chance": 0.05,
        "pages": [
            {
                "type": "text",
                "text": (
                    "The corridor opens into a natural spring — clear water bubbling up "
                    "from a crack in the bedrock, pooling in a stone basin "
                    "that someone carved long before the Consortium arrived. "
                    "Runes circle the basin's edge, faintly glowing."
                ),
            },
            {
                "type": "choice",
                "text": (
                    "The water looks clean. Impossibly clean for this deep underground. "
                    "The runes pulse in a slow rhythm, like breathing."
                ),
                "choices": [
                    {
                        "label": "Drink deeply",
                        "response": (
                            "The water is cold and sweet and tastes of starlight — "
                            "of something you'd forgotten existed this far from the sky. "
                            "Strength flows back into your limbs. Wounds close. "
                            "For a brief, shining moment, you remember what hope feels like."
                        ),
                        "effect": {"type": "heal", "value": 40},
                    },
                    {
                        "label": "Fill your waterskin but don't drink",
                        "response": (
                            "You fill your waterskin from the spring. "
                            "The water glows faintly through the leather — "
                            "you'll find a use for it later. "
                            "The runes dim slightly as you take from the basin."
                        ),
                        "effect": {"type": "gold", "value": 20},
                    },
                    {
                        "label": "Study the runes instead",
                        "response": (
                            "The runes are old — far older than the Consortium, "
                            "older than the kingdom above. They describe a ritual of cleansing, "
                            "meant to purify corruption from the earth itself. "
                            "Whoever carved this basin knew the Depths were sick "
                            "long before the Binding was conceived. "
                            "The knowledge settles into your mind like a stone into deep water."
                        ),
                        "effect": {"type": "xp", "value": 25},
                    },
                ],
            },
        ],
    },
    {
        "trigger_floors": (5, 9),
        "chance": 0.05,
        "pages": [
            {
                "type": "text",
                "text": (
                    "A ghost. There is no other word for it. A translucent figure "
                    "stands in the center of the chamber, repeating the same motions — "
                    "walking to a wall, placing something invisible, turning, walking back. "
                    "A loop. An echo. It does not seem to notice you."
                ),
            },
            {
                "type": "choice",
                "text": (
                    "The ghost wears Consortium robes. This was a researcher, once. "
                    "Their loop is methodical — they were working when they died, "
                    "and death did not stop the work."
                ),
                "choices": [
                    {
                        "label": "Disrupt the loop — break the cycle",
                        "response": (
                            "You step into the ghost's path. It stops. Looks at you. "
                            "For one terrible moment, recognition flares in its hollow eyes. "
                            "'The... the readings... they're wrong...' it whispers. "
                            "Then it dissolves, and where it stood, a small crystal falls to the floor — "
                            "a data core, still containing the researcher's final findings."
                        ),
                        "effect": {"type": "lore", "value": 1},
                    },
                    {
                        "label": "Watch and learn the pattern",
                        "response": (
                            "You observe the ghost's movements for several minutes. "
                            "The pattern resolves into meaning — it's checking containment seals, "
                            "following a maintenance route. The sequence reveals "
                            "the location of a sealed supply room two floors down. "
                            "Knowledge the ghost no longer needs."
                        ),
                        "effect": {"type": "xp", "value": 20},
                    },
                    {
                        "label": "Leave it alone — the dead deserve their rituals",
                        "response": (
                            "You skirt the edge of the chamber and leave the ghost to its work. "
                            "As you pass, its hand brushes your arm — accident or intention, "
                            "you cannot tell. Where it touched, your skin tingles with warmth. "
                            "A benediction from the dead."
                        ),
                        "effect": {"type": "heal", "value": 15},
                    },
                ],
            },
        ],
    },
    {
        "trigger_floors": (4, 8),
        "chance": 0.04,
        "pages": [
            {
                "type": "text",
                "text": (
                    "A trap. You see it too late — the floor gives way beneath your leading foot, "
                    "revealing a pit lined with rusted spikes. You catch yourself on the edge, "
                    "hanging by your fingertips over the drop."
                ),
            },
            {
                "type": "choice",
                "text": (
                    "Your arms burn. The edge is crumbling. Below, the spikes "
                    "are stained with old blood. You have seconds."
                ),
                "choices": [
                    {
                        "label": "Pull yourself up with brute strength",
                        "response": (
                            "Every muscle screams as you haul yourself back over the lip. "
                            "You roll away from the edge, panting, and lie on the cold stone "
                            "staring at the ceiling. Your arms are torn and bleeding from the effort, "
                            "but you're alive. You're alive."
                        ),
                        "effect": {"type": "damage", "value": 15},
                    },
                    {
                        "label": "Swing to the far ledge",
                        "response": (
                            "You build momentum and launch yourself across the gap. "
                            "For a sickening moment you're in freefall — then your hands "
                            "find purchase on the far side. You scramble up and look back. "
                            "The pit is wider than you thought. On the far ledge: "
                            "a skeleton that didn't make the jump. Its pouch holds gold."
                        ),
                        "effect": {"type": "gold", "value": 25},
                    },
                ],
            },
        ],
    },
    {
        "trigger_floors": (6, 10),
        "chance": 0.04,
        "pages": [
            {
                "type": "text",
                "text": (
                    "The chamber is filled with mushrooms that glow in shifting colors — "
                    "azure, violet, sickly green. The air is heavy with spores, "
                    "and the patterns of light seem almost deliberate, almost meaningful. "
                    "You feel lightheaded."
                ),
            },
            {
                "type": "choice",
                "text": (
                    "The spores are thickening. Your vision swims. "
                    "The mushroom patterns are resolving into something — "
                    "a message, a warning, an invitation."
                ),
                "choices": [
                    {
                        "label": "Breathe deep and let the vision come",
                        "response": (
                            "The world dissolves. You see the Depths from above — "
                            "all fifteen floors laid bare like a cross-section of a wound. "
                            "You see the Binding, a web of iron and light. "
                            "You see the Unraveling pressing against it from below, "
                            "not with malice but with the blind persistence of roots seeking sun. "
                            "The vision fades. You collapse, gasping, changed."
                        ),
                        "effect": {"type": "xp", "value": 30},
                    },
                    {
                        "label": "Cover your mouth and push through quickly",
                        "response": (
                            "You tear a strip from your cloak, press it over your mouth and nose, "
                            "and push through the chamber at a dead sprint. The colors blur. "
                            "Something brushes your mind — vast, alien, curious — "
                            "and then you're through, gasping clean air on the other side."
                        ),
                        "effect": {"type": "heal", "value": 10},
                    },
                    {
                        "label": "Harvest the mushrooms for later use",
                        "response": (
                            "You carefully pluck several of the glowing fungi, "
                            "wrapping them in cloth to contain the spores. "
                            "The light dies quickly once severed from the network, "
                            "but the alchemical properties remain. "
                            "These will sell well, or serve as potent reagents."
                        ),
                        "effect": {"type": "gold", "value": 20},
                    },
                ],
            },
        ],
    },
    {
        "trigger_floors": (8, 12),
        "chance": 0.05,
        "pages": [
            {
                "type": "text",
                "text": (
                    "A door that should not exist. It is made of dark wood — impossible this deep, "
                    "where no tree has ever grown — and it stands in the middle of the corridor, "
                    "attached to nothing. No frame, no wall. Just a door. "
                    "It is slightly ajar."
                ),
            },
            {
                "type": "choice",
                "text": (
                    "Warm light spills from the crack. You smell bread baking, "
                    "hear the crackle of a fireplace. Home. It smells like home — "
                    "YOUR home, specifically, a place you haven't thought about in years."
                ),
                "choices": [
                    {
                        "label": "Open the door and step through",
                        "response": (
                            "You step through into warmth and light and the scent of a meal "
                            "you ate as a child. For exactly thirty seconds, you are somewhere safe. "
                            "A room that never existed. A life that might have been. "
                            "Then it folds shut behind you and you're back in the corridor, "
                            "the door gone, your eyes wet, your wounds somehow lighter."
                        ),
                        "effect": {"type": "heal", "value": 35},
                    },
                    {
                        "label": "Slam it shut — this is a trap",
                        "response": (
                            "You kick the door closed. It resists for a moment — "
                            "the smell of bread intensifies, a voice calls your name — "
                            "then it clicks shut and vanishes. The corridor is cold and dark again. "
                            "Your heart hammers. That was close. Whatever that was, "
                            "it knew things about you that nothing down here should know."
                        ),
                        "effect": {"type": "xp", "value": 20},
                    },
                ],
            },
        ],
    },
    {
        "trigger_floors": (9, 13),
        "chance": 0.04,
        "pages": [
            {
                "type": "text",
                "text": (
                    "You find a mirror. Not a polished shield or a still pool — "
                    "an actual mirror, ornately framed, standing upright in the rubble. "
                    "Your reflection looks back at you. But it's wrong. "
                    "The reflection is you from weeks ago — before the descent. "
                    "Unscarred. Fed. Rested. Hopeful."
                ),
            },
            {
                "type": "choice",
                "text": (
                    "Your reflection smiles at you. You are not smiling. "
                    "It raises a hand and presses it against the glass from the other side. "
                    "The glass is warm to the touch."
                ),
                "choices": [
                    {
                        "label": "Press your hand to the glass",
                        "response": (
                            "Your hand meets your reflection's. Warmth floods through the glass "
                            "and into your bones. For a moment, you feel as you did before — "
                            "whole, strong, unbroken. Your reflection nods, once, "
                            "and the mirror shatters. Among the shards, "
                            "a single piece glows with captured light."
                        ),
                        "effect": {"type": "heal", "value": 30},
                    },
                    {
                        "label": "Smash the mirror",
                        "response": (
                            "You strike the glass with your weapon. It explodes inward — "
                            "not outward, INWARD — into a space that shouldn't exist behind it. "
                            "From the broken frame, a handful of gold coins spill out. "
                            "Old coins, stamped with a seal you don't recognize. "
                            "The mirror is gone. So is the person you used to be."
                        ),
                        "effect": {"type": "gold", "value": 35},
                    },
                    {
                        "label": "Study the reflection — what is it trying to tell you?",
                        "response": (
                            "You watch your reflection carefully. It mouths words you cannot hear, "
                            "then turns and walks away — into a version of the Depths "
                            "that looks different. Cleaner. Older. Before the Consortium. "
                            "Before the Binding. You memorize every detail before the image fades. "
                            "The mirror goes dark. The knowledge remains."
                        ),
                        "effect": {"type": "xp", "value": 25},
                    },
                ],
            },
        ],
    },
    {
        "trigger_floors": (10, 14),
        "chance": 0.03,
        "pages": [
            {
                "type": "text",
                "text": (
                    "The ground trembles. Cracks split the floor and a low, resonant hum "
                    "fills the chamber — the sound of the Binding straining under impossible force. "
                    "Dust and debris rain from the ceiling. The walls flex inward, "
                    "then snap back. A containment breach. Localized, but violent."
                ),
            },
            {
                "type": "choice",
                "text": (
                    "Raw energy bleeds from the cracks — not light, not heat, "
                    "but something that makes your teeth sing and your scars itch. "
                    "The breach is temporary. It will seal itself. But right now, "
                    "it offers something: a glimpse of raw, unfiltered power."
                ),
                "choices": [
                    {
                        "label": "Absorb the leaking energy",
                        "response": (
                            "You thrust your hands into the breach. Pain — exquisite, searing, "
                            "transcendent — races through every nerve. Something fundamental shifts "
                            "inside you. When the breach seals, you withdraw hands that crackle "
                            "with faint violet light. You are more than you were. "
                            "But you are also less certain of what 'you' means."
                        ),
                        "effect": {"type": "xp", "value": 40},
                    },
                    {
                        "label": "Take cover and wait it out",
                        "response": (
                            "You press yourself against the wall and ride out the tremor. "
                            "The breach seals. The hum fades. When you emerge from cover, "
                            "the cracks in the floor have left behind crystallized residue — "
                            "valuable to alchemists and Consortium researchers. "
                            "You scrape what you can into your pouch."
                        ),
                        "effect": {"type": "gold", "value": 30},
                    },
                ],
            },
        ],
    },
]


# ======================================================================
# NARRATIVE QUEST DESCRIPTIONS - flavorful alternatives to generic quest text
# ======================================================================

NARRATIVE_QUEST_TEMPLATES = {
    "kill": [
        "The shadows grow restless with {target}s. Thin their numbers — slay {count} of the wretched things.",
        "A blood-price must be paid. Hunt {count} {target}s before they multiply beyond containment.",
        "The {target}s have grown bold. Cull {count} of them and restore the fragile balance of these halls.",
        "Every {target} that breathes is a threat to the living. Put {count} of them in the ground. Permanently.",
        "The corridors reek of {target}. Exterminate {count} and reclaim what ground you can.",
    ],
    "fetch": [
        "A {item} lies somewhere in the darkness. Its power may tip the scales. Find {count}.",
        "The Consortium hid {count} {item}(s) in these depths. Retrieve what was buried.",
        "Whispers speak of a {item} lost to time. Seek it out. The Depths will not surrender it willingly.",
        "A dead delver's journal mentions {count} {item}(s) cached nearby. Find them before something else does.",
        "The traders need {count} {item}(s) to keep operations running. Scavenge what the Depths provide.",
    ],
    "explore": [
        "Map {count} chambers of this forsaken place. Knowledge of the layout may save lives — or end them.",
        "The cartographers' guild once mapped these halls. Their work is lost. Explore {count} rooms to rebuild it.",
        "Push deeper. Chart {count} unexplored rooms. Every corner revealed is a corner that can't hide an ambush.",
        "The path forward is unknown. Scout {count} chambers and report what you find — if you come back.",
    ],
    "boss": [
        "The guardian of this depth stirs. Seek the {target} and prove your worth — or perish in the attempt.",
        "{target} bars the way to the deeper chambers. It must be destroyed. Or convinced. Or survived.",
        "The {target} has claimed this floor as its domain. Challenge it, and the way forward opens. Fail, and join the bones.",
        "No one passes the {target} without paying a toll. Usually in blood.",
    ],
}

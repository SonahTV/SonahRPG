"""Class-specific backstories for SonahRPG characters."""

# Each backstory is 3-5 paragraphs, written in second person ("You were...")
# They set up the character's motivation and relationship to The Depths

CLASS_BACKSTORIES = {
    "Warrior": {
        "title": "The Disgraced Knight",
        "paragraphs": [
            (
                "You were Captain Erenne of the Warden's Guard -- the iron fist that kept "
                "Ashenmere's citizens in line and its Condemned marching into the Maw on "
                "schedule. Fifteen years you served. Fifteen years of escorting the damned to "
                "the edge and watching them disappear into the dark without so much as a scream. "
                "You told yourself it was justice. You told yourself the Consortium knew best. "
                "You told yourself a lot of things, and you believed them right up until you "
                "found out where the extra Condemned were coming from."
            ),
            (
                "Commander Halveth. Your commanding officer, your mentor, the man who pinned "
                "the captain's badge to your chest and told you that duty was the only virtue "
                "worth dying for. He had been falsifying Condemnation orders for three years, "
                "rounding up vagrants and debtors and political inconveniences and feeding them "
                "to the Maw off the books. Not as punishment. As tribute. The Consortium's "
                "Harbinger faction had convinced him that the Entity required a steady supply of "
                "souls to keep sleeping, and Halveth -- ever the dutiful soldier -- had obliged "
                "without question."
            ),
            (
                "You found the ledger in his office. Names, dates, causes of death listed as "
                "'descent (voluntary)' for people who had been dragged to the Maw in chains. "
                "Forty-seven names. Forty-seven people who had committed no crime, whose families "
                "had been told they had emigrated or died of fever or simply vanished. You "
                "confronted Halveth in his quarters. He did not deny it. He said you would "
                "understand eventually. He reached for his sword.\n\n"
                "You reached yours first."
            ),
            (
                "The tribunal lasted two days. The Consortium produced evidence that Halveth was "
                "acting under sanctioned authority -- classified authority that no captain would "
                "have been privy to. Your killing of a commanding officer was therefore not "
                "whistleblowing but murder, and murder in Ashenmere carries only one sentence. "
                "They branded the Seal of Severance on your hand at dawn, and the last thing "
                "you saw before the darkness swallowed you was Halveth's replacement already "
                "standing at the Maw's edge, ledger in hand, ready to continue the count."
            ),
            (
                "You descend not because you have accepted your punishment, but because the "
                "truth descends with you. Forty-seven names are carved into the inside of your "
                "shield. If The Depths are where the Consortium's victims end up, then you will "
                "find them. You will find them and you will bear witness, because someone has to "
                "remember, and the dead deserve better than a falsified ledger and a comfortable lie."
            ),
        ],
        "motivation": (
            "To find the souls of the innocent Condemned and bear witness to what the Consortium "
            "has done, even if no one above will ever hear the testimony."
        ),
        "secret": (
            "Commander Halveth's ledger contained a forty-eighth name that you did not recognize "
            "at the time: Arch-Binder Kael. Not a Condemned -- a volunteer. Kael entered The "
            "Depths willingly, decades after the Binding, carrying something Halveth's notes "
            "describe only as 'the key to the third path.' You do not know what the third path "
            "is, but you know that the Consortium has been searching for Kael's remains for "
            "three hundred years and has never found them."
        ),
    },
    "Rogue": {
        "title": "The Silenced Thief",
        "paragraphs": [
            (
                "You were the best second-story artist in Ashenmere, which is a polite way of "
                "saying you robbed the rich and kept every copper for yourself. No ideology, no "
                "Robin Hood pretensions -- you stole because you were good at it and because the "
                "alternative was the glue factories in the Ashfeld District, where the desperate "
                "dissolved horse bones for a wage that wouldn't cover the smell. You had rules: "
                "never steal from anyone who would miss it, never carry a weapon you intend to "
                "use, and never, ever break into the Consortium's Seventh Archive."
            ),
            (
                "You broke all three rules on the same night. A client -- anonymous, paying in "
                "unmarked gold sovereigns, communicating through dead drops -- wanted a specific "
                "document from the Archive's sealed collection. The fee was enough to leave "
                "Ashenmere forever, to buy a cottage on the coast where the ground didn't hum "
                "and the sky wasn't perpetually overcast. You didn't ask what the document was. "
                "You didn't care. You should have cared."
            ),
            (
                "The Archive's defenses were formidable but not impossible. Glyph-locked doors, "
                "pressure-sensitive floors, guard rotations timed to the minute. You spent three "
                "months mapping the patterns and four minutes inside. The document was in a lead "
                "box sealed with wax that wept when you broke it. You opened it in the alley "
                "outside, just to make sure it was the right one.\n\n"
                "You read the first three lines and your hands started shaking. You read the rest "
                "and the shaking didn't stop for a week."
            ),
            (
                "The document was the Consortium's original survey of the Entity -- the assessment "
                "conducted before the Binding, when they still thought containment was optional. "
                "It described the Entity not as a threat but as the world's substrate, the "
                "foundation upon which all reality was constructed. The Binding didn't imprison a "
                "monster. It suppressed the immune system of a living cosmos, and the Consortium "
                "knew -- they KNEW -- that the suppression would eventually fail and that when it "
                "did, the world would not end but would be rewritten. Rewritten without humanity. "
                "Without Ashenmere. Without anything that the Entity's immune response identified "
                "as a pathogen."
            ),
            (
                "You ran. You made it as far as the city gate before the Consortium's Silencers "
                "caught you. The document was confiscated. Your client vanished. The tribunal "
                "charged you with treason, sedition, and 'possession of existential contraband' "
                "-- a crime you did not know existed until it was applied to you. You were "
                "Condemned at dawn, and the last thing the Arch-Warden whispered in your ear was: "
                "'What you read was the truth. And the truth is why you can never leave.'\n\n"
                "Now you carry the truth into the dark, the only thief in history who stole "
                "something too heavy to fence and too dangerous to put down."
            ),
        ],
        "motivation": (
            "To survive long enough to find a way to transmit what you learned back to the "
            "surface -- the truth about what the Entity is and what the Binding is really doing "
            "to the world."
        ),
        "secret": (
            "Your anonymous client was a member of the Harbinger faction who wanted the document "
            "not to expose the Consortium but to complete a ritual. The original survey contains "
            "the Entity's true name -- the one thing the Binding requires to be made permanent "
            "or to be dissolved entirely. You memorized the name before the document was taken. "
            "It sits in your mind like a coal that will not cool, and sometimes, in the quiet "
            "between heartbeats, you hear it whispering itself."
        ),
    },
    "Mage": {
        "title": "The Wayward Arcanist",
        "paragraphs": [
            (
                "You were a prodigy. The youngest researcher ever admitted to the Consortium's "
                "Inner Circle, granted access to the Binding Archives at an age when most "
                "arcanists were still learning to light candles with their minds. Your thesis on "
                "seal degradation patterns earned you a commendation from the Arch-Preserver "
                "herself. Your models predicted the rate of the Binding's decay to within 0.2% "
                "accuracy. You were brilliant. You were celebrated. You were also catastrophically, "
                "unforgivably curious."
            ),
            (
                "The Sixth Archive contained theoretical models. The Seventh contained raw data. "
                "But there was an Eighth Archive that appeared on no official map, referenced only "
                "in footnotes that had been imperfectly redacted. You found it behind a wall that "
                "shouldn't have existed in a basement that the building's blueprints denied. The "
                "door was sealed with a ward so old it had fossilized, and you cracked it the way "
                "you cracked everything: with elegant mathematics and an absolute absence of "
                "restraint."
            ),
            (
                "The Eighth Archive contained the Consortium's failed experiments. Attempts to "
                "communicate with the Entity. Attempts to harness its dream-energy as a power "
                "source. Attempts to breed creatures that could survive in the Depths and report "
                "back. Each experiment more desperate than the last, each one ending in disaster "
                "and classification. And at the very back of the Archive, behind a glass case "
                "that hummed with containment fields, a single object: a fragment of the "
                "Entity's body. A splinter of something that was neither stone nor flesh nor "
                "thought, but all three simultaneously."
            ),
            (
                "You touched it. Of course you touched it. You were a researcher, and researchers "
                "touch things they shouldn't, and the fragment responded to your arcane signature "
                "like a tuning fork finding its resonance. For one ecstatic, terrible moment, you "
                "SAW. You saw the Binding from below, saw the cracks that your models had "
                "predicted, and you saw your own arcane probe -- the gentle diagnostic spell you "
                "had cast without thinking -- widen one of those cracks by a fraction of a "
                "fraction of a degree. Enough to matter. Enough to accelerate the degradation "
                "by decades."
            ),
            (
                "You reported yourself immediately. The Consortium's response was swift: your "
                "research was confiscated, your access revoked, your name struck from the "
                "academic records. The official charge was 'reckless endangerment of the Binding,' "
                "but the real crime was seeing too clearly and speaking too honestly about what "
                "you saw. You were Condemned not as punishment but as assignment -- sent into The "
                "Depths to assess the damage you caused and, if possible, to repair it from the "
                "inside. No one believes this is possible. You are not sure you believe it either. "
                "But you are the one who widened the crack, and so you are the one who must go "
                "down into the dark and try to stitch the wound closed with the same hands that "
                "opened it."
            ),
        ],
        "motivation": (
            "To reach the Binding itself and repair the damage caused by your probe -- or, if "
            "repair is impossible, to understand the Entity well enough to find another way to "
            "keep the world intact."
        ),
        "secret": (
            "When you touched the Entity's fragment, the vision you received contained more than "
            "the damage report. You saw the Binding's complete architecture, including the "
            "function of the five Arch-Binders fused into the seal. They are not anchors. They "
            "are translators. The Binding works by converting the Entity's alien cognition into "
            "patterns that human reality can process -- and the five Arch-Binders are the "
            "dictionaries. If even one of them fails, the translation breaks down, and the "
            "Entity's raw thoughts begin leaking into the world unfiltered. You also saw that "
            "one of the five -- Arch-Binder Mordecai -- has been dead for over a century. The "
            "Consortium does not know this. The seal is running on four translators instead of "
            "five, and the gaps in translation are what the people of Ashenmere experience as "
            "nightmares."
        ),
    },
    "Cleric": {
        "title": "The Faithless Priest",
        "paragraphs": [
            (
                "You were Vicar Aldren of the Cathedral of Enduring Light, the largest house of "
                "worship in Ashenmere and the spiritual anchor of a city that desperately needed "
                "something to believe in. For twenty years you led your congregation in prayers "
                "to gods whose names you spoke with conviction and whose existence you never "
                "questioned. The faithful came to you with their fears about the Maw, about the "
                "tremors, about the nightmares that plagued every citizen of Ashenmere from "
                "childhood, and you gave them comfort. You gave them hope. You gave them "
                "beautiful lies wrapped in liturgy."
            ),
            (
                "The truth came on a Tuesday, during a routine blessing of the foundations. Every "
                "year, the clergy descended into the Cathedral's crypt to renew the wards that "
                "supposedly kept the holy ground consecrated against the Depths' influence. It was "
                "ceremonial. Symbolic. The wards were decorative at best. But this year, the "
                "lowest crypt was different. A wall had collapsed, revealing a chamber that "
                "predated the Cathedral by centuries -- a chamber that predated Ashenmere itself."
            ),
            (
                "Inside, you found the original altar. Not the Cathedral's altar, with its gold "
                "leaf and its sculpted saints and its reassuring geometry. This altar was carved "
                "from a single piece of stone that was not stone, inscribed with symbols that "
                "your ordination training identified as 'pre-divine script' -- the language used "
                "before gods existed, when the world was still raw potential and the Entity was "
                "still awake. The altar was not dedicated to any god. It was dedicated to the "
                "Entity. And the inscriptions made clear that the gods your congregation worshipped "
                "-- the gods you had built your life around -- were not the Entity's creators "
                "or its jailors. They were its dreams. Every deity in every pantheon was a "
                "character in the Entity's sleeping mind, as fictional as the heroes in a "
                "bedtime story."
            ),
            (
                "You brought this to the Archbishop. The Archbishop already knew. The entire "
                "senior clergy knew. The Church of Enduring Light was not a house of worship "
                "but a house of containment, its rituals designed not to honor the gods but to "
                "reinforce the Binding through collective belief. The congregation's faith was "
                "fuel -- their prayers were converted into seal-energy by mechanisms hidden in "
                "the Cathedral's architecture. Every hymn, every sermon, every whispered prayer "
                "at a bedside was another brick in the Entity's prison. The faithful were not "
                "worshippers. They were batteries."
            ),
            (
                "You could not unknow it. You tried. You returned to your pulpit and opened your "
                "mouth to deliver the evening homily and what came out was not comfort but truth. "
                "You told them everything. The Entity, the Binding, the gods that were dreams, "
                "the prayers that were chains. The congregation wept. The Archbishop's guards "
                "dragged you from the pulpit before you finished. The charge was heresy, but the "
                "crime was honesty, and in Ashenmere, honesty about the foundations is the one "
                "sin that cannot be forgiven.\n\n"
                "You were Condemned at dawn. The Seal of Severance burned away the last of "
                "your holy symbols, and as you stood at the edge of the Maw, you felt something "
                "you had not felt in twenty years of ministry: genuine faith. Not in gods who "
                "were dreams, but in the truth that had destroyed your life and was now pulling "
                "you downward into the dark where all truths eventually settle."
            ),
        ],
        "motivation": (
            "To confront the Entity directly and determine the truth about the divine -- whether "
            "the gods are truly its dreams, and if so, whether faith has any meaning in a world "
            "built on the sleep of something that does not know it is creating."
        ),
        "secret": (
            "The pre-divine script on the original altar contained a passage that the Church "
            "hierarchy had never successfully translated, written in a grammatical tense that "
            "does not exist in any human language -- a tense that describes events that are "
            "simultaneously past, present, and future. You translated it. Your seminary training "
            "in dead languages, combined with the Entity's influence seeping through the broken "
            "wall, gave you the key. The passage reads: 'When the dreamer wakes, the dreams do "
            "not die. They become the dreamer's memory. The gods you worship will not cease to "
            "exist. They will be remembered, and to be remembered by the Entity is to become "
            "more real than you were when you were believed in.' The gods survive the waking. "
            "The world survives. But only if someone is there at the moment of waking to remind "
            "the Entity that the dream was worth having."
        ),
    },
}

def level_1():
    print("\nAct I: Embers of Fate")
    print("\nLevel 1: The Spark")
    print("The stench of burnt wood and metal assaults your nostrils. Crimson embers glow softly against the black remains of your village. You clutch a burnt pendant, its metal still warm against your palm – the last tangible memory of your mother.")
    print("A profound silence hangs in the air, broken only by the occasional crackle of dying flames.")
    while True:
        choice = input("What do you do? (examine pendant/look around/call out/search debris) ")
        if choice.lower() == 'examine pendant':
            print("You trace the scorched carvings on the pendant. It depicts a entwined flame and crescent moon. A wave of grief washes over you, followed by a flicker of fierce resolve.")
            return 'level_2'
        elif choice.lower() == 'look around':
            print("Your gaze sweeps across the devastation. Familiar landmarks are now unrecognizable piles of ash. A chilling realization sinks in: you are utterly alone.")
            return 'level_2'
        elif choice.lower() == 'call out':
            print("You cry out for your family, your voice raw with despair. The silence that answers is deafening, confirming your deepest fear.")
            return 'level_2'
        elif choice.lower() == 'search debris':
            print("Driven by a desperate hope, you sift through the charred remains of your home. You find nothing but ash and sorrow. The weight of your loss becomes unbearable.")
            return 'level_2'
        else:
            print("Invalid action. Please try again.")

def level_2():
    print("\nLevel 2: A Stranger's Oath")
    print('As dawn breaks, casting a pale light over the ruins, a figure emerges from the mist. Cloaked and imposing, he approaches you with a solemn gaze. "I am Ser Kaelen," he says, his voice resonating with authority. "I saw the fire. I saw you."')
    print('He offers a hand. "I will not raise you as a ward, orphan. I see a warrior in you. Come with me, and I will teach you the way of the blade, the meaning of honor. Swear to forge your own destiny, with fire in your veins and vengeance in your heart." The bleeding moon hangs low in the sky, a silent witness to this pivotal moment.')
    while True:
        choice = input("Do you 'accept his oath', 'hesitate and question', or 'refuse his offer'? ")
        if choice.lower() == 'accept his oath':
            print('You grasp Ser Kaelen\'s hand, a spark of hope igniting within the ashes of your despair. "I swear it," you vow, your voice filled with newfound determination.')
            return 'level_3_5'
        elif choice.lower() == 'hesitate and question':
            print('"Why me, Ser Knight?" you ask, your voice still trembling. "Why would you help a forsaken orphan?"')
            print('Ser Kaelen\'s eyes hold a strange intensity. "Destiny works in mysterious ways, child. I see a potential in you, a fire that could either save or consume this world. I choose to guide it." You decide to trust his words, for now.')
            return 'level_3_5'
        elif choice.lower() == 'refuse his offer':
            print('"I need no charity," you say, pulling away. "I will find my own way." Ser Kaelen\'s expression remains unreadable. "The road ahead is perilous, child. But the choice is yours." He leaves you standing alone once more, the weight of your solitude crushing.')
            print("Game Over. Your path diverges from the main story.")
            return None
        else:
            print("Invalid choice. Please try again.")

def level_3_5():
    print("\nLevels 3-5: Training of Ash")
    print("Years of rigorous training under Ser Kaelen transform you. The clang of steel against steel becomes a familiar rhythm. You discover a latent magical ability, wild and untamed, like the embers that claimed your past.")
    while True:
        choice = input("Focus on: (sparring/magic/learning honor/continue) ")
        if choice.lower() == 'sparring':
            print("You dedicate yourself to mastering the blade. Each parry, each strike, hones your reflexes and strengthens your resolve. You learn to anticipate your opponents, your movements becoming fluid and deadly.")
        elif choice.lower() == 'magic':
            print("You delve into the mysteries of your burgeoning magic. It feels like a volatile fire within you, capable of both creation and destruction. Ser Kaelen guides you, teaching you control and focus.")
        elif choice.lower() == 'learning honor':
            print("Ser Kaelen imparts the principles of honor, duty, and chivalry. These lessons shape your moral compass, influencing not only how you fight but who you become.")
        elif choice.lower() == 'continue':
            print("Years have passed. You are no longer just an orphan. You are a skilled warrior, touched by magic and guided by a strong sense of honor. The world beyond the training grounds awaits.")
            return 'level_6'
        else:
            print("Invalid choice. Please try again.")

def level_6():
    print("\nLevel 6: The Witch's Warning")
    print("Deep within the whispering woods, where ancient trees claw at the sky, you encounter her. Alira. Her raven hair frames a face both ethereal and intense, her silver eyes holding an ancient wisdom. The villagers speak of her in hushed tones – a witch, they say.")
    print("She approaches you with an unnerving grace. Her gaze pierces through your defenses, seeming to see the very fire that burns within you. 'Flame-born,' she murmurs, her voice like the rustling of leaves. 'Your soul is tied to the moon's fate. A prophecy stirs.' As her hand touches your chest, a jolt of energy surges through you, and the fire within pulses in recognition.")
    while True:
        choice = input("How do you react? (listen intently/express skepticism/ask about the prophecy/step back warily) ")
        if choice.lower() == 'listen intently':
            print("You are captivated by her words, a sense of destiny resonating within you. You listen as she speaks of a coming darkness, of a balance between fire and moon, and of the pivotal role you are destined to play.")
            return 'level_7_9'
        elif choice.lower() == 'express skepticism':
            print("'Prophecies are just stories,' you say, your hand instinctively moving to your sword hilt. 'And witches... they are often misunderstood.' Alira's gaze softens slightly. 'Believe what you will, Flame-born. But the threads of fate are already weaving.'")
            return 'level_7_9'
        elif choice.lower() == 'ask about the prophecy':
            print("You press Alira for more details about this prophecy. She speaks in cryptic verses and veiled allusions, hinting at great power and great sacrifice. The connection between fire and moon remains shrouded in mystery.")
            return 'level_7_9'
        elif choice.lower() == 'step back warily':
            print("An instinctual caution takes hold. 'Stay away from me, witch,' you warn, your hand gripping the pendant beneath your tunic. Alira's silver eyes hold a hint of sadness. 'The path ahead will be treacherous enough without fear guiding your steps, Flame-born.'")
            return 'level_7_9'
        else:
            print("Invalid action. Please try again.")

def level_7_9():
    print("\nLevels 7-9: Tensions Rise")
    print("At the royal court, your knighthood, earned through skill rather than birth, draws the disdainful glances of nobles. Political intrigue hangs heavy in the air, like a brewing storm.")
    print("Your path crosses with Princess Lyssandra. Her initial indifference turns to a sharp interest after you defeat her champion in a duel. Her gaze lingers on you, a mixture of respect and something more...")
    input("Press Enter to continue...")
    return 'level_10'

def level_10():
    print("\nLevel 10: Ballad of Sparks")
    print("The grand ballroom gleams with candlelight. Princess Lyssandra seeks you out, her presence radiating an aura of jasmine and fine wine. Her hand, delicate yet firm, rests in yours as you begin to dance.")
    print("In that moment, surrounded by the swirling gowns and hushed whispers, the looming war and the ghosts of your past recede. Only the intoxicating nearness of the princess and a burgeoning desire remain.")
    input("Press Enter to continue...")
    return 'level_11_13'

def level_11_13():
    print("\nLevels 11-13: Rumors of the East")
    print("Reports of strange occurrences reach the court - golems marching in the east, fire-breathers in the north. The court dismisses them, but Ser Kaelen believes the threats.")
    print("He leads a secret mission, and you experience your first real combat, slaying a corrupted drake. The smell of burning scale is a haunting reminder of the battle.")
    input("Press Enter to continue...")
    return 'level_14'

def level_14():
    print("\nLevel 14: Shadows Beneath the Skin")
    print("One stormy night, Alira appears at your tent, drenched and fevered. She collapses, vulnerable.")
    print("You stay by her side until dawn, nursing her. In her feverish sleep, she whispers truths... and your name is among them.")
    input("Press Enter to continue...")
    return 'level_15_17'

def level_15_17():
    print("\nLevels 15-17: Whispering Ruins")
    print("You and Alira discover an ancient ruin, with moonstone walls and fire-forged doors. Inside, murals depict a flame-bound hero and a moon-born witch.")
    print('Your eyes meet. A silent understanding passes between you. Alira steps back, a whisper escaping her lips: "It\'s you." ')
    input("Press Enter to continue...")
    return 'level_18_20'

def level_18_20():
    print("\nLevels 18-20: The Bond Forms")
    print("During a raid on a cursed village, Alira saves you, burning half her power to shield you. That night, firelight dances between you as a new intimacy blossoms. Your bond is no longer just prophecy - it is real.")
    input("Press Enter to continue...")
    return 'level_21_23'

def level_21_23():
    print("\nLevels 21-23: Fractures")
    print("Lyssandra learns of Alira, and jealousy turns to bitterness. Ser Kaelen warns you of your duty to the crown, a loyalty that clashes with your growing passion. The tension threatens to break everything.")
    input("Press Enter to continue...")
    return 'level_24'

def level_24():
    print("\nLevel 24: The Betrayal at Hollowspire")
    print("A noble, allied with enemy forces, sets a trap. You are ambushed. Ser Kaelen fights to buy you time, his blood staining your hands. His last words echo in your ears: 'Find your fire. Or be consumed.'")
    input("Press Enter to continue...")
    return 'level_25_27'

def level_25_27():
    print("\nLevels 25-27: Dragonfall")
    print("To the north, a dragon ravages the land. You face it, not just as a knight, but as someone marked. The fire within you surges. You strike its heart, and a strange soulbond snaps into place. You are more than fire-touched now.")
    input("Press Enter to continue...")
    return 'level_28'

def level_28():
    print("\nLevel 28: Coronation of Flames")
    print("The King summons you, naming you Flamewarden. A symbol. A tool. Lyssandra kisses you after the ceremony, her lips a mix of power and desperation. But your heart burns for another, and you pull away.")
    input("Press Enter to continue...")
    return 'level_29_31'

def level_29_31():
    print('\nLevels 29-31: The Witch\'s Truth')
    print("Alira reveals her lineage: the last Moonborn, hunted by witches and men alike. She bears a star-shaped scar, identical to those in the ancient murals. And you, her Flamebound, are destined to protect her... or destroy her.")
    input("Press Enter to continue...")
    return 'level_32_34'

def level_32_34():
    print("\nLevels 32-34: War Echoes")
    print("Skirmishes break out. Golems breach the western pass. Witches of the Covens stir. The ancient prophecy unfolds, and the ending is uncertain. Only that love could damn the world or save it.")
    input("Press Enter to continue...")
    return 'level_35'

def level_35():
    print("\nLevel 35: The Burning Choice")
    print("To stop the escalating war, you are faced with an impossible choice: kill a royal emissary, a friend, a brother in arms.")
    while True:
        choice = input("Do you make the sacrifice? (yes/no) ")
        if choice.lower() == 'yes':
            print("You make the terrible choice. The world tilts on its axis. Lyssandra's screams echo in your mind, Alira's silence weighs heavily. You have crossed a line. There is no going back.")
            return 'level_36'
        else:
            print("You cannot bring yourself to do it. The war continues to escalate, and the consequences will be dire...")
            return None # Game ends here for this choice
        return None # Should not reach here

def level_36():
    print("\nAct II: Shadows of Passion")
    print("\nLevel 36: Exile")
    print("Branded a traitor, you are exiled under storm-choked skies, Alira at your side. You flee south, through wilds where forgotten gods whisper from dead trees.")
    input("Press Enter to continue...")
    return 'level_37_39'

def level_37_39():
    print("\nLevels 37-39: The Wounded Grove")
    print("In a grove once sacred, you seek refuge. Alira is wounded, her magic unstable. You nurse her, your hand against her fevered skin, your own nascent magic a balm against her pain.")
    print("One night, she cries out, not in pain, but in a raw surrender. You kiss her, tasting her sorrow, and find solace in each other's arms under the ghost-lit boughs.")
    input("Press Enter to continue...")
    return 'level_40'

def level_40():
    print("\nLevel 40: The Voice of the Flame")
    print("A dream pulls you under. A dragon of pure fire speaks from within your very being. 'You are my heir,' it proclaims. 'Fireborn not of blood, but of soul.' You awaken with hands ablaze, eyes glowing gold. Alira stares at you, a mixture of awe and fear in her silver gaze.")
    input("Press Enter to continue...")
    return 'level_41_43'

def level_41_43():
    print("\nLevels 41-43: March of Stone")
    print("Golem armies march from the east, their movements relentless and cold. Rumors speak of a queen of stone and ash who commands them. You and Alira pursue them to the jagged peaks of the Cracked Spine canyon.")
    print("What you find chills you to the bone: Lyssandra, clad in obsidian armor, leading the stone legions. Her heart, shattered by betrayal, has turned to ice and vengeance.")
    input("Press Enter to continue...")
    return 'level_44'

def level_44():
    print("\nLevel 44: The Battle of Shatterwall")
    print("The canyon echoes with the clash of magic and stone. Alira summons storms of silver light, while you unleash torrents of fire. But Lyssandra, driven by a force beyond her own, will not fall.")
    print("'You chose her!' she screams, her voice laced with pain and fury. In that moment, you understand: she is not leading them. She is possessed.")
    input("Press Enter to continue...")
    return 'level_45_47'

def level_45_47():
    print("\nLevels 45-47: Into the Mirrorhold")
    print("To save Lyssandra, you and Alira venture into the Mirrorhold, a treacherous realm of inner reflections. You are forced to confront your own cruelties, your jealousies, your broken past.")
    print("Alira faces her deepest fear: that you will abandon her. You emerge from the mirrored depths changed, hardened, your bond with Alira forged anew in the crucible of self-awareness.")
    input("Press Enter to continue...")
    return 'level_48'

def level_48():
    print("\nLevel 48: The Moonlit Reunion")
    print("Under the soft glow of a full moon, a rare moment of peace settles between you and Alira. She bathes in the silvery light, her skin shimmering like moon-kissed silk. You join her, the cool night air against your heated skin.")
    print("Whispers of promises, unspoken before, now fill the air. That night, her tears are not of sorrow, but of a profound connection only you understand. She trembles only for you.")
    input("Press Enter to continue...")
    return 'level_49_51'

def level_49_51():
    print('\nLevels 49-51: The Witch Queen\'s Pact')
    print("The Nine Witches of the Covens demand Alira's fealty, threatening her very life if she refuses. To protect her, you challenge their ancient matriarch to a duel in a hall woven from illusions.")
    print("When you fall to one knee, seemingly defeated, Alira steps forward, her voice ringing with defiance. 'He is mine,' she declares. 'He is flame to my moon.' Impressed by your bond, the witches allow you to live.")
    input("Press Enter to continue...")
    return 'level_52'

def level_52():
    print("\nLevel 52: The First Eclipse")
    print("The sun vanishes without warning. The First Eclipse has begun, plunging the realm into an eerie twilight. Fires dwindle, crops wither, and a primal unease stirs among the beasts. Prophecy has begun its inexorable march.")
    print("Deep within you, you feel a subtle shift, something awakening beneath your skin.")
    input("Press Enter to continue...")
    return 'level_53_55'

def level_53_55():
    print("\nLevels 53-55: The Journey to Vael'thorin")
    print("You and Alira journey to the ancient city of Vael'thorín, said to hold the Moonforge, a place of immense power. Along the way, you gather unlikely allies: an elven assassin bound by a debt to Alira, and a dwarven pyromancer fascinated by your fiery nature. Bonds of trust and a simmering passion weave between you all.")
    input("Press Enter to continue...")
    return 'level_56'

def level_56():
    print("\nLevel 56: Temptation")
    print("One moonlit night, the elven assassin, their movements like liquid shadow, kisses you. It is a fleeting moment, a brush of lips and a spark of unexpected heat, leaving you both confused. Alira sees the exchange, and the hurt in her silver eyes burns more fiercely than any flame. That night, silence hangs heavy between you.")
    input("Press Enter to continue...")
    return 'level_57'

def level_57():
    print("\nLevel 57: The Soul Trial")
    print("To enter the Moonforge, an ancient trial demands a sacrifice of memory. You offer your happiest: Alira laughing freely in the sacred grove. The forge accepts your offering, and your power surges, amplified by the ancient magic. Yet, a part of you feels strangely emptier.")
    input("Press Enter to continue...")
    return 'level_58_60'

def level_58_60():
    print('\nLevels 58-60: Lyssandra\'s Redemption')
    print("Captured and purged of the obsidian corruption, Lyssandra is returned to herself, her eyes filled with a profound sorrow. She weeps in your arms, confessing her desperate desire to be loved. You hold her, offering comfort, but your heart belongs elsewhere. She kisses your cheek, a sisterly gesture, and whispers, 'Then die for her, not me.'")
    input("Press Enter to continue...")
    return 'level_61'

def level_61():
    print("\nLevel 61: The Ashborn Army")
    print("From the frozen north, a new terror arises: the Ashborn, souls of the dead twisted by the encroaching moonfire. You lead the charge against them, steel in hand, fury in your heart. You ride a dragon, its scales mirroring your inner fire. Alira rides beside you on a fierce storm-wolf. Fire and lightning clash against steel and shadow.")
    input("Press Enter to continue...")
    return 'level_62'

def level_62():
    print("\nLevel 62: Passion Before the End")
    print("Before the final, brutal battle of this act, you and Alira find solace in each other's arms once more. Not out of desperation, but out of a deep and abiding devotion. In the heart of an ancient temple, bathed in candlelight and the scent of rose ash, you become one, your souls intertwining in a bond stronger than prophecy.")
    input("Press Enter to continue...")
    return 'level_63_64'

def level_63_64():
    print("\nLevels 63-64: Battle of the Wyrmspire")
    print("The final confrontation takes place atop cliffs that pierce the very stars. Lyssandra leads your combined forces with newfound resolve. You face the Ashborn king, his essence a chilling void, and burn him into nothingness. Alira seals the dimensional rift with a sacrifice of her own blood, collapsing in your arms, weakened but alive. Her magic, however, has begun to fade.")
    input("Press Enter to continue...")
    return 'level_65'

def level_65():
    print("\nLevel 65: A Moment of Peace")
    print("A fragile victory. The First Eclipse ends, but a second moon appears in the sky – dark, cracked, and radiating a hungry light. The mythic omen of the Endflame. You hold Alira close as the twin moons cast their eerie glow, and the wind whispers that your fate is far from over.")
    input("Press Enter to continue...")
    return 'level_66'

def level_66():
    print('\nAct III: The Moon\'s Reckoning')
    print("\nLevel 66: The Dark Moon Rises")
    print("Overnight, it appears – a second moon, vast and fractured, bleeding an unnatural light across the sky. The Dark Moon. Alira trembles when she sees it, her remaining magic flickering erratically. 'It's not a moon,' she whispers, her voice filled with dread. 'It's a wound in the sky.'")
    input("Press Enter to continue...")
    return 'level_67_69'

def level_67_69():
    print("\nLevels 67-69: Skyfall Citadel")
    print("You and Alira fly to the Elvoran Skylands, where the ancient citadel of Skyfall hangs suspended among the clouds. Its once grand halls are deserted, its dragons restless and agitated. There, in a chamber echoing with the whispers of stars, you learn a profound truth: you were not merely chosen, but forged in the heart of prophecy, born of fire and starlight.")
    input("Press Enter to continue...")
    return 'level_70'

def level_70():
    print("\nLevel 70: Awakening the Flamebound")
    print("You stand atop the volcanic Isle of Ash and unleash a primal cry that echoes across the heavens. Fire surges up your spine, scales like molten gold coil beneath your skin, and your eyes burn with an inner light. You become the Flamebound – a hybrid of mortal and elemental, the living protector of the ancient myth.")
    input("Press Enter to continue...")
    return 'level_71_72'

def level_71_72():
    print("\nLevels 71-72: Stoneborn Rebellion")
    print("In the subterranean Stoneborn Depths, the golem legions rise in rebellion against the Ashborn. You meet with Forgeheart, their sentient leader, in his molten throne room. You pledge your allegiance to their cause, and in return, he gifts you the Emberbrand – a weapon that hungers for heat and whispers with the memories it consumes.")
    input("Press Enter to continue...")
    return 'level_73_75'

def level_73_75():
    print("\nLevels 73-75: Embers of the Past")
    print("Through the perilous Forgeheart Trials, the Emberbrand forces you to relive your greatest failures: Kaelen's death, Lyssandra's descent, Alira's fading strength. You emerge from the fiery trials bleeding and scarred, but your resolve remains unbroken. Your memories become the very runes etched into the blade.")
    input("Press Enter to continue...")
    return 'level_76_78'

def level_76_78():
    print("\nLevels 76-78: Eclipse Marshes")
    print("In the desolate swamps shrouded by the eternal eclipse, the Coven of Nine awaits. Alira's own kin. They demand her sacrifice to appease the Dark Moon and halt its advance. You refuse, choosing love over ancient tradition, and flee, pursued by the very witches who once called her sister.")
    input("Press Enter to continue...")
    return 'level_79'

def level_79():
    print("\nLevel 79: Soulbind Severed")
    print("You are ambushed by the relentless coven. You fall, wounded and vulnerable. Alira steps between you and certain death. In a desperate act of love, she severs your soulbond, taking your pain, your fading strength, into herself. You awaken to a chilling emptiness. She is gone.")
    input("Press Enter to continue...")
    return 'level_80'

def level_80():
    print("\nLevel 80: Alone in the Mire")
    print("Lost and broken in the desolate mire, you wander aimlessly, half-dead. It is Lyssandra who finds you, her face etched with a weary understanding. She nurses you back to health with her own magic and a bitter smile. 'I told you you'd die for her,' she says, her voice hollow. 'Now live for yourself.'")
    input("Press Enter to continue...")
    return 'level_81_83'

def level_81_83():
    print("\nLevels 81-83: War-Torn Realms")
    print("Across the fractured kingdoms, war rages with renewed ferocity. Ashborn, corrupted dragons, and the relentless witches of the coven tear the land apart. You lead desperate campaigns, steel in hand, your heart a hollow echo of Alira's name. But the fire within you burns dimmer now.")
    input("Press Enter to continue...")
    return 'level_84'

def level_84():
    print("\nLevel 84: Return of the Storm-Wolf")
    print("Against all odds, Alira returns. But she is changed. Her eyes burn with silver fire, her skin crackles with raw power. She has become something new, something forged in sacrifice: a Moonbound sorceress. She kisses you once, a fleeting touch of ice and starlight, and you know, with a chilling certainty, that she is fading.")
    input("Press Enter to continue...")
    return 'level_85'

def level_85():
    print("\nLevel 85: The Last Choice")
    print("To stop the encroaching darkness of the second eclipse, the Dark Moon must be shattered from within. But the only way to open a path is through the consumption of a soulbond. Yours, or hers.")
    while True:
        choice = input("Whose soulbond will be consumed? (yours/hers) ")
        if choice.lower() == 'yours':
            print("You make the ultimate sacrifice, offering the remnants of your bond to open the way. A searing pain engulfs you as a part of your very being is consumed...")
            return 'level_86_89'
        elif choice.lower() == 'hers':
            print("With a heavy heart, you accept Alira's fading strength must be the key. A wave of sorrow washes over you as her essence prepares for the final sacrifice...")
            return 'level_86_89'
        else:
            print("Invalid choice. Please try again.")

def level_86_89():
    print("\nLevels 86-89: Astral Veil")
    print("You step through the shimmering Moon Gate into the Astral Veil, a liminal realm between memory and myth. Together, you face shadow-versions of yourselves: twisted by jealousy, consumed by coldness, shattered by loss. In a garden of stars, defiant against the encroaching darkness, you make love one last time, a radiant act of defiance. You beg her not to leave you, your voice thick with despair.")
    input("Press Enter to continue...")
    return 'level_90'

def level_90():
    print("\nLevel 90: Her Decision")
    print("At the spire's peak, bathed in the ethereal glow of the twin moons, Alira whispers, her voice a fading echo of moonlight. 'You have carried the fire, my love. Let me carry the shadow.' With a serene smile, she sacrifices herself, her essence becoming pure light and moonstone, shattering the veil and opening the path to the Dark Moon. You scream her name, but no sound escapes your lips.")
    input("Press Enter to continue...")
    return 'level_91_94'

def level_91_94():
    print("\nLevels 91-94: Spires of Ascension")
    print("Alone, you ascend the twin spires, each step a heavy burden of grief. You face trials of heart, of hope, of enduring love. At the summit, you look down upon a world beginning to heal, but the emptiness beside you is a constant ache. You kneel in silent mourning.")
    input("Press Enter to continue...")
    return 'level_95'

def level_95():
    print("\nLevel 95: The New Flame")
    print("With a heavy heart, you place the Emberbrand onto the ancient Altar of Waking. The earth trembles, and a wave of life surges through the land. Alira's voice, faint but clear, echoes in your mind: 'Love is not what ends us. It is what makes us endure.'")
    input("Press Enter to continue...")
    return 'level_96_98'

def level_96_98():
    print("\nLevels 96-98: Final Battle")
    print("The cracked surface of the Dark Moon ruptures, and the Ashborn King emerges – an ancient god made flesh, his power a chilling embodiment of shadow and despair. You fight him in the skies, in the depths of the sea, among the distant stars. Lyssandra, the Stoneborn, and all your allies stand with you, a beacon of hope against the encroaching darkness.")
    input("Press Enter to continue...")
    return 'level_99'

def level_99():
    print("\nLevel 99: One Last Gift")
    print("As the Ashborn King unleashes a final, devastating blow, darkness closing in, a surge of light catches you. A silver flame, familiar and beloved. Alira. Not as she was, but as pure essence. She merges with you, your soulbond reigniting with a blinding intensity. You rise, burning with the power of both moon and fire, and strike the final, decisive blow.")
    input("Press Enter to continue...")
    return 'level_100'

def level_100():
    print("\nLevel 100: Under Twin Moons")
    print("Peace settles over the land. The sky clears, and two moons now hang in the balance – one of fire, one of light. You return to the sacred grove where you first truly knew Alira. There, you plant a seed of silver flame. From it grows a radiant tree, its leaves whispering her name on the wind.")
    print("\nEpilogue:")
    print("You are the Flamewarden. Lover of the Moonborn. The world sings again. But at night, when you close your eyes, you still feel her beside you.")
    print("\nAnd sometimes—when the twin moons align—you swear you hear her whisper:")
    print("'My love... we were never meant to end. Only to burn eternal.'")
    return None # End of the game

def play_game():
    current_level = 'level_1'
    while current_level:
        if current_level == 'level_1':
            current_level = level_1()
        elif current_level == 'level_2':
            current_level = level_2()
        elif current_level == 'level_3_5':
            current_level = level_3_5()
        elif current_level == 'level_6':
            current_level = level_6()
        elif current_level == 'level_7_9':
            current_level = level_7_9()
        elif current_level == 'level_10':
            current_level = level_10()
        elif current_level == 'level_11_13':
            current_level = level_11_13()
        elif current_level == 'level_14':
            current_level = level_14()
        elif current_level == 'level_15_17':
            current_level = level_15_17()
        elif current_level == 'level_18_20':
            current_level = level_18_20()
        elif current_level == 'level_21_23':
            current_level = level_21_23()
        elif current_level == 'level_24':
            current_level = level_24()
        elif current_level == 'level_25_27':
            current_level = level_25_27()
        elif current_level == 'level_28':
            current_level = level_28()
        elif current_level == 'level_29_31':
            current_level = level_29_31()
        elif current_level == 'level_32_34':
            current_level = level_32_34()
        elif current_level == 'level_35':
            current_level = level_35()
        elif current_level == 'level_36':
            current_level = level_36()
        elif current_level == 'level_37_39':
            current_level = level_37_39()
        elif current_level == 'level_40':
            current_level = level_40()
        elif current_level == 'level_41_43':
            current_level = level_41_43()
        elif current_level == 'level_44':
            current_level = level_44()
        elif current_level == 'level_45_47':
            current_level = level_45_47()
        elif current_level == 'level_48':
            current_level = level_48()
        elif current_level == 'level_49_51':
            current_level = level_49_51()
        elif current_level == 'level_52':
            current_level = level_52()
        elif current_level == 'level_53_55':
            current_level = level_53_55()
        elif current_level == 'level_56':
            current_level = level_56()
        elif current_level == 'level_57':
            current_level = level_57()
        elif current_level == 'level_58_60':
            current_level = level_58_60()
        elif current_level == 'level_61':
            current_level = level_61()
        elif current_level == 'level_62':
            current_level = level_62()
        elif current_level == 'level_63_64':
            current_level = level_63_64()
        elif current_level == 'level_65':
            current_level = level_65()
        elif current_level == 'level_66':
            current_level = level_66()
        elif current_level == 'level_67_69':
            current_level = level_67_69()
        elif current_level == 'level_70':
            current_level = level_70()
        elif current_level == 'level_71_72':
            current_level = level_71_72()
        elif current_level == 'level_73_75':
            current_level = level_73_75()
        elif current_level == 'level_76_78':
            current_level = level_76_78()
        elif current_level == 'level_79':
            current_level = level_79()
        elif current_level == 'level_80':
            current_level = level_80()
        elif current_level == 'level_81_83':
            current_level = level_81_83()
        elif current_level == 'level_84':
            current_level = level_84()
        elif current_level == 'level_85':
            current_level = level_85()
        elif current_level == 'level_86_89':
            current_level = level_86_89()
        elif current_level == 'level_90':
            current_level = level_90()
        elif current_level == 'level_91_94':
            current_level = level_91_94()
        elif current_level == 'level_95':
            current_level = level_95()
        elif current_level == 'level_96_98':
            current_level = level_96_98()
        elif current_level == 'level_99':
            current_level = level_99()
        elif current_level == 'level_100':
            current_level = level_100()
        elif current_level is None:
            break # End the game
if __name__ == "__main__":
    play_game()

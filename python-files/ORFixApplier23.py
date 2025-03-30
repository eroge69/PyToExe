#Code fix and improved by golanah921
#Original idea by Nooble_

import os
import argparse

parser = argparse.ArgumentParser(description="Apply ORFIX to character.ini")
parser.add_argument("-im", "--merged", action="store_true", help="ORFIX ignore to merged.ini")
parser.add_argument("-ic", "--ignorechar", action="store_true", help="ORFIX ignore character.ini")
parser.add_argument("-isf", "--ignoreshaderfix", action="store_true", help="ORFIX ignore chara file that has shader fix script applied")
parser.add_argument("-id", "--ignoredisabled", action="store_true", help="ORFIX ignore file begin with DISABLED")
parser.add_argument("-un", "--usename", action="store_true", help="ORFIX detect using character name if no matching hash found")

args = parser.parse_args()

chara_name_Position_IB_Hash = [['Dori','2a2a63ab','04929496'],['Collei','348e58c4','3da6f8c7'],['Tighnari','ed2e7d59','69a807fc'],['Candace','9cee8711','a84cc930'],['Cyno','226f076e','af184471'],['Nilou','b2acc1df','1e8a5e3c'],['Nahida','7106f05d','9b13c166'],['Layla','2656ccca','8ec3c0d8'],['Faruzan','6162188c','faad3720'],['Wanderer','0110e1c7','6bba515c'],['Alhaitham','3ef08385','639d1fb8'],['YaoYao','293449d6','6c14db37'],['Dehya','9aeecbcb','63e3e58e'],['Mika','1876e82e','41760901'],['Baizhu','17baa562','be0be707'],['Kaveh','b56fd424','5966a63f'],['Kirara','b57d7fe2','f6e9af7d'],['Lyney','6f7b7740','09bcb0fd'],['Lynette','98eb2db4','39d89255'],['Freminet','d2bfc751','1812a5f8'],['Neuvillette','cad3a022','f055eadd'],['Wriothesley','c351ac3a','9e62b4e7'],['Furina','8294fe98','045e580b'],['Charlotte','c5a6d98e','ff554aca'],['Navia','f4e09bd7','7321d0b1'],['Chevreuse','4d8d965a','77208d51'],['Xianyun','39838e8f','7f79ea6e'],['GaMing','b94ef036','b5eb19b6'],['Gaming','ad952c56','6cb43453'],['AyakaSpring','cf78a1d0','bb6ced0e'],['LisaStudent','37c70461','f30eece6'],['KaeyaSailwind','b9b77eff','59f2a0f2'],['GanyuTwilight','9b3f356e','cb283c86'],['ShenheFrostFlower','ee0980eb','83a9116d'],['Arlecchino','6895f405','e811d2a1'],['Sethos','60d33d25','2faea4e4'],['Clorinde','07f8ad68','d6371da1'],['Sigewinne','c883a144','072fe941'],['NilouBreeze','7d53d78f','00439fbb'],['KiraraBoots','f8013ba9','846979e2'],['Emilie','62679081','ad5364a7'],['Mualani','03872d46','c511e979'],['Kachina','888c4b7c','8f29c0bb'],['Kinich','42796c33','bceefe19'],['Xilonen','a4571ede','4c2fa96d'],['Chasca','b5a29a7d','d41fb0ea'],['Ororon','effae185','503c0cb0'],['Citlali','362dc30c','f81f893c'],['Mavuika','80b13a2f','43f8af29'],['LanYan','e9049ebd','1066a76c'],['HuTaoSkin','a78db232','92fce51e'],['XianglingSkin','05a65c3f','cc7a4851'],['MavuikaBike','04b33215','9bec497f'],['Yumemizuki Mizuki','bbdaf598','ec1ed3c9']]
#chara_name_PositionHash = [['Dori','2a2a63ab'],['Collei','348e58c4'],['Tighnari','ed2e7d59'],['Candace','9cee8711'],['Cyno','226f076e'],['Nilou','b2acc1df'],['Nahida','7106f05d'],['Layla','2656ccca'],['Faruzan','6162188c'],['Wanderer','0110e1c7'],['Alhaitham','3ef08385'],['YaoYao','293449d6'],['Dehya','9aeecbcb'],['Mika','1876e82e'],['Baizhu','17baa562'],['Kaveh','b56fd424'],['Kirara','b57d7fe2'],['Lyney','6f7b7740'],['Lynette','98eb2db4'],['Freminet','d2bfc751'],['Neuvillette','cad3a022'],['Wriothesley','aa6f1268'],['Furina','8294fe98'],['Charlotte','c5a6d98e'],['Navia','f4e09bd7'],['Chevreuse','4d8d965a'],['Xianyun','39838e8f'],['GaMing','b94ef036'],['Gaming','ad952c56'],['AyakaSpring','cf78a1d0'],['LisaStudent','37c70461'],['KaeyaSailwind','b9b77eff'],['GanyuTwilight','9b3f356e'],['ShenheFrostFlower','ee0980eb'],['KleeBlossomingStarlight','0f5fedb4'],['Chiori','c8e25747']]
chara_post30_no_orfix_need=['KleeBlossomingStarlight','ShenheFrostFlower','Chiori']
#chara_name = ['Dori','Collei','Tighnari','Candace','Cyno','Nilou','Nahida','Layla','Faruzan','Wanderer','Alhaitham','YaoYao','Dehya','Mika','Baizhu','Kaveh','Kirara','Lyney','Lynette','Freminet','Neuvillette','Wriothesley','Furina','Charlotte','Navia','Chevreuse','Xianyun','GaMing','Gaming','AyakaSpring','LisaStudent','KaeyaSailwind','GanyuTwilight','ShenheFrostFlower']
chara_part = ['Body','Dress','Head','Extra','HatHead','JacketHead','JacketBody','HoodDownHead']
excludepart = ['TighnariFaceHead','CynoDress','CynoFaceHead','NilouFaceHead','FaruzanDress','MikaDress','LynetteHead','LynetteDress','NeuvilletteHead','NeuvilletteDress','FurinaDress','AyakaSpringDress','KaeyaSailwindHead','KaeyaSailwindDress','GanyuTwilightDress','GanyuTwilightBody','ShenheFrostFlowerHead','ShenheFrostFlowerBody','ShenheFrostFlowerDress','ShenheFrostFlowerExtra','ArlecchinoDress','NilouBreezeHead','NilouBreezeBody','NilouBreezeDress','HuTaoSkinBody','HuTaoSkinExtra']
donotneed = ['FaceHead', 'VertexLimitRaise', 'IB','Position','Blend','Texcoord','FXHead','FxHead','MavuikaSunglasses','PonytailHead']
checklist =[]
genshin_patch = "5.4 second  half"
orfix = f"run = CommandList\global\ORFix\ORFix"

input("IMPORTANT: This ORFIXApplier script only work for character released up to genshin patch "+genshin_patch+".\nCheck for newer version if the character is release after "+genshin_patch+" patch.\nPress Enter to start applying ORFIX")

############Old shaderfix remover##########
###Shadercode
Shadercode0 =r"""; Version 1.0.0 AGMG Tool Developer Version 3 Shader Fixer


; Generated shader fix for 3.0+ GIMI importer characters. Please contact the tool developers at https://discord.gg/agmg if you have any questions.

; Variables -----------------------
"""
Shadercode1 = r"""[Constants]
global $CharacterIB
;0=none, 1=head, 2=body, 3=dress, 4=extra, etc.

[Present]
post $CharacterIB = 0

[ResourceRefHeadDiffuse]
[ResourceRefHeadLightMap]
[ResourceRefBodyDiffuse]
[ResourceRefBodyLightMap]
[ResourceRefDressDiffuse]
[ResourceRefDressLightMap]
[ResourceRefExtraDiffuse]
[ResourceRefExtraLightMap]

; ShaderOverride ---------------------------

[ShaderRegexCharReflection]
shader_model = ps_5_0
run = CommandListReflectionTexture
[ShaderRegexCharReflection.pattern]
mul r\d+\.\w+, r\d+\.\w+,[^.]*\.\w+\n
mad o\d+\.\w+, r\d+\.\w+, cb\d+\[\d+\]\.\w+, r\d+\.\w+\n
mov o\d+\.\w+, l\(\d+\.\d+\)\n

[ShaderRegexCharOutline]
shader_model = ps_5_0
run = CommandListOutline
[ShaderRegexCharOutline.pattern]
mov o\d+\.\w+, l\(\d+\)\n
mov o\d+\.\w+, r\d+\.\w+\n
mov o\d+\.\w+, l\(\d+\.\d+\)

; OPTIONAL: If regex match breaks, use a [ShaderOverride] command matching shader hash for reflection then use "run = CommandListOutline" under the command

; CommandList -------------------------

[CommandListReflectionTexture]
if $CharacterIB != 0
    if $CharacterIB == 1
        ps-t0 = copy ResourceRefHeadDiffuse
    else if $CharacterIB == 2
        ps-t0 = copy ResourceRefBodyDiffuse
    else if $CharacterIB == 3
        ps-t0 = copy ResourceRefDressDiffuse
    else if $CharacterIB == 4
        ps-t0 = copy ResourceRefExtraDiffuse    
    endif
drawindexed=auto
$CharacterIB = 0
endif

[CommandListOutline]
if $CharacterIB != 0
    if $CharacterIB == 1
        ps-t1 = copy ResourceRefHeadLightMap
    else if $CharacterIB == 2
        ps-t1 = copy ResourceRefBodyLightMap
    else if $CharacterIB == 3
        ps-t1 = copy ResourceRefDressLightMap
    else if $CharacterIB == 4
        ps-t1 = copy ResourceRefExtraLightMap
    endif
drawindexed=auto
$CharacterIB = 0
endif
"""
Shadercode2 = r"""[Constants]
global $CharacterIB
;0=none, 1=head, 2=body, 3=dress, 4=extra, etc.

[Present]
post $CharacterIB = 0

[ResourceRefHeadDiffuse]
;[ResourceRefHeadLightMap]
[ResourceRefBodyDiffuse]
;[ResourceRefBodyLightMap]
[ResourceRefDressDiffuse]
;[ResourceRefDressLightMap]
[ResourceRefExtraDiffuse]
;[ResourceRefExtraLightMap]

; ShaderOverride ---------------------------

[ShaderRegexCharReflection]
shader_model = ps_5_0
run = CommandListReflectionTexture
[ShaderRegexCharReflection.pattern]
mul r\d+\.\w+, r\d+\.\w+,[^.]*\.\w+\n
mad o\d+\.\w+, r\d+\.\w+, cb\d+\[\d+\]\.\w+, r\d+\.\w+\n
mov o\d+\.\w+, l\(\d+\.\d+\)\n

;[ShaderRegexCharOutline]
;shader_model = ps_5_0
;run = CommandListOutline
;[ShaderRegexCharOutline.pattern]
;mov o\d+\.\w+, l\(\d+\)\n
;mov o\d+\.\w+, r\d+\.\w+\n
;mov o\d+\.\w+, l\(\d+\.\d+\)
;broken as of version 4.0

; OPTIONAL: If regex match breaks, use a [ShaderOverride] command matching shader hash for reflection then use "run = CommandListOutline" under the command

; CommandList -------------------------

[CommandListReflectionTexture]
if $CharacterIB != 0
    if $CharacterIB == 1
        ps-t0 = copy ResourceRefHeadDiffuse
    else if $CharacterIB == 2
        ps-t0 = copy ResourceRefBodyDiffuse
    else if $CharacterIB == 3
        ps-t0 = copy ResourceRefDressDiffuse
    else if $CharacterIB == 4
        ps-t0 = copy ResourceRefExtraDiffuse    
    endif
drawindexed=auto
$CharacterIB = 0
endif

;[CommandListOutline]
;if $CharacterIB != 0
;    if $CharacterIB == 1
;        ps-t1 = copy ResourceRefHeadLightMap
;    else if $CharacterIB == 2
;        ps-t1 = copy ResourceRefBodyLightMap
;    else if $CharacterIB == 3
;        ps-t1 = copy ResourceRefDressLightMap
;    else if $CharacterIB == 4
;        ps-t1 = copy ResourceRefExtraLightMap
;    endif
;drawindexed=auto
;$CharacterIB = 0
;endif
"""
Shadercode3 ="""$CharacterIB = 1
ResourceRefHeadDiffuse = reference ps-t1
ResourceRefHeadLightMap = reference ps-t2

"""
Shadercode4 ="""$CharacterIB = 2
ResourceRefBodyDiffuse = reference ps-t1
ResourceRefBodyLightMap = reference ps-t2

"""
Shadercode5 ="""$CharacterIB = 3
ResourceRefDressDiffuse = reference ps-t1
ResourceRefDressLightMap = reference ps-t2

"""
Shadercode6 ="""$CharacterIB = 4
ResourceRefExtraDiffuse = reference ps-t1
ResourceRefExtraLightMap = reference ps-t2

"""
Shadercode7 ="""$CharacterIB = 1
ResourceRefHeadDiffuse = reference ps-t1
"""
Shadercode8 ="""$CharacterIB = 2
ResourceRefBodyDiffuse = reference ps-t1
"""
Shadercode9 ="""$CharacterIB = 3
ResourceRefDressDiffuse = reference ps-t1
"""
Shadercode10 ="""$CharacterIB = 4
ResourceRefExtraDiffuse = reference ps-t1
"""


####Old shaderfix remover function
def remove_old_shaderfix(lines):
    """
    Removes shader code from the given list of lines and checks if the new lines are different.
    
    Args:
        lines (list): List of strings representing the lines of the file.
    
    Returns:
        tuple: A tuple containing:
            - new_lines (list): List of strings with shader code removed.
            - is_modified (bool): True if new_lines is different from lines, False otherwise.
    """
    is_modified = False
    # Convert the list of lines into a single string for easier processing
    content = "".join(lines)
    
    # Remove the shader code patterns for any Shadercode in the format Shadercode+number
    for var_name, var_value in globals().items():
        if var_name.startswith("Shadercode") and isinstance(var_value, str):
            content = content.replace(var_value, '')
    # Split the content back into lines
    new_lines = content.splitlines(keepends=True)
    
    # Check if the new lines are different from the old lines
    is_modified = new_lines != lines
    
    return new_lines, is_modified

####Result normlize and strip function

def normalize(lines):
    normalized_lines = []
    for line in lines:
        #Converting line with orfix and original file (due to the way orfix is inserted in merged.ini) to two line
        split_lines = line.split("\n")
        for part in split_lines:
            #Removing empty line (Due to the way orfix line was removed)
            stripped_part = part.strip()
            if stripped_part:
                normalized_lines.append(stripped_part)
    return normalized_lines

###Main + orfix applier/remover
for r, d, f in os.walk(".\\"):
    for file in f:
        if not (args.ignoredisabled == True and file.startswith ("DISABLED")):
            if file.endswith(".ini") and not file.endswith ("desktop.ini") and not file.endswith("ORFix.ini") and "BufferValues" not in os.path.join(r, file) and "NOAPP" not in os.path.join(r, file):
                print(".ini file found!: " + os.path.join(r, file))
                try:
                    with open(os.path.join(r, file), "r", encoding ="utf-8") as openFile:
                        lines = openFile.readlines()
                        lines_backup = lines.copy()
                        override = False
                        override_loop = False
                        ifencounter = False
                        old_shader_fix = False 
                        drawindexed_encounter = False
                        drawindexed_encounter_count =0
                        state = 0
                        chara_position_hash_name = ""
                        chara_IB_hash_name = ""
                        chara_name = ""
                        old_shader_fix_found = 0
                        have_orfix = 0
                        checked_part_list=[]
                        checked = False
                        orfix_applier_changed = False
                        old_shaderfix_removed_changed = False
                        #Remove any oldshaderfix if detected
                        lines, old_shaderfix_removed_changed = remove_old_shaderfix(lines)
                        lines_backup_old_shader_removed = lines.copy()
                        #Detect orfix in file
                        for i, line in enumerate(lines):
                            if (orfix).lower() in line.lower():
                                lines[i]=""
                                have_orfix = 1
                        #check ini for chara_name
                        for line in lines:
                            for i in range(len(chara_name_Position_IB_Hash)):
                                if chara_name_Position_IB_Hash[i][1] in line:
                                    chara_position_hash_name = chara_name_Position_IB_Hash[i][0]
                                if chara_name_Position_IB_Hash[i][2] in line:
                                    chara_IB_hash_name = chara_name_Position_IB_Hash[i][0]
                                if len(chara_position_hash_name)!=0 and chara_IB_hash_name!=0:
                                # If both possitiion hash and IB hash of the same chara is found, search is finished
                                    if chara_position_hash_name == chara_IB_hash_name:
                                        chara_name = chara_position_hash_name
                                        break
                            if args.ignoreshaderfix == True:
                                #Check if .ini have old shader fix
                                if "$CharacterIB" in line:                                                
                                    old_shader_fix = True
                                    old_shader_fix_found = 1
                                    break
                            if args.ignoreshaderfix == True:
                                if len(chara_name) != 0 and old_shader_fix_found ==1:
                                    break
                            else:
                                if len(chara_name) != 0:
                                    break
                        if args.usename == True and len(chara_name) == 0:
                            for i in range(len(chara_name_Position_IB_Hash)):
                                if chara_name_Position_IB_Hash[i][0] in lines[0]:
                                    print("No matching position or IB hash found.\nChara found using name")
                                    chara_name = (chara_name_Position_IB_Hash[i][0])
                        #Create checklist
                        checklist.clear()
                        for part in chara_part:
                            checklist.append(chara_name+part)
                        #exclude part that need to be excluded from checklist
                        for exclude in excludepart:
                            if exclude in checklist:
                                checklist.remove(exclude)
                        if len(chara_name) !=0 and chara_name not in chara_post30_no_orfix_need:                            
                            for checkitem in checklist:
                                #remove name to make checkitem to part list only
                                checkitem=checkitem.replace(chara_name,"")
                                lineNumber = 0
                                if not file.endswith ("merged.ini"):
                                    if not args.ignorechar == True:
                                        if not old_shader_fix == True:
                                            if state == 0:
                                                state = 1
                                            for line in lines:                                    
                                                if line.startswith("[TextureOverride") and checkitem in line and not "FaceHead" in line:
                                                    override = True
                                                    if any (item in line for item in donotneed):
                                                        override = False
                                                    if checkitem == "Head" and ("HatHead"  or "JacketHead" or "HoodDownHead") in line:
                                                        override = False
                                                    if checkitem == "Body" and ("JacketBody") in line:
                                                        override = False
                                                if line == orfix+"\n":
                                                    override = False
                                                if override == True:
                                                    #Make sure that orfix command is not the last run command.
                                                    #This is because merge script only copy last run command, if orfix is last any other command before will not be copy
                                                    if line == "\n" or ("run" in line and not line == orfix) or "drawindexed = " in line:
                                                        lines.insert(lineNumber, orfix + "\n")
                                                        #lines[lineNumber] = "run = CommandList\global\ORFix\ORFix\n\n"
                                                        override = False
                                                        state = 2
                                                lineNumber += 1
                                if file.endswith ("merged.ini"):                                        
                                    if not args.merged:
                                        if file.endswith ("merged.ini"):                                       
                                            for line in lines:  
                                                if line.startswith("[CommandList") and checkitem in line and not "FaceHead" in line:
                                                    override = True
                                                    override_loop = True
                                                    if any (item in line for item in donotneed):
                                                        override = False
                                                        override_loop = False
                                                    if checkitem == "Head" and ("HatHead"  or "JacketHead" or "HoodDownHead") in line:
                                                        override = False
                                                        override_loop = False
                                                    if checkitem == "Body" and ("JacketBody") in line:
                                                        override = False
                                                        override_loop = False
                                                    if chara_name == "Mavuika":
                                                        if checkitem == "Body":
                                                            if "Dress"in line:
                                                                override = False
                                                                override_loop = False
                                                            if "Head"in line: 
                                                                override = False
                                                                override_loop = False                                                               
                                                if override_loop == True:
                                                    if override == True:
                                                        if orfix in line:
                                                            override = False
                                                            if state == 0:
                                                                state = 1 
                                                        if "drawindexed = " in line:
                                                            #lines.insert(lineNumber, "run = CommandList\global\ORFix\ORFix\n")
                                                            state = 2
                                                            override = False
                                                            drawindexed_encounter = True
                                                            ifencounter = True
                                                            if drawindexed_encounter_count == 0:
                                                                lines[lineNumber] = "\t"+orfix+"\n"+lines[lineNumber]
                                                            drawindexed_encounter_count = drawindexed_encounter_count+1

                                                        if "else if" in line or "endif" in line:
                                                            #lines.insert(lineNumber, "run = CommandList\global\ORFix\ORFix\n")
                                                            if drawindexed_encounter == False:
                                                                lines[lineNumber] = "\t"+orfix+"\n"+lines[lineNumber]
                                                            else:
                                                                drawindexed_encounter = False
                                                            drawindexed_encounter_count =0
                                                            state = 2
                                                            override = False
                                                            ifencounter = True
                                                    if override == False:
                                                        if "else if" in line or "endif" in line:
                                                            ifencounter = True
                                                    #turn on override flag to continue override loop
                                                    if ifencounter == True:
                                                        override = True
                                                        ifencounter = False
                                                    #exit override loop if encounter endif
                                                    if "endif" in line:
                                                        override_loop = False
                                                if override_loop == False:
                                                    override = False
                                                lineNumber += 1
                        else:
                            for i, line in enumerate(lines):
                                if (orfix).lower() in line.lower():
                                    lines[i] = ""
                    openFile.close()
                    #Normalizing line from old and new file to compare
                    #if old file is the same as new file, no file will be created
##                    lines_strip = [line.strip() for line in lines if line.strip()]
##                    lines_backup_old_shader_removed = [line.strip() for line in lines_backup_old_shader_removed if line.strip()]
                    lines_normalize = normalize(lines)
                    lines_backup_old_shader_removed_normalize = normalize(lines_backup_old_shader_removed)
##                    for i, (line1, line2) in enumerate(zip(lines_normalize, lines_backup_old_shader_removed_normalize)):
##                        if line1 != line2:
##                            print(f"Difference at line {i+1}:")
##                            print(f"lines: {line1}")
##                            print(f"lines_backup: {line2}")
##                    for i, line1 in enumerate(lines_normalize):
##                         print(f"lines{i}: {line1}")
##                    for i, line2 in enumerate(lines_backup_old_shader_removed_normalize):
##                         print(f"lines{i}: {line2}")
                    if lines_normalize != lines_backup_old_shader_removed_normalize:
                        orfix_applier_changed = True
                    
                    if orfix_applier_changed == True or old_shaderfix_removed_changed == True:
                        ##Create backup file and write new file
                        backup_file = "Backup_ORFIX_Applier_"+file.replace(".ini","")+".txt"
                        with open(os.path.join(r, file), 'w') as file:
                            file.writelines(lines)
                        
                        with open(os.path.join(r, backup_file), 'w') as file:
                            file.writelines(lines_backup)
                            
                        if old_shaderfix_removed_changed == True:
                            print("Old shader fix removed\n")
                        if orfix_applier_changed == True:
                            if have_orfix == 0:
                                print("ORFIX applied\nA backup file is created in .txt format in the same folder as the .ini file\n")
                            else:
                                print("ORFIX was mistakenly applied before but it is correctly applied now.\nA backup file is created in .txt format in the same folder as the .ini file\n")
                        if orfix_applier_changed == False:
                            if have_orfix == 0:
                                print("ORFIX not applied/not needed\n")                            
                            else:
                                print("ORFIX has already been correctly applied before running this script\n")
                    else:
                        if have_orfix == 0:
                            print("ORFIX not applied/not needed\n")                            
                        else:
                            print("ORFIX has already been correctly applied before running this script\n")
                            
                except:
                    print("Something went wrong!")





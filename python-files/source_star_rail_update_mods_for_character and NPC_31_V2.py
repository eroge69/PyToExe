# Made by Sora_
# Thanks to the Genshin Impact Modding Community for their help and support
# Thanks to LeoTorreZ and SilentNightSound, this script is adapted from their script
# Thanks for BladeMouX and Plutoisy, for allowing me to find these hashes in advance
# Special thanks for !someone name has 63B long? help me complete this script

# Fixes for all playable character's body, hair and face, also contain some NPCs and enemy's hashes.
# Note: This fix DOES NOT contain the fixes before 3.0 for older mods, you need to find 3.0 version of them

# ##########################################################################################################################
#     ................                .... ..   ..               ............. ............                              
#     ................                ... ...                    .........................                               
#   ..............            ....                 ..            ........,]`.]............                               
# ................            ......                             ...,/\]/O],*,[\[]........                               
# ............                                           ........,/\@O@/,/\]]],`=`*,=\`...........                       
# .......... .        ..                                 ....../@\@@/`/*`,/\/\[,*,,**=OO]]]........                      
# ............                                        .. ..../O\O@[,,,///`********,*`,]\]*/\`.....                       
# ...........  ...                                    .. .../O@@^*,/\/`*/\***********,**/*/\/.....                       
# ............. .... .                     .  ............][\ooo\O\@^]/ooo`****,*****`*`^`/O@O..... ..                .. 
# ............. .... .                   ............,O\OOO\oo]OOo@`@OO//`***,\\,,``/^,\^,***[\....                      
# ............                            .............,//*,*]/oO^\@ooooo/^*]\]/`\*//**=**`[^*/^...                      
# ............                            ...=]]]]]/[**`*,,*/\o@`O@O/OO\=O/[O\``[/^/``*O]`**,^\\....                     
# ............ ...                       ......,OooooO/@@/o\[//=@o@o//,OOO/\//*/\OO\]`=\^*O]/@@\^..       .. .           
# ............    ..                      ........[@O\oooo\O@/@OOO\///O/\\@^]@\OOO\\\oOO^\@o]OO\^..       .. .           
# .......... .....    ..      .  .       ............/oo/\/,\@O@O@\OO\^]]@@/\,\//`=OO\O@^@O/=\\OO`....        ..         
# ..... ....... ..... .       ....        .........,//O[[]OOOOOO/O/@@@@@@\/]o\OO`=O@\=OO/O/,=/^@@@....        ..         
# ................            .....  .............=\`*`/\OOooO/@/@,O@@@@O^,@\OO*=O@\*oOOOO^=^/@/@,\... ..         .......
# ................            ....        ......,//*,/OOOoO\=/OOo^\\.\O/.../O//\/@\O\@@\OO*@\O=\@..=.....         ....   
# ................                    ........,/,/,//OO\/*,*@oOO\^O@......*O/`.**\@@@^@@@^/\O^**=^........               
# ...,]/\]].....                      .....]\\*/O\@oo\/,`*/@Oo/@o^=^.....,.......@O@`/@@^@/oO`\OO^... .                  
# .,/`@O[*............................,]/^**/@O/OOOO``*,\o@O/\OO/^=\..........[...,.*@O@@OO@,*/=/..                      
# O,[,`\]/[\/OOO\/^[*,\/**,]]]]]]O\Oo\,*,/OO@@oOO`**,*,oO\/*@@@@/o,@\`..............@O@Oo@@`*/./...                      
# \,/[,*`,\//@//oo\O]*,\`..\/**`,Oo/[OOo@O@\O/\//o\,`\//[*//@@@O@o`@^@`.[,......../@\@OO@@*=`......                      
# O/@//\`*/**[\/\OO\@\\`\[\..\][\/@OO\OO^OO/]o/o/o\[/\*,/O/\@@@\O@O@,/@\.`..,]/@@OOO@@o@@/`.......                       
# \/...,,[[\`*,*\\\/O[@.,//*./OOOO@@@OO@Ooo\o\@/\[,*\,OO@oo@@@@@O@@@=@@@@@@@@OO@=@@@OOO\O^.. ... .                       
# .......*``],,``/\O]*/..\\^=\/oOo///\oOOOOO\]`*/`/]OO/oOO\O@@@@@@@@@@@@@@@@@O@@@@O\O@OO=^...     .. .                   
# .../\\\\\=\/O\/[^\`=/...`.@\],/O`**\]`oooooo^O@\oo\@O@OOOOOOOO@@@@/@@@@@@@@@@\OO@@@/\/=.......  ..                     
# ./OooooOO/^/^***/\,/@`....@/`,,*`*`*/]]O/@//ooOOO/@@@@O\OOOOOOOOOOOO@O]\@@@@O@@@@@@OO@OO^......         ....           
# OooO/@\o\/*`******/@O^....@.*`*`***]/@@OOOOOOO/O@@OO\@@@@OOOOOO@@OO@OOOO@@@@@OOO@@@@@O@@O^.......               ....   
# OOO\Oo\/**`**,**\]`@,=^**//\\/\\\`O\oO@/`/@O\@@OOOOOOOO@@@@OOO/@@@@@@@OOO@@@@OOOOO@@@@@@@O\..  .                . ..   
# OOOOO@[,,*`]/Oooooo\Ooo\oo/O`/\@*[,[O@/O\OOO@@OOOOOO@OOOO@@@@OOOOO@@@@@O@@@/@\@@[OOOOO@@@@OO`...         .......       
# OOOo/*`,,@oooo\oooo\//@\oo/O\//,\@OooOOOoo@O@OOOOO@@O@@@@@@@O@OOOOOO@@\\@@OO\OO@@`\/OOO\@@OO@...          . ....       
# OOo@*``/\/[.......,.==@@OO/OO\/\^OO/@\OoO\@@@@@@@@@@@@@@@@@\@@@@@OOO@@@/@@OOOOO@@@@@OOOOOO@OO^...       ....           
# OOOO,,/............^,@@O\@^@O/\//OO@@@@@@@@@@@@@@@@OOO/OOOOOO@O\@OOO@@@@@O]]\]]/O@\OOOOOOOOO@O...         ..           
# =OO/.................@@OO@@@=]oo^OOO@@@@@OOOOOO/OO@O@@@@\OOOOOO@@@@/OOOOOO@@@@@@@@@@@OO@@@@@@@^.                       
# ............,\O`.....,@O@@@OO@/\/OOOOO@@@OOOOOOOOOOOO@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@^.                       
# ............/@^........\/OOOOOO@@O/OOO@@OOOOOOOOOOOOOOOOOO\@O@@@@@@@@@@@@@@@@@@@@@@@@OOOOOO@@@^.                       
# .. ... .....^*,].........\@O/@@@@@@@@@@@@@@@@@@OOOo/O@@@@@@O/o@@@@@@@@@@@@@@@OO@@@@@@@OOOOOOO@^.              ..       
# ............\,***[].......=@@@@@@@@@@@@@@@@@@@@@@@@@@@@@OOOOOoO\@@@@@@@@OO@O@OOOOOOO@@OOOOO@@@^.  ..        ......     
# ... .........\,***,*[`......@oO@@@@@@@@@@@@@@@@@@@@@@\/OOoO/O/`*\@@@@@@@OOOOO@OOOOOOO\\OOOOOO@^..   ...       ..   .   
# ....... .......\\,*``*,[]...,@OO@@@@@@@@@@@@@@@@@@[ooooo@/^*]/O\/\@@@@@OOOO@@@OOOOOOOOOO@OOOOO\..               ....   
# .................,@@]*^,,*``**,\\@@@@@@@@@@@@@/@\oOO[]]/@\oooooooo\@@@@O@OOO@@O@@@OO\OOO@@OOOO@..               ...... 
# ....    ............[@//]]`****]\]/@@@@@@@@@O@OOOooooooooooooOooO@\\/@@@@@@@OO/@@@@@@@@@OOOOOOO\....                   
# ....  .... .... .......,\Oo//[]*^ooooooo\/@@ooOoooooOoooooOoO/`.//ooO\@@@@@@@/O@OO/@@@@@@@/OOOOO^...                   
# .. ...  ....    ..   ......[\[`/=/oooooOooooooooOOOoo/OO[`...,/Ooo\\/./@@@@@@@@@OOOO\\@@@@@@@O@@@.....                 
# ......  ....           ........[\O/[[[[[OO[[[[[\O/[`.......,O/\ooO`..=OO@@@@@@@@@OOOOOOOO@\@OO@@@@.... .               
# ....    ....           .........,/\\......................///O/`......=@@@@@@@@@@OOOOOOOOOO@OO\@@@^.....               
# ....       .            .........*=....................,[///`.........=@@@@@@@@@@OOOOOOOOOOO@O@@@@@.....               
# ...... .                  ..   ...\\................,/][`.......... ..@@@@@@@@@@@@OOOOO@@@O\@@@@@@@@....               
# ........                        ....\`.........]/OO[`.......  .......=@@@@@@@@@@@@@@@O@@@@@@@@@@@@@@^...               
# . .... .... ....              ...........[`.............      .......@@@@@@@/OOO@@@@@@@@@@@@@@/@@@O@@^..               
#   ......... ...             .   ..... ..................        ...,/@@@@@@@OOOOO/@@@@@@@OOO@@@@@OOOO@`.               
#   ........  ....                    .    ......   ................/@@@@@@@@@@OOO@OOO@@@@@OOOOO@@@OOOOO@.........       
# .   .....   ....                        .. ..  .         .. ..../@@@@@@@@@@@@@@O@@@@@@@@@@@@/O/@@OOOOOOO/`.... ..      
#    ...    ..           .                                ....../OOO@@@@@@@@@@@@@O@@@@@@@@@@@@@@@=@@OOOO\/O/\.....       
#    .... .           ....                               ...../@OOOOOO@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@OOOO\//O\\.....      
# ........        ...... .                .           ....../@OOOOOOOO@@@@@@@@@@@@@@@@@@OoO@@@@@@@OOOOOOO/o`@]O....      
# ........        .....                   ...         .....,@OOOOOO@@@@@O@=]/[[[@@@@@@@@@OOOOOOO@@OOOOOOOOo/o///`...     
# ..  ...   ..                                    .....,/@@@@@OOO@@@@@@@@\oooooooooooo/o]\\\]]/@@@@OOOOOOO/]@[O`......   
# ##########################################################################################################################

import os
import struct
import argparse
import shutil

old_vs_new = {
    # Acheron
    "7212e8c5":"9de39691",
    "bc9d2d77":"a52830c5",
    # Acheronhair
    "9745dc50":"8ef0c1e2",
    "ee6055e3":"01912bb7",
    "567105bf":"4fc4180d",
    "e4645cb9":"0b9522ed",
    # Acheronface
    "896ef2ee":"90dbef5c",
    "f8b9e830":"17489664",
    # Aglaea
    "0f0feeb5":"e0fe90e1",
    # Aglaeahair
    "f79bf55c":"ee2ee8ee",
    "88964833":"67673667",
    # Aglaeaface
    "8124d93b":"6ed5a76f",
    # Argenti
    "3f920a7c":"d0637428",
    # Argentihair
    "78c72ec8":"6172337a",
    "cc1a18f7":"23eb66a3",
    # Argentiface
    "13e52094":"0a503d26",
    "e0caccfa":"0f3bb2ae",
    # Arlan
    "aa7d97fd":"458ce9a9",
    # Arlanhair
    "6aee5919":"735b44ab",
    "b9ac47a5":"565d39f1",
    # Arlanface
    "25060ff7":"3cb31245",
    "642d3ecb":"8bdc409f",
    # Asta
    "f65d0287":"19ac7cd3",
    # Astahair
    "967c0759":"8fc91aeb",
    "a6d492d3":"4925ec87",
    # Astaface
    "6f2e00c4":"769b1d76",
    "8fd302a3":"60227cf7",
    # Aventurine
    "8e11bb4f":"61e0c51b",
    # Aventurinehair
    "8de65cb9":"9453410b",
    "dbef38cc":"341e4698",
    # Aventurineface
    "ad82dc30":"b437c182",
    "d6703a6e":"3981443a",
    # Bailu
    "96a4a724":"7955d970",
    "e2fb7ce0":"fb4e6152",
    # Bailuhair
    "1779da3f":"0eccc78d",
    "68cef846":"873f8612",
    # Bailuface
    "0ae19e5d":"135483ef",
    "15a034fc":"fa514aa8",
    # BlackSwan
    "b4ec029d":"5b1d7cc9",
    "10fb3cab":"094e2119",
    # BlackSwanhair
    "dc153ce0":"c5a02152",
    "0d8672ce":"e2770c9a",
    # BlackSwanface
    "33edc9b2":"2a58d400",
    "ede8abb0":"0219d5e4",
    # Blade
    "4cc66b74":"a3371520",
    # Bladehair
    "dd309961":"c48584d3",
    "aab6366e":"4547483a",
    # Bladeface
    "90237dd2":"89966060",
    "2bc042b8":"c4313cec",
    # Boothill
    "5183fce7":"be7282b3",
    "bd451832":"86707f18",
    "f36e4a49":"6226eb4c",
    # Boothillhair
    "d164f7fd":"c8d1ea4f",
    "add5290e":"4224575a",
    # Boothillface
    "80a5d96e":"9910c4dc",
    "e495cc7d":"0b64b229",
    # Bronya
    "09c90e7f":"e638702b",
    "90a94c09":"4d61fb3a",
    # Bronyahair
    "4265a087":"5bd0bd35",
    "cd417d46":"22b00312",
    # Bronyaface
    "9718281f":"8ead35ad",
    "314fb3a3":"debecdf7",
    # Caelus
    "2baba62a":"c45ad87e",
    # Caelushair
    "870564f1":"9eb07943",
    "6786de68":"8877a03c",
    # Caelusface
    "87f2f3ce":"9e47ee7c",
    # Castorice
    "aa594182":"45a83fd6",
    # Castoricehair
    "fb3eae6f":"e28bb3dd",
    "6b52f38e":"776a0dad",
    "40c9c4e2":"e2ce4067",
    # Castoriceface
    "f1e7fb1f":"e852e6ad",
    "081b6cb4":"e7ea12e0",
    # Clara
    "89e485a2":"6615fbf6",
    # Clarahair
    "486f6900":"51da74b2",
    "d7130c52":"38e27206",
    # Claraface
    "d252d8ba":"cbe7c508",
    "01c3ad70":"ee32d324",
    # DanHeng
    "b7594abd":"58a834e9",
    # DanHenghair
    "b591da57":"ac24c7e5",
    "031da129":"ececdf7d",
    # DanHengface
    "8ed66c8a":"97637138",
    "5bfc6e67":"b40d1033",
    # DrRatio
    "ec519551":"03a0eb05",
    # DrRatiohair
    "7a9d0dac":"6328101e",
    "7d37a021":"92c6de75",
    # DrRatioface
    "b88dc8c6":"a138d574",
    "6e1dc670":"81ecb824",
    # Feixiao
    "704530bd":"9fb44ee9",
    # Feixiaohair
    "33418ff8":"2af4924a",
    "b5994a59":"5a68340d",
    # Feixiaoface
    "fbd97f64":"e26c62d6",
    "3e6aa1cc":"d19bdf98",
    # Firefly
    "681937c7":"87e84993",
    # Fireflyhair
    "d0ebca93":"c95ed721",
    "7981904e":"9670ee1a",
    # Fireflyface
    "60fa9067":"794f8dd5",
    "b5ca90ce":"5a3bee9a",
    # Fugue
    "94f94174":"7b083f20",
    # Fuguehair
    "869bd4b2":"9f2ec900",
    "5332f9ed":"bcc387b9",
    # Fugueface
    "9963bd2c":"80d6a09e",
    "6d651fcc":"82946198",
    # Fuguetail
    "e0a23cff":"f917214d",
    "04d0f9a0":"eb2187f4",
    # FuXuan
    "3f5bd667":"d0aaa833",
    # FuXuanhair
    "5f23a159":"4696bceb",
    "8f1c057c":"60ed7b28",
    # FuXuanface
    "f8d8d92e":"e16dc49c",
    "b11ec441":"5eefba15",
    # Gallagher
    "b8346c8b":"57c512df",
    # Gallagherhair
    "b0198c11":"a9ac91a3",
    "d9d4ed61":"36259335",
    # Gallagherface
    "ac642ccc":"b5d1317e",
    "0a7424b1":"e5855ae5",
    # Gepard
    "9875df96":"7784a1c2",
    # Gepardhair
    "26734c62":"3fc651d0",
    "ff3a4705":"10cb3951",
    # Gepardface
    "19c9ccc9":"007cd17b",
    "37f39435":"d802ea61",
    # Guinaifen
    "93f9c6fc":"7c08b8a8",
    "506edd10":"637ad2db",
    # Guinaifenhair
    "1b4cc6bb":"02f9db09",
    "7e75c06e":"9184be3a",
    # Guinaifenface
    "735df382":"6ae8ee30",
    "3753bbee":"d8a2c5ba",
    # Hanya
    "208022e7":"cf715cb3",
    # Hanyahair
    "10952bd7":"09203665",
    "a15c444f":"4ead3a1b",
    # Hanyaface
    "adf8b2de":"b44daf6c",
    "5311cf0a":"bce0b15e",
    # Herta
    "383d8083":"d7ccfed7",
    # Hertahair
    "2d748a84":"34c19736",
    "40ff8968":"af0ef73c",
    # Hertaface
    "93d98b8b":"8a6c9639",
    "c1948160":"2e65ff34",
    # Himeko
    "947bc57e":"7b8abb2a",
    "5212e2f9":"4ba7ff4b",
    # Himekohair
    "a8f00e3a":"b1451388",
    "71a1c8eb":"9e50b6bf",
    # Himekoface
    "9ca6e275":"8513ffc7",
    "88093f50":"67f84104",
    # Hook
    "9d68704b":"84dd6df9",
    "cf732951":"20825705",
    # Hookhair
    "2c0285e5":"35b79857",
    "516052b3":"be912ce7",
    # Hookface
    "7d70c461":"64c5d9d3",
    "0a410eec":"e5b070b8",
    # Huohuo
    "a1b1aafa":"4e40d4ae",
    # Huohuohair
    "21b42643":"38013bf1",
    "6a7c7d6d":"858d0339",
    # Huohuoface
    "7c8be987":"653ef435",
    "c9bc7a6e":"264d043a",
    # Jade
    "e7048976":"08f5f722",
    # Jadehair
    "e62b239a":"ff9e3e28",
    "93ba2c04":"7c4b5250",
    # Jadeface
    "4c0adcc6":"55bfc174",
    "7076a247":"9f87dc13",
    # Jiaoqiu
    "aaa5a0ff":"4554deab",
    # Jiaoqiuhair
    "667ba145":"7fcebcf7",
    "1cf0d06c":"f301ae38",
    # Jiaoqiuface
    "4c754f6c":"55c052de",
    "91c5de25":"7e34a071",
    # JingYuan
    "cc58b451":"23a9ca05",
    # JingYuanhair
    "31319f5f":"288482ed",
    "e1d746fc":"0e2638a8",
    # JingYuanface
    "9d60acea":"84d5b158",
    "61d571f5":"8e240fa1",
    # Jingliu
    "cb320050":"24c37e04",
    # Jingliuhair
    "35f278be":"2c47650c",
    "ae0df48a":"41fc8ade",
    # Jingliuface
    "6f96493b":"76235489",
    "ecf0b54f":"0301cb1b",
    # Jingliumask
    "11a90c69":"081c11db",
    "7fb40d9c":"3c4256b0",
    # Kafka
    "4babbbd9":"a45ac58d",
    "cd2222f8":"d4973f4a",
    # Kafkahair
    "cdda77a3":"d46f6a11",
    "91133916":"7ee24742",
    # Kafkaface
    "7cbe836d":"650b9edf",
    "e811b655":"07e0c801",
    # Lingsha
    "ea4c4532":"05bd3b66",
    # Lingshahair
    "c207a096":"dbb2bd24",
    "bc787aec":"538904b8",
    # Lingshaface
    "e779f220":"feccef92",
    "dc9cba18":"336dc44c",
    # Luka
    "3fe3d055":"d012ae01",
    # Lukahair
    "a96bca86":"b0ded734",
    "e98c3d24":"067d4370",
    # Lukaface
    "222b9650":"3b9e8be2",
    "614df023":"8ebc8e77",
    # Lunae
    "9cbdcefd":"734cb0a9",
    # Lunaehair
    "09d4edc5":"1061f077",
    "97be0a41":"784f7415",
    # Lunaeface
    "c7751dba":"dec00008",
    "4616d1e7":"a9e7afb3",
    # Luocha
    "0a1b224a":"e5ea5c1e",
    # Luochahair
    "2f7b8290":"36ce9f22",
    "5484d0a4":"bb75aef0",
    # Luochaface
    "d5f4ef26":"cc41f294",
    "02962a1d":"ed675449",
    # Lynx
    "fa9c73b8":"156d0dec",
    # Lynxhair
    "7ab99fa3":"630c8211",
    "195d3f53":"f6ac4107",
    # Lynxface
    "b636d476":"af83c9c4",
    "de5813fa":"31a96dae",
    # March7th
    "baaeaaf0":"555fd4a4",
    # March7thhair
    "09903e8e":"1025233c",
    "749c6d11":"9b6d1345",
    # March7thface
    "b23869e0":"ab8d7452",
    "694f577b":"86be292f",
    # March7thSkin
    "472e6131":"a8df1f65",
    # March7thSkinhair
    "09903e8e":"1025233c",
    "749c6d11":"9b6d1345",
    # March7thTheHunt
    "712bac55":"9edad201",
    # March7thTheHunthair
    "411425d0":"58a13862",
    "6f468e3f":"80b7f06b",
    # Misha
    "7cbca09c":"934ddec8",
    # Mishahair
    "af206cba":"b6957108",
    "3ae2fc69":"d513823d",
    # Mishaface
    "be8ee647":"a73bfbf5",
    "999dff73":"766c8127",
    # Moze
    "86630c6b":"6992723f",
    # Mozehair
    "c88fe0e7":"d13afd55",
    "49534d8c":"a6a233d8",
    # Mozeface
    "48ddd366":"5168ced4",
    "07f88cc9":"e809f29d",
    # Mydei
    "caf79f9b":"2506e1cf",
    # Mydeihair
    "aa0733d3":"b3b22e61",
    "403a12dd":"afcb6c89",
    "c0a7cb23":"5eab2525",
    "84eb69d9":"6b307cf7",
    # Mydeiface
    "7243533d":"9db22d69",
    # Natasha
    "23c6f5ac":"cc378bf8",
    "f795f7c5":"ee20ea77",
    "4958a3f3":"50edbe41",
    # Natashahair
    "29539b93":"30e68621",
    "38e692c7":"d717ec93",
    # Natashaface
    "4a197424":"53ac6996",
    "94322ac5":"7bc35491",
    # Natashapotion
    "f795f7c5":"ee20ea77",
    "425deed9":"01abb5f5",
    # Pela
    "b889667f":"5778182b",
    # Pelahair
    "fd24333c":"e4912e8e",
    "4b1780bb":"a4e6feef",
    # Pelaface
    "db053da4":"c2b02016",
    "53070a34":"bcf67460",
    # Qingque
    "109719da":"ff66678e",
    # Qingquehair
    "926cd87e":"8bd9c5cc",
    "1efcf666":"f10d8832",
    # Qingqueface
    "968fce83":"8f3ad331",
    "8c6fc97d":"639eb729",
    # Rappa
    "929ed561":"7d6fab35",
    # Rappahair
    "d5d249db":"cc675469",
    "16da2868":"f92b563c",
    # Rappaface
    "19526add":"00e7776f",
    "be6516d2":"51946886",
    # Robin
    "22e9e92a":"3b5cf498",
    "94a0e452":"7b519a06",
    # Robinhair
    "c659dc72":"dfecc1c0",
    "022d66fa":"eddc18ae",
    # Robinface
    "4eb1753f":"5704688d",
    "68e89a79":"8719e42d",
    # RuanMei
    "2d3d915a":"c2ccef0e",
    "7e4f7890":"67fa6522",
    # RuanMeihair
    "7ed84bde":"676d566c",
    "3b0cb896":"d4fdc6c2",
    # RuanMeiface
    "5a981b24":"432d0696",
    "490a691b":"a6fb174f",
    # Sampo
    "b9371b3c":"56c66568",
    # Sampohair
    "3095786c":"292065de",
    "d4ab62d7":"3b5a1c83",
    # Sampoface
    "3b4bdc1f":"22fec1ad",
    "f3f0c980":"1c01b7d4",
    # Seele
    "8a952009":"65645e5d",
    # Seelehair
    "0eec1b57":"175906e5",
    "a9013cae":"46f042fa",
    # Seeleface
    "e1a2635f":"f8177eed",
    "e9ffad95":"060ed3c1",
    # Serval
    "ab709ef7":"4481e0a3",
    # Servalhair
    "591d16e1":"40a80b53",
    "5bca39c4":"b43b4790",
    # Servalface
    "2de93d4b":"345c20f9",
    "876b2a8c":"689a54d8",
    # SilverWolf
    "17906457":"f8611a03",
    # SilverWolfhair
    "520314e4":"4bb60956",
    "567d08be":"b98c76ea",
    # SilverWolfface
    "314115a3":"28f40811",
    "2cf46858":"c305160c",
    # Sparkle
    "91b9fb51":"7e488505",
    # Sparklebubble
    "b1be2710":"a80b3aa2",
    "0385188d":"407343a1",
    # Sparklehair
    "5b9af3ba":"422fee08",
    "4e477254":"a1b60c00",
    # Sparkleface
    "c2cce86e":"db79f5dc",
    "4873b590":"a782cbc4",
    # Stelle
    "5aadfa65":"b55c8431",
    # Stellehair
    "8c0c078f":"95b91a3d",
    "46ed784a":"a91c061e",
    # Stelleface
    "00658faa":"19d09218",
    "45a18e05":"aa50f051",
    # Sunday
    "c5c1150d":"2a306b59",
    # Sundayhair
    "ca09a4f1":"d3bcb943",
    "f74c7344":"18bd0d10",
    # Sundayface
    "0fc6e4fe":"1673f94c",
    # Sushang
    "f30f2d7f":"1cfe532b",
    # Sushanghair
    "c87cf153":"d1c9ece1",
    "38293906":"d7d84752",
    # Sushangface
    "ad69421b":"b4dc5fa9",
    "d0568383":"3fa7fdd7",
    # TheHerta
    "54d8694d":"bb291719",
    # TheHertahair
    "79daebcd":"606ff67f",
    "9be881fe":"7419ffaa",
    # TheHertaface
    "cdc9515a":"22382f0e",
    # Tingyun
    "069ee84c":"e96f9618",
    # Tingyunhair
    "be07554f":"a7b248fd",
    "44cee658":"ab3f980c",
    # Tingyunface
    "f9fa713f":"e04f6c8d",
    "ff6fdae4":"109ea4b0",
    # Topaz
    "55ef95d4":"ba1eeb80",
    # Topazhair
    "a413be23":"bda6a391",
    "cbd71321":"24266d75",
    # Topazface
    "e0b28d05":"f90790b7",
    "78012798":"97f059cc",
    # Tribbie
    "1663ad11":"f992d345",
    # Tribbiehair
    "fe4495a6":"e7f18814",
    "7dd3bc06":"9222c252",
    # Tribbieface
    "caf6b434":"2507ca60",
    # Welt
    "aa4229a3":"45b357f7",
    # Welthair
    "c13c202e":"d8893d9c",
    "34e99315":"db18ed41",
    # Weltface
    "8cad004f":"95181dfd",
    "0aafd819":"e55ea64d",
    # Xueyi
    "9127a7b3":"7ed6d9e7",
    "8936451b":"908358a9",
    # Xueyihair
    "5ad7108a":"43620d38",
    "e0f8ce61":"0f09b035",
    # Xueyiface
    "acec2843":"b55935f1",
    "4aab3325":"a55a4d71",
    # Yanqing
    "40828c6c":"af73f238",
    # Yanqinghair
    "a2ee2b45":"bb5b36f7",
    "628a3954":"8d7b4700",
    # Yanqingface
    "5bc1537b":"42744ec9",
    "34eb9f8c":"db1ae1d8",
    # Yukong
    "0d24ec87":"e2d592d3",
    # Yukonghair
    "96478ccb":"8ff29179",
    "3219c61a":"dde8b84e",
    # Yukongface
    "1c4be428":"05fef99a",
    "e539f4ce":"0ac88a9a",
    # Yunli
    "2ab1d1bd":"c540afe9",
    # Yunlihair
    "6c60e749":"75d5fafb",
    "22a4c645":"cd55b811",
    # Yunliface
    "44a7e483":"5d12f931",
    "be092ccf":"51f8529b",
    ## other hash
    # AmphoreusLoliNPC-1
    "dda35578":"c41648ca",
    "e9d817e8":"062969bc",
    # AmphoreusLoliNPC-2
    "8287eb6e":"9b32f6dc",
    "f8152c40":"17e45214",
    # AmphoreusLoliNPC-3
    "5e7a6aad":"47cf771f",
    "bda9c73f":"5258b96b",
    # AmphoreusNPC1-1
    "af18050f":"b6ad18bd",
    "abd8978e":"4429e9da",
    # AmphoreusNPC1-2
    "c487e3ef":"dd32fe5d",
    "7bd8bb12":"9429c546",
    # AmphoreusNPC1-3
    "667bbd6f":"7fcea0dd",
    "e553e2c7":"0aa29c93",
    # AmphoreusNPC2-1
    "2af3a2df":"d039e386",
    "d95a13b5":"5b958520",
    "3a57ca1e":"b0f43db2",
    "05bd6e65":"473e01f2",
    "f7836426":"7b955957",
    # AmphoreusNPC2-2
    "38186b93":"6205432d",
    "527c39d7":"27bf8ebf",
    "f942391e":"7abd2d8f",
    "3d12735a":"b10b2e91",
    "da48c709":"a23ddb70",
    # AmphoreusNPC2-3
    "4054a3fe":"7549a8b8",
    "960e77ad":"2f74813a",
    "2c263e6c":"ed4c8417",
    "46f3ff5f":"938a531f",
    "b2206637":"2c760e0b",
    # AmphoreusNPC3-1
    "c71aa0e9":"deafbd5b",
    "0d459ac9":"e2b4e49d",
    # AmphoreusNPC3-2
    "e752099b":"fee71429",
    "3747e5ed":"d8b69bb9",
    # AmphoreusNPC3-3
    "cdd6cd01":"d463d0b3",
    "4846e3fa":"a7b79dae",
    # AmphoreusNPC4-1
    "b263bc44":"abd6a1f6",
    "34e69a64":"db17e430",
    # AmphoreusNPC4-2
    "d2d88f62":"cb6d92d0",
    "f1f30cf3":"1e0272a7",
    # AmphoreusNPC4-3
    "7a26f186":"6393ec34",
    "a55c5aaf":"4aad24fb",
    # AmphoreusNPC5-1
    "b1f10cd5":"a8441167",
    "6de96e6e":"8218103a",
    # AmphoreusNPC5-2
    "8898dbb9":"912dc60b",
    "512b60d1":"beda1e85",
    # AmphoreusNPC5-3
    "3f55afb2":"26e0b200",
    "75bec472":"9a4fba26",
    # AurumatonSpectralEnvoy
    "1f5654c4":"06e34976",
    "f61e2627":"19ef5873",
    # Chords
    "93b253e7":"8a074e55",
    "157d3961":"fa8c4735",
    # CocoliaMD
    "ef07afd2":"f6b2b260",
    "b06e7593":"5f9f0bc7",
    # CompanyEmployee
    "80429718":"99f78aaa",
    "89743b50":"66854504",
    # DecayingShadow
    "49f9d1e5":"504ccc57",
    "9cce1165":"733f6f31",
    # DestructObj-Amphoreus
    "e94f5824":"f0fa4596",
    "a3fdf5fe":"e00baed2",
    # DestructObj-HertaSpaceStation
    "4f07ac05":"56b2b1b7",
    "a46c436b":"e79a1847",
    # DestructObj-Jarilo-VI
    "759fa196":"6c2abc24",
    "845a071f":"c7ac5c33",
    # DestructObj-Luofu
    "07814a7e":"1e3457cc",
    "ef66faaa":"ac90a186",
    # DestructObj2-Amphoreus
    "cc00c3a7":"d5b5de15",
    "a0f13cc1":"e30767ed",
    # DestructObj2-HertaSpaceStation
    "2e051c5d":"37b001ef",
    "9a134c5c":"d9e51770",
    # DestructObjTech-Amphoreus
    "f0880cff":"e93d114d",
    "b15f1f0a":"f2a94426",
    # DestructObjTech-HertaSpaceStation
    "28365225":"31834f97",
    "4ccac05b":"0f3c9b77",
    # DestructObjTech-Jarilo-VI
    "f9f9c6d6":"e04cdb64",
    "1641072e":"55b75c02",
    # DestructObjTech-Luofu
    "0e471e54":"17f203e6",
    "2fbe1332":"6c48481e",
    # Garmentmaker
    "484b5014":"51fe4da6",
    "31d815ee":"de296bba",
    # GarmentmakerSword
    "df444c4c":"c6f151fe",
    "13483937":"fcb94763",
    # GuardianShadow
    "4e8967f8":"573c7a4a",
    "8f549559":"60a5eb0d",
    # HertaSpaceStationLoliNPC-1
    "181dc042":"01a8ddf0",
    "24a44dd9":"cb55338d",
    # HertaSpaceStationLoliNPC-2
    "e5328f4c":"fc8792fe",
    "6e1dccfd":"81ecb2a9",
    # HertaSpaceStationLoliNPC-3
    "96f5d1cf":"8f40cc7d",
    "a080f5ba":"4f718bee",
    # HertaSpaceStationNPC1-1
    "6a5b23b0":"73ee3e02",
    "f3147d2f":"1ce5037b",
    # HertaSpaceStationNPC1-2
    "796716a5":"60d20b17",
    "c5334397":"2ac23dc3",
    # HertaSpaceStationNPC1-3
    "ba600701":"a3d51ab3",
    "303e84b6":"dfcffae2",
    # HertaSpaceStationNPC2-1
    "fb858acf":"e230977d",
    "d7a04dcf":"3851339b",
    # HertaSpaceStationNPC2-2
    "22b0ae41":"3b05b3f3",
    "9b16dd34":"74e7a360",
    # HertaSpaceStationNPC2-3
    "84e7c2ad":"9d52df1f",
    "a186a3f3":"4e77dda7",
    # HertaSpaceStationNPC3-1
    "3cc75b26":"25724694",
    "41ffe904":"ae0e9750",
    # HertaSpaceStationNPC3-2
    "5b76a8e4":"42c3b556",
    "78e0e741":"97119915",
    # HertaSpaceStationNPC3-3
    "dff98b92":"c64c9620",
    "c7d28178":"2823ff2c",
    # Jarilo-VILoliNPC-1
    "4ec4ff4a":"5771e2f8",
    "469555d4":"a9642b80",
    # Jarilo-VILoliNPC-2
    "839fb43d":"9a2aa98f",
    "03f7cc0c":"ec06b258",
    # Jarilo-VILoliNPC-3
    "3a2a38ec":"239f255e",
    "0dc8b8b1":"e239c6e5",
    # Jarilo-VINPC1-1
    "17b8acfd":"0e0db14f",
    "dee2cb8f":"3113b5db",
    # Jarilo-VINPC1-2
    "cb0e6b81":"d2bb7633",
    "f61407ea":"19e579be",
    "f391ee20":"40737fdd",
    # Jarilo-VINPC1-3
    "267ee4a0":"3fcbf912",
    "2bef9f4d":"c41ee119",
    # Jarilo-VINPC2-1
    "051dec78":"1ca8f1ca",
    "18b574c0":"f7440a94",
    # Jarilo-VINPC2-2
    "5685e826":"4f30f594",
    "4b791087":"a4886ed3",
    # Jarilo-VINPC2-3
    "9e2ed0a2":"879bcd10",
    "00f5d9a1":"ef04a7f5",
    # Jarilo-VINPC3-1
    "78d8b9e7":"616da455",
    "05a7b795":"ea56c9c1",
    # Jarilo-VINPC3-2
    "0fe45c8c":"1651413e",
    "731e330f":"9cef4d5b",
    # Jarilo-VINPC3-3
    "639b96a6":"7a2e8b14",
    "4a097720":"a5f80974",
    # LuofuLoliNPC-1
    "3fc8d61e":"267dcbac",
    "0aef4192":"e51e3fc6",
    # LuofuLoliNPC-2
    "0f37b1b2":"1682ac00",
    "b27ef4d9":"5d8f8a8d",
    # LuofuLoliNPC-3
    "2e3cadac":"3789b01e",
    "ee06a355":"01f7dd01",
    # LuofuNPC1-1
    "08f85552":"114d48e0",
    "08600875":"e7917621",
    # LuofuNPC1-2
    "dfac1dae":"c619001c",
    "38870c9d":"d77672c9",
    # LuofuNPC1-3
    "ae3604aa":"b7831918",
    "91122253":"7ee35c07",
    # LuofuNPC2-1
    "99c4cd87":"8071d035",
    "d58cd44b":"3a7daa1f",
    # LuofuNPC2-2
    "23c4f7e1":"3a71ea53",
    "3bb80caf":"d44972fb",
    # LuofuNPC2-3
    "fa6f2140":"e3da3cf2",
    "a788062f":"4879787b",
    # LuofuNPC3-1
    "888b8d61":"913e90d3",
    "35d73a8d":"da2644d9",
    # LuofuNPC3-2
    "f1a27cb3":"e8176101",
    "252d24d2":"cadc5a86",
    # LuofuNPC3-3
    "56313ed8":"e3da3cf2",
    "71504f62":"4879787b",
    "790b7013":"d6a8c091",
    # Mara-StruckWarden
    "7e427e16":"67f763a4",
    "eac4ead3":"05359487",
    # Messenger
    "8db73e2a":"94022398",
    "258b5a81":"ca7a24d5",
    # Past
    "6c61253f":"75d4388d",
    "b9c70ad2":"56367486",
    # PenaconyLoliNPC-1
    "588d2d50":"413830e2",
    "0ac48257":"e535fc03",
    # PenaconyLoliNPC-2
    "4c350a3d":"5580178f",
    "b6d18831":"5920f665",
    # PenaconyLoliNPC-3
    "d87f36f5":"c1ca2b47",
    "1a4e3624":"f5bf4870",
    # PenaconyNPC1-1
    "df0fd15c":"c6baccee",
    "d9f69a39":"3607e46d",
    # PenaconyNPC1-2
    "77505e42":"6ee543f0",
    "2614a98d":"c9e5d7d9",
    # PenaconyNPC1-3
    "4362ba7e":"5ad7a7cc",
    "e30281de":"0cf3ff8a",
    # PenaconyNPC2-1
    "b62379c1":"af966473",
    "5c1fdf60":"b3eea134",
    # PenaconyNPC2-2
    "373d10bf":"2e880d0d",
    "f6fe3359":"190f4d0d",
    # PenaconyNPC2-3
    "8b209de2":"92958050",
    "b467336d":"5b964d39",
    # PenaconyNPC3-1
    "8cd12bf9":"9564364b",
    "61a07507":"8e510b53",
    # PenaconyNPC3-2
    "39ca48a0":"207f5512",
    "88a29256":"6753ec02",
    # PenaconyNPC3-3
    "da18ef05":"c3adf2b7",
    "323c8898":"ddcdf6cc",
    # Sam
    "6799671e":"7e2c7aac",
    "20f1a341":"cf00dd15",
    "bb844ba7":"e1446be0",
    # Siobhan
    "e7b4d744":"fe01caf6",
    "41b400fe":"ae457eaa",
    "91aec744":"334192b1",
    "f7e9b490":"6a4133f4",
    "0a345e81":"a55fda83",
    "74ed7efc":"15313587",
    "e1c07b3c":"c0f69713",
    "812273c7":"98b4fa51",
    "4e17629f":"8493de99",
    "3ac64e77":"6ad3a6f8",
    "f2362641":"ecaf7432",
    "00298224":"6916750a",
    # SpaceAnchor
    "2b8e11df":"323b0c6d",
    "837da7fe":"c08bfcd2",
    # Titankin
    "d3f9d51f":"ca4cc8ad",
    "c365ae0b":"2c94d05f",
    # WraithWarden
    "fb82ffbc":"e237e20e",
    "d2d4f52a":"3d258b7e",
    # ascended
    "e7ed8a5a":"fe5897e8",
    "88273782":"67d649d6",
    # cuanGaiZhe
    "07c849d7":"1e7d5465",
    "8b0fbf16":"64fec142",
    # duoLueZhe
    "d4d3a4aa":"cd66b918",
    "d7e8dab8":"3819a4ec",
    # jingwei
    "9e4fb633":"87faab81",
    "253b0ea5":"caca70f1",
    # liulangzhe
    "6c9875d4":"752d6866",
    "58637f0b":"b792015f",
    # Mem
    "7c5713d5":"65e20e67",
    "ff9789b2":"1066f7e6",
    # moXiaoZhe
    "606fbb39":"79daa68b",
    "40393e28":"afc8407c",
    # yunqixunfang
    "9863bd15":"81d6a0a7",
    "d21fd2f9":"3deeacad",
}

replacement_mapping = {
    # sora
    "sora_abcd": {
        "sora_abcd":"sora_abcd",
    },
}

def process_folder(folder_path):
    '''Process all the files in the folder and subfolders,
    replacing the old values with the new ones.'''
    for root, dirs, files in os.walk(folder_path):
        for file in [x for x in files if x.lower().endswith('.ini') and x.lower() != 'desktop.ini']:
            file_path = os.path.join(root, file)
            print(f"--> Get in file '{file}' at '{file_path}'")
            try:
                with open(file_path, 'r', encoding="utf-8") as f:
                    s = f.read()
                    # old_stream = s
                if '[disabled1234567890]' in s:
                    print(f"Skipping file '{file}' as it already contains '[disabled1234567890]'")
                    continue
                modified = False
                for old, new in old_vs_new.items():
                    if old in s:
                        s = s.replace(old, new)
                        print(f" -  Hash '{old}' has been replase with '{new}'")
                        modified = True
                
                for key, values in replacement_mapping.items():
                    if key in s:
                        for search_string, replace_string in values.items():
                            if search_string not in s:
                                print(f" -  Not contain the specified string '{search_string}'. Skipping current string")
                                continue
                            else:
                                modified = True
                                if callable(replace_string):
                                    strr = replace_string(key)
                                    s += f'\n\n{strr}'
                                    print(f' -  {search_string[:4]}...{search_string[-4:]} --> {strr[:4]}...{strr[-4:]}')
                                else:
                                    s = s.replace(search_string, replace_string)
                                    print(f' -  {search_string[:4]}...{search_string[-4:]} --> {replace_string[:4]}...{replace_string[-4:]}')
                    else:
                        print(f" -  key '{key}' not in")
                if modified:
                    backup_file_path = os.path.join(root, f"backup_{os.path.splitext(file)[0]}.txt")
                    shutil.copy2(file_path, backup_file_path)
                    print(f" -  Backup created: '{backup_file_path}'")
                    with open(file_path, 'w', encoding="utf-8") as f:
                        f.write(s)
                        print(f'<-- File has been modified!')
                else:
                    print(f'<-- File had no matches. Skipping')
            except Exception as e:
                print(f'Error processing file: {file_path}')
                print(e)
                continue

if __name__ == '__main__':
    process_folder(os.getcwd())
    input('Done!')

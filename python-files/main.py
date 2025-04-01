from email import policy
from email.parser import BytesParser
from email.parser import Parser
from email import message_from_file
import sys
import os
import os.path
from collections import defaultdict
import shutil

def meta(eml_file, count):
    with open(eml_file, 'rb') as fp:
        msg = BytesParser(policy=policy.default).parse(fp)
    with open(eml_file) as fp:
        msg_text = message_from_file(fp)
        
    text = msg_text.get_payload()[0]
    eml_file = os.path.basename(eml_file)
    dir_name = count + "." + str(os.path.splitext(eml_file)[0])
    with open(dir_name + "/" + eml_file + ".html", 'w') as f:
        f.write(str(text) + "<br /><br /><br />" + 
        'To:' + str(msg['to']).replace("<", "- ").replace(">", "") + "<br />" + 
        'From:' + str(msg['from']).replace("<", "- ").replace(">", "") + "<br />" +
        'Date:' + msg['date'] + "<br />" +
        'Subject:' + msg['subject'] + "<br />"
        )

def parse_message(eml_file):
    with open(eml_file) as f:
        return Parser().parse(f)

def find_attachments(message):
    found = []
    for part in message.walk():
        if 'content-disposition' not in part:
            continue
        cdisp = part['content-disposition'].split(';')
        cdisp = [x.strip() for x in cdisp]
        if cdisp[0].lower() != 'attachment':
            continue
        parsed = {}
        for kv in cdisp[1:]:
            key, val = kv.split('=', 1)
            if val.startswith('"'):
                val = val.strip('"')
            elif val.startswith("'"):
                val = val.strip("'")
            parsed[key] = val
        found.append((parsed, part))
    return found

def run(eml_filename, count):
    dir_name = os.path.basename(eml_filename)
    dir_name = count + "." + str(os.path.splitext(dir_name)[0])
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)
        os.mkdir(dir_name + "/" + "files")
    meta(eml_filename, count)
    msg = parse_message(eml_filename)
    attachments = find_attachments(msg)
    #print ("Found {0} attachments...".format(len(attachments)))
    for cdisp, part in attachments:
        cdisp_filename = os.path.normpath(cdisp['filename'])
        if os.path.isabs(cdisp_filename):
            cdisp_filename = os.path.basename(cdisp_filename)
        file_ext = str(os.path.splitext(cdisp_filename)[1]).replace(".", "")
        if "pdf?=" in cdisp_filename:
            file_ext = "pdf"
            cdisp_filename += "." + file_ext
        
        #print(file_ext)
        if not os.path.isdir(dir_name + "/" + "files" + "/" + file_ext):
            os.mkdir(dir_name + "/" + "files" + "/" + file_ext)
        towrite = os.path.join(dir_name, "files", file_ext, cdisp_filename)
        #print( "Writing " + towrite)
        with open(towrite, 'wb') as fp:
            data = part.get_payload(decode=True)
            fp.write(data)





#run("/home/user/Desktop/em/adrian.perez@buzonejercito.mil.co/Drafts/0000018320-Fwd_ Buenos días envió ordenes de Operaciones del mes de diciembre, para que por favor me regalen los anexos.eml")


eml_files = []
m_files = []
other_files = []
for root, directories, files in os.walk("."):
    for file in files:
        ext = str(os.path.splitext(file)[1])
        if ".eml" == ext:
            eml_files.append(os.path.join(root, file))
        elif ".meta" == ext: 
            m_files.append(os.path.join(root, file))
        else: 
            other_files.append(os.path.join(root, file))
other_files = other_files[1::]


count = 0
size = len(eml_files)
for other in other_files:
    if not os.path.isdir("_other"):
        os.mkdir("_other")
    shutil.move(other ,"./_other")
for m in m_files:
    if not os.path.isdir("_meta"):
        os.mkdir("_meta")
    shutil.move(m ,"./_meta")
for eml in eml_files:
    count += 1
    run(eml, str(count))
    os.remove(eml)
    print(str(count)+"/"+str(size))
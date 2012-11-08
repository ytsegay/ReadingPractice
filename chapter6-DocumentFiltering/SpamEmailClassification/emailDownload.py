import email
import docClass
    
# this section gets emails from my live account ... old and dead
def getFelasfaEmails():
    import imaplib
    import getpass

    
    
    conn = imaplib.IMAP4_SSL('imap.googlemail.com')
    username = raw_input("username: ")
    password = getpass.getpass("password: ")
    
    conn.login(username, password)
    code,foo = conn.select('[Gmail]/Spam')
    #code,foo = conn.select('INBOX')
    
    fl = open('gmailSpamEmail.dat', 'w')
    
    if code != 'OK':
        print 'failed to select inbox'
        return
    
    code,foo = conn.search(None, 'ALL')
    
    if code == 'OK':
        msgList = foo[0].split()
        
        for msg in msgList:
            code,data = conn.fetch(msg, '(RFC822)')
            
            if code == 'OK':
                
                rawEmail = data[0][1]
                e = email.message_from_string(rawEmail)
                emailText = str(get_first_text_block(e))
                
                # make sure the body doesn't contain any html
                if len(emailText) > 5 and (emailText.lower().find('<html>') == -1 and emailText.lower().find('<body>') == -1):
                    print 'fetched ',msg
                    
                    sender = ''
                    subject = ''
                    if 'From' in e.keys():
                        sender = e['From']
                    if 'Subject' in e.keys():
                        subject = e['Subject']
                    
                    #print e.keys()
                    fl.write(sender)
                    fl.write('\n')
                    fl.write(subject)
                    fl.write('\n')
                    fl.write(emailText)
                    fl.write('\n')
                           
                    fl.write('===========##===========##===========##===========##===========##===========##===========##\n')
                #return
    conn.close()
    conn.logout()

    fl.close()

def get_first_text_block(email_message_instance):
    maintype = email_message_instance.get_content_maintype()
    if maintype == 'multipart':
        for part in email_message_instance.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload()
    elif maintype == 'text':
        return email_message_instance.get_payload()
    else:
        return 'Failed to find a text part'


def parseEmails(file):
    import re

    f = open(file, 'r');
    docs = {}
    counter = 0
    
    while 1:
        line = f.readline()
        if not line: break
        
        line = line.strip()
        
        if line == '===========##===========##===========##===========##===========##===========##===========##':
            counter += 1
            continue
        
        docs.setdefault(counter, [])
        docs[counter].append(line)
    
    f.close()
    
    retDocs = []
    for k,e in docs.items():
        if len(e) == 0: continue
        
        sender = e[0]
        senderEmail = email.Utils.parseaddr(sender)
        subject = docs[k][1]
        
        body = ' '.join(docs[k][2:])
        splitter = re.compile('\\W*')
    
        subjectWords = [w.lower() for w in splitter.split(subject.lower()) if len(w) > 2 and len(w) < 20]
        bodyWords = [w.lower() for w in splitter.split(body.lower()) if len(w) > 2 and len(w) < 20]
        #senderWords = ['sender'+senderEmail]
        senderWords = []
        
        retDocs.append((senderWords + subjectWords + bodyWords))
    
    return retDocs    

def getArrayTerms(arr):
    features = {}
    for f in arr:
        features[f] = 1
    
    return features

def main():
    c1 = docClass.docClassifier(getArrayTerms)
    
    docsPos = parseEmails('gmailInboxEmail.dat')
    docsNeg = parseEmails('gmailSpamEmail.dat')
    
    for d in docsPos[:10]:
        c1.train(d, 'positive', getArrayTerms)
    
    for d in docsNeg[:10]:
        c1.train(d, 'negative', getArrayTerms)
    
    print c1.itemsInCatWithFeatCounter
    
    failed = total = 0
    for i in range(11,30):
        #if c1.getItemFisherClassification(docsPos[i], 'unknown') == 'negative':
        print docsNeg[i]
        outcome = c1.getItemClassification(docsNeg[i], 'unknown')
        print outcome
        
        if outcome == 'positive':
            failed += 1
        total += 1
    
    print failed, ' ', total
    #print docsPos[11]
    #print docsNeg[11]
    
    #getFelasfaEmails()


if __name__ == '__main__':
    main()

import json
import sys

with open(sys.argv[1],'r', encoding='utf-8') as inFile:
    with open(sys.argv[2], 'w', encoding='utf-8') as outFile:
        header =  None
        headix= None
        for l in inFile:
            o=json.loads(l)
            if header is None:
                header = []
                for k in o:
                    if isinstance(o[k],dict):
                        for k2 in o[k]:
                            header.append(k+'.'+k2)
                            if type(o[k][k2]) is dict:
                                raise(k+'.'+k2)
                    elif isinstance(o[k],list):
                        raise(k)
                    else:
                        header.append(k)
                outFile.write('\t'.join(header)+'\n')
            else:
                for k in o:
                    if isinstance(o[k],dict):
                        for k2 in o[k]:
                            if k+'.'+k2 not in header:
                                raise(k+'.'+k2)                            
                    elif isinstance(o[k],list):
                        raise(k)
                    elif k not in header:
                        raise(k)                        
            r=[]
            for h in header:
                if '.' in h:    
                    k=h.split('.')
                    #print(k)
                    if k[0] in o and k[1] in o[k[0]]:
                        r.append(str(o[k[0]][k[1]]).replace('\n','\\n'))
                    else:
                        r.append('')
                else:                    
                    r.append(o[h] if h in o else '')
            outFile.write('\t'.join(r)+'\n')


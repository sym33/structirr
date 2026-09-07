"""Semantic reference independently implemented in V4; unchanged algorithms."""
import datetime,re
def reference(c):
    s=c['state']; family=s['family']
    if family=='type':
        v=s['value']; checks={'null':v is None,'boolean':isinstance(v,bool),'integer':isinstance(v,int) and not isinstance(v,bool),'number':isinstance(v,float),'string':isinstance(v,str),'array':isinstance(v,list),'object':isinstance(v,dict)}
        answer='accept' if checks[s['required_type']] else 'reject'
    elif family=='date':
        # ISO date strings sort in date order; validate syntax separately.
        for value in (s['date'],s['start'],s['end'],*s['blackout']): datetime.date.fromisoformat(value)
        answer='allow' if s['start']<=s['date']<s['end'] and s['date'] not in s['blackout'] else 'deny'
    elif family=='url':
        if s['operation']=='encode':
            safe=b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.~'
            answer=''.join(chr(b) if b in safe else '%%%02X'%b for b in s['input'].encode('utf-8'))
        else:
            data=bytearray(); text=s['input']; i=0
            while i<len(text):
                if text[i]=='%' and re.fullmatch('[0-9A-Fa-f]{2}',text[i+1:i+3]): data.append(int(text[i+1:i+3],16)); i+=3
                else: data.extend(text[i].encode('utf-8')); i+=1
            answer=data.decode('utf-8')
    else:
        permitted=set(s['allow'])-set(s['deny']); answer='allow' if s['region'] in permitted else 'deny'
    labels=[k for k,v in c['candidates'].items() if v==answer]
    assert len(labels)==1, c
    return labels[0]


import re
s=open('lychrel_correctif.log','r',encoding='utf8').read()
miss=set(re.findall(r"Reference `([^']+)' on",s))
# also match patterns like "Reference `label' undefined" exact
miss2=set(re.findall(r"Reference `([^']+)' undefined",s))
miss = sorted(miss|miss2)
for m in miss:
    print(m)
print('COUNT',len(miss))

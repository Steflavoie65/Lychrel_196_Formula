import re, os
p='..\lychrel_correctif.tex' if os.path.exists('..\\lychrel_correctif.tex') else 'lychrel_correctif.tex'
text=open(p,'r',encoding='utf8').read()
refs=set(re.findall(r'\\(?:ref|eqref|autoref|pageref)\{([^}]+)\}',text))
labels=set(re.findall(r'\\label\{([^}]+)\}',text))
missing=sorted(refs-labels)
if not missing:
    print('NO_MISSING')
else:
    out='%% Auto-generated missing labels placeholder\n'
    for m in missing:
        out += f'\\newlabel{{{m}}}{{}}{{}}\n'
    open('import_missing_labels.tex','w',encoding='utf8').write(out)
    print('WROTE',os.path.getsize('import_missing_labels.tex'))

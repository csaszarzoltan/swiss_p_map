from pathlib import Path
import json,re,sys
root=Path(__file__).resolve().parent
idx=json.loads((root/'index.json').read_text(encoding='utf-8'))
errors=[]
files=sorted(root.glob('SPEC-[0-9][0-9][0-9]-*.md'))
expected_count = idx.get('spec_count', len(files))
if len(files) != expected_count: errors.append(f'spec_count={len(files)} expected={expected_count}')
if idx.get('spec_count') != len(files) or len(idx.get('specs',[])) != len(files): errors.append('index count mismatch')
required=[f'## {i}.' for i in range(1,15)]
for p in files:
 t=p.read_text(encoding='utf-8')
 for h in required:
  if h not in t: errors.append(f'{p.name}: missing {h}')
 if not re.search(r'^status: SPEC_READY$',t,re.M): errors.append(f'{p.name}: status')
 req=set(re.findall(r'REQ-\d{3}(?:-\d{3})?',t.split('## 6.')[0]))
 mapped=set(re.findall(r'^- (REQ-\d{3}(?:-\d{3})?) ->',t,re.M))
 if not req.issubset(mapped): errors.append(f'{p.name}: unmapped {sorted(req-mapped)}')
 ac=set(re.findall(r'^### (AC-\d{3}(?:-\d{3})?):',t,re.M))
 if len(ac)<2: errors.append(f'{p.name}: acceptance count')
 if any(x in t.lower() for x in ['placeholder','todo:','tbd']): errors.append(f'{p.name}: forbidden placeholder')
indexed={x['file'] for x in idx['specs']}
actual={p.name for p in files}
if indexed!=actual: errors.append('index/files mismatch')
if errors:
 print('FAIL'); print('\n'.join(errors)); sys.exit(1)
print(f'PASS specs={len(files)} requirements={sum(len(set(re.findall(r"REQ-[0-9]{3}",p.read_text(encoding="utf-8").split("## 6.")[0]))) for p in files)} acceptance={sum(len(re.findall(r"^### AC-[0-9]{3}:",p.read_text(encoding="utf-8"),re.M)) for p in files)} coverage=100%')

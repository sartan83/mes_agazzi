#!/usr/bin/env python3
# Builds TEST_REPORT.md / TEST_REPORT.html from target/surefire-reports and target/site/jacoco of every module.
# Usage (repo root, after `mvn clean install`): python3 docs/generate_test_report.py
import glob,os,csv,html,sys,xml.etree.ElementTree as ET,datetime,subprocess
root=sys.argv[1] if len(sys.argv)>1 else '.'; os.chdir(root)
import json
B=json.load(open('docs/test-report/baseline-jdk8.json'))
mods=[]
for pom in sorted(glob.glob('mes-plugins/*/pom.xml'))+['mes-application/pom.xml']:
    d=os.path.dirname(pom); m=os.path.basename(d)
    t=f=e=s=0; classes=0; secs=0.0
    for x in glob.glob(f'{d}/target/surefire-reports/TEST-*.xml'):
        r=ET.parse(x).getroot(); classes+=1
        t+=int(r.get('tests'));f+=int(r.get('failures'));e+=int(r.get('errors'));s+=int(r.get('skipped'));secs+=float(r.get('time') or 0)
    cov=None
    c=f'{d}/target/site/jacoco/jacoco.csv'
    if os.path.exists(c):
        mi=co=bm=bc=0
        for row in csv.DictReader(open(c)):
            mi+=int(row['LINE_MISSED']);co+=int(row['LINE_COVERED']);bm+=int(row['BRANCH_MISSED']);bc+=int(row['BRANCH_COVERED'])
        cov=(co,mi+co,bc,bm+bc)
    mods.append(dict(m=m,t=t,f=f,e=e,s=s,p=t-f-e-s,classes=classes,secs=secs,cov=cov))
bl=lambda m: f"{B[m]['tests']} / {B[m]['skipped']}" if m in B else '0 / 0'
T={k:sum(x[k] for x in mods) for k in 't f e s p classes'.split()}
lc=sum(x['cov'][0] for x in mods if x['cov']); lt=sum(x['cov'][1] for x in mods if x['cov'])
bc=sum(x['cov'][2] for x in mods if x['cov']); bt=sum(x['cov'][3] for x in mods if x['cov'])
pct=lambda a,b: f'{100*a/b:.1f}%' if b else 'n/a'
jv=subprocess.run(['java','-version'],capture_output=True,text=True).stderr.splitlines()[0]
mv=subprocess.run(['mvn','-v'],capture_output=True,text=True).stdout.splitlines()[0]
sha=subprocess.run(['git','rev-parse','--short','HEAD'],capture_output=True,text=True).stdout.strip()
now=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
cmd=os.environ.get('REPORT_CMD','mvn clean verify')
md=[f'# Test report — Java 17 migration','',f'- Generated: {now}',f'- Commit: `{sha}` (branch `java17-migration`)',f'- JDK: `{jv}`',f'- Maven: `{mv}`',f'- Command: `{cmd}`','- HTML: [`TEST_REPORT.html`](TEST_REPORT.html) (this summary with per-module drill-down), Surefire aggregate: [`docs/test-report/surefire-report.html`](docs/test-report/surefire-report.html)','',
 '## Totals','','| Tests | Passed | Failed | Errors | Skipped | Test classes | Line coverage | Branch coverage |','|--:|--:|--:|--:|--:|--:|--:|--:|',
 f"| {T['t']} | {T['p']} | {T['f']} | {T['e']} | {T['s']} | {T['classes']} | {pct(lc,lt)} ({lc}/{lt}) | {pct(bc,bt)} ({bc}/{bt}) |",'',
 'Baseline (unmodified `master`, JDK 1.8.0_504): 822 tests, 0 failures, 0 errors, 29 skipped. The extra test/skip on JDK 17 is `TSFOrderSuppliesOrderStateValidationServiceTest` (no active test methods, `@Ignore`d; see `MIGRATION_NOTES.md`).','',
 '## Per module','','| Module | Tests | Passed | Failed | Errors | Skipped | Line coverage | Branch coverage | JDK 8 baseline (tests / skipped) |','|---|--:|--:|--:|--:|--:|--:|--:|--:|']
for x in mods:
    c=x['cov']; lcv=pct(c[0],c[1]) if c else 'n/a'; bcv=pct(c[2],c[3]) if c else 'n/a'
    md.append(f"| `{x['m']}` | {x['t']} | {x['p']} | {x['f']} | {x['e']} | {x['s']} | {lcv} | {bcv} | {bl(x['m'])} |")
md+=['','Modules with 0 tests have no test sources on `master`; they are compiled, woven and packaged as part of the same build. Coverage is JaCoCo line/branch coverage of each module\'s own classes by its own tests (`n/a` = module without tests); the total coverage is computed over the modules that have tests.']
open('TEST_REPORT.md','w').write('\n'.join(md)+'\n')
rows=''.join(f"<tr class='{'bad' if x['f'] or x['e'] else ('none' if not x['t'] else '')}'><td>{html.escape(x['m'])}</td><td>{x['t']}</td><td>{x['p']}</td><td>{x['f']}</td><td>{x['e']}</td><td>{x['s']}</td><td>{pct(*x['cov'][:2]) if x['cov'] else 'n/a'}</td><td>{pct(*x['cov'][2:]) if x['cov'] else 'n/a'}</td><td>{bl(x['m'])}</td></tr>" for x in mods)
ok=T['f']==0 and T['e']==0
H=f"""<!doctype html><html><head><meta charset="utf-8"><title>Test report — Java 17 migration</title><style>
body{{font-family:system-ui,sans-serif;margin:2rem;color:#1a1a1a}}h1{{margin-bottom:.2rem}}.meta{{color:#555;font-size:.9rem}}
.cards{{display:flex;gap:1rem;margin:1.5rem 0;flex-wrap:wrap}}.card{{border:1px solid #ddd;border-radius:8px;padding:1rem 1.4rem;min-width:8rem}}
.card b{{display:block;font-size:1.8rem}}.ok b{{color:#1a7f37}}.ko b{{color:#cf222e}}table{{border-collapse:collapse;width:100%;font-size:.9rem}}
th,td{{border-bottom:1px solid #eee;padding:.35rem .6rem;text-align:right}}th:first-child,td:first-child{{text-align:left}}th{{background:#f6f8fa;position:sticky;top:0}}
tr.bad td{{background:#ffebe9}}tr.none td{{color:#888}}.banner{{padding:.8rem 1rem;border-radius:8px;font-weight:600;background:{'#dafbe1' if ok else '#ffebe9'}}}</style></head><body>
<h1>Test report — Java 17 migration</h1><div class="meta">Generated {now} · commit <code>{sha}</code> · <code>{html.escape(jv)}</code> · <code>{html.escape(mv)}</code> · <code>{html.escape(cmd)}</code></div>
<p class="banner">{'ALL TESTS PASSED' if ok else 'FAILURES PRESENT'} — {T['t']} tests, {T['f']} failures, {T['e']} errors, {T['s']} skipped across {len(mods)} modules</p>
<div class="cards"><div class="card"><span>Tests</span><b>{T['t']}</b></div><div class="card ok"><span>Passed</span><b>{T['p']}</b></div><div class="card {'ko' if T['f'] else ''}"><span>Failed</span><b>{T['f']}</b></div><div class="card {'ko' if T['e'] else ''}"><span>Errors</span><b>{T['e']}</b></div><div class="card"><span>Skipped</span><b>{T['s']}</b></div><div class="card"><span>Line coverage</span><b>{pct(lc,lt)}</b></div><div class="card"><span>Branch coverage</span><b>{pct(bc,bt)}</b></div></div>
<p class="meta">Baseline (unmodified master, JDK 1.8.0_504): 822 tests, 0 failures, 0 errors, 29 skipped. Surefire aggregate report: <a href="docs/test-report/surefire-report.html">docs/test-report/surefire-report.html</a></p>
<table><thead><tr><th>Module</th><th>Tests</th><th>Passed</th><th>Failed</th><th>Errors</th><th>Skipped</th><th>Line cov.</th><th>Branch cov.</th><th>JDK 8 baseline (tests / skipped)</th></tr></thead><tbody>{rows}</tbody></table></body></html>"""
open('TEST_REPORT.html','w').write(H)
print(T, pct(lc,lt), pct(bc,bt))

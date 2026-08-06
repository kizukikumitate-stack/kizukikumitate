import { chromium } from 'playwright';
import { spawn } from 'child_process';
const srv = spawn('python3', ['-m','http.server','8133'], {cwd:'/Users/morimotoyasuhito/kizukikumitate', stdio:'ignore'});
await new Promise(r=>setTimeout(r,1200));
const b = await chromium.launch();
for (const page of ['karuizawa-offsite','gaikokujinzai-teichaku']) {
  for (const [name,w,h] of [['pc',1280,1000],['sp',390,844]]) {
    const p = await b.newPage({viewport:{width:w,height:h}, deviceScaleFactor:name==='sp'?2:1.4});
    await p.goto(`http://localhost:8133/${page}.html`, {waitUntil:'networkidle'});
    await p.evaluate(()=>document.querySelectorAll('.reveal').forEach(e=>e.classList.add('on')));
    await p.screenshot({path:`/tmp/claude-501/${page}-${name}.png`, fullPage: name==='pc'});
    const ov = await p.evaluate(()=>({sw:document.documentElement.scrollWidth, cw:document.documentElement.clientWidth}));
    console.log(page, name, JSON.stringify(ov));
    await p.close();
  }
}
await b.close(); srv.kill();

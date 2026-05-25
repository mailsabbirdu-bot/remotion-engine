import {chromium} from 'playwright';
import {spawn} from 'child_process';
import path from 'path';
import fs from 'fs';
import dns from 'dns';
import { execSync } from 'child_process';

if (dns.setDefaultResultOrder) {
    dns.setDefaultResultOrder('ipv4first');
}

async function render() {
    const port = 3000;
    // Targeting dev server for stability on Colab
    const url = `http://localhost:${port}/?render=true&ui=false`;

    console.log('🚀 Step 1: Starting Vite Dev Server...');
    const vite = spawn('npm', ['run', 'start', '--', '--port', port.toString(), '--host', '0.0.0.0', '--strictPort'], {
        cwd: process.cwd(),
        shell: true
    });

    vite.stdout.on('data', (data) => {
        const line = data.toString();
        if (line.includes('Local:') || line.includes('Network:')) {
            console.log(`[Vite]: ${line.trim()}`);
        }
    });

    console.log('🌐 Step 2: Launching Headless Browser...');
    const browser = await chromium.launch({
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
            '--autoplay-policy=no-user-gesture-required',
            '--disable-web-security'
        ]
    });

    const page = await browser.newPage({
        viewport: { width: 1920, height: 1080 },
        deviceScaleFactor: 1
    });
    page.setDefaultTimeout(0);

    // Tracing and Logging
    page.on('console', msg => console.log(`[BROWSER]: ${msg.text()}`));
    page.on('pageerror', err => console.error('❌ [BROWSER ERROR]:', err.message));
    page.on('requestfailed', req => {
        if (!req.url().includes('favicon')) {
            console.error(`❌ [REQ FAILED]: ${req.url()} - ${req.failure()?.errorText}`);
        }
    });

    const outRoot = path.join(process.cwd(), 'out');
    if (fs.existsSync(outRoot)) fs.rmSync(outRoot, {recursive: true});
    fs.mkdirSync(outRoot);

    await page.exposeFunction('startScene', (index, id) => {
        console.log(`🎬 [RENDER] Scene ${index+1} Started: ${id}`);
        const sceneDir = path.join(outRoot, id);
        if (!fs.existsSync(sceneDir)) fs.mkdirSync(sceneDir);
        return true;
    });

    await page.exposeFunction('saveFrame', async (sceneId, frameNumber, dataUrl) => {
        const base64Data = dataUrl.replace(/^data:image\/png;base64,/, "");
        const filePath = path.join(outRoot, sceneId, `${frameNumber.toString().padStart(6, '0')}.png`);
        fs.writeFileSync(filePath, base64Data, 'base64');
        if (frameNumber % 60 === 0) console.log(`[DISK]: Saved frame ${frameNumber} for ${sceneId}`);
        return true;
    });

    await page.exposeFunction('endScene', (id) => {
        console.log(`✅ [RENDER] Scene Captured: ${id}. Encoding...`);
        const sceneDir = path.join(outRoot, id);
        const videoOutput = path.join(outRoot, `${id}.webm`);
        const framesPattern = path.join(sceneDir, '%06d.png');

        try {
            execSync(`ffmpeg -y -framerate 30 -i "${framesPattern}" -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 4M -crf 15 "${videoOutput}"`, { stdio: 'ignore' });
            console.log(`🚀 [SUCCESS] Video saved: ${id}.webm`);
            fs.rmSync(sceneDir, {recursive: true});
        } catch (err) {
            console.error(`❌ [ERROR] FFmpeg failed for ${id}:`, err.message);
        }
        return true;
    });

    try {
        console.log(`🔗 Step 3: Connecting to Dev Server...`);
        let success = false;
        for (let i = 0; i < 60; i++) {
            try {
                const response = await page.goto(url, {waitUntil: 'networkidle', timeout: 10000});
                if (response && response.status() === 200) {
                    success = true;
                    console.log('✅ App loaded successfully in Dev Mode.');
                    break;
                }
            } catch (e) {
                await new Promise(r => setTimeout(r, 2000));
            }
        }

        if (!success) throw new Error(`Could not reach Vite server at ${url}.`);

        console.log('🎬 Step 4: Rendering sequence...');

        let lastLog = Date.now();
        const progressCheck = setInterval(async () => {
            if (Date.now() - lastLog > 60000) {
                console.log('⚠️ [STUCK MONITOR]: No frame activity for 60s.');
                await page.screenshot({path: 'stuck-debug.png'});
                lastLog = Date.now();
            }
        }, 30000);

        await page.waitForFunction(() => window.finished === true, {timeout: 0, polling: 1000});
        clearInterval(progressCheck);
        console.log('🏁 All renders complete.');

    } catch (e) {
        console.error('❌ Render Failed:', e.message);
        await page.screenshot({path: 'fatal-error.png'});
    } finally {
        await browser.close();
        vite.kill();
        process.exit(0);
    }
}

render().catch(err => {
    console.error('💥 Fatal Error:', err);
    process.exit(1);
});

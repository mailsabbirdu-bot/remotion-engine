import {chromium} from 'playwright';
import {spawn, execSync} from 'child_process';
import path from 'path';
import fs from 'fs';
import dns from 'dns';

if (dns.setDefaultResultOrder) {
    dns.setDefaultResultOrder('ipv4first');
}

async function render() {
    const port = 3000;
    // Navigation URL - target root in dev mode
    const url = `http://localhost:${port}/?render=true&ui=false`;

    console.log('🚀 Step 1: Starting Vite Development Server...');
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

    page.on('requestfailed', request => {
        // console.error(`❌ [REQ FAILED]: ${request.url()} - ${request.failure()?.errorText}`);
    });

    page.on('response', response => {
        if (response.status() >= 400) {
            console.error(`❌ [RES ERR]: ${response.url()} status ${response.status()}`);
        }
    });

    page.on('console', msg => {
        console.log(`[BROWSER]: ${msg.text()}`);
    });

    page.on('pageerror', err => {
        console.error('❌ [BROWSER FATAL]:', err.message);
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
        console.log(`✅ [RENDER] Scene Captured: ${id}. Encoding to transparent WebM...`);
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
        console.log(`🔗 Step 3: Connecting to local server...`);
        let success = false;
        // Give Vite a moment to start
        await new Promise(r => setTimeout(r, 5000));

        for (let i = 0; i < 60; i++) {
            try {
                const response = await page.goto(url, {waitUntil: 'load', timeout: 15000});
                if (response && response.status() === 200) {
                    success = true;
                    console.log('✅ Page loaded successfully.');
                    break;
                }
                console.log(`...waiting (status: ${response ? response.status() : 'none'})`);
            } catch (e) {
                console.log(`...waiting for server (attempt ${i+1}/60) - ${e.message}`);
                await new Promise(r => setTimeout(r, 2000));
            }
        }

        if (!success) {
            await page.screenshot({path: 'connection-failure.png'});
            throw new Error(`Server at ${url} not reachable.`);
        }

        console.log('🎬 Step 4: Rendering sequence...');

        // Progress monitor
        let lastLog = Date.now();
        const progressCheck = setInterval(async () => {
            if (Date.now() - lastLog > 60000) {
                console.log('⚠️ [STUCK MONITOR]: No progress for 60s. Taking emergency screenshot...');
                await page.screenshot({path: 'stuck-screenshot.png'});
                lastLog = Date.now();
            }
        }, 30000);

        await page.waitForFunction(() => window.finished === true, {timeout: 0, polling: 1000});
        clearInterval(progressCheck);
        console.log('🏁 All renders complete.');

    } catch (e) {
        console.error('❌ Render Process Failed:', e.message);
        try {
            await page.screenshot({path: 'fatal-error-screenshot.png'});
            console.log('📸 Fatal error screenshot saved.');
        } catch(ssErr) {}
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

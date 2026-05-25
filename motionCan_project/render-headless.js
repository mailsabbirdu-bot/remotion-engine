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
    const url = `http://127.0.0.1:${port}/index.html?render=true&ui=false`;

    console.log('🏗️ Building project...');
    try {
        execSync('npm run build', {cwd: process.cwd(), stdio: 'inherit'});
    } catch (err) {
        console.error('❌ Build failed:', err.message);
        process.exit(1);
    }

    console.log('🚀 Starting preview server...');
    const vite = spawn('npm', ['run', 'serve', '--', '--port', port.toString(), '--host', '0.0.0.0', '--strictPort'], {
        cwd: process.cwd(),
        shell: true
    });

    vite.stdout.on('data', (data) => {
        const line = data.toString();
        if (line.includes('Local:') || line.includes('Network:')) {
            console.log(`Vite: ${line.trim()}`);
        }
    });

    console.log('🌐 Launching Browser...');
    const browser = await chromium.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
    });

    const page = await browser.newPage();
    page.setDefaultTimeout(0);

    page.on('console', msg => {
        console.log(`[BROWSER]: ${msg.text()}`);
    });

    page.on('pageerror', err => {
        console.error('❌ [BROWSER ERROR]:', err.message);
    });

    const outRoot = path.join(process.cwd(), 'out');
    if (fs.existsSync(outRoot)) fs.rmSync(outRoot, {recursive: true});
    fs.mkdirSync(outRoot);

    await page.exposeFunction('startScene', (index, id) => {
        console.log(`🎬 Scene [${index+1}] Start: ${id}`);
        const sceneDir = path.join(outRoot, id);
        if (!fs.existsSync(sceneDir)) fs.mkdirSync(sceneDir);
        return true;
    });

    await page.exposeFunction('saveFrame', async (sceneId, frameNumber, dataUrl) => {
        const base64Data = dataUrl.replace(/^data:image\/png;base64,/, "");
        const filePath = path.join(outRoot, sceneId, `${frameNumber.toString().padStart(6, '0')}.png`);
        fs.writeFileSync(filePath, base64Data, 'base64');
        return true;
    });

    await page.exposeFunction('endScene', (id) => {
        console.log(`✅ Scene Captured: ${id}. Encoding...`);
        const sceneDir = path.join(outRoot, id);
        const videoOutput = path.join(outRoot, `${id}.webm`);
        const framesPattern = path.join(sceneDir, '%06d.png');

        try {
            execSync(`ffmpeg -y -framerate 30 -i "${framesPattern}" -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 4M -crf 15 "${videoOutput}"`, { stdio: 'ignore' });
            console.log(`🚀 scene video saved: ${id}.webm`);
            fs.rmSync(sceneDir, {recursive: true});
        } catch (err) {
            console.error(`❌ FFmpeg failed for ${id}:`, err.message);
        }
        return true;
    });

    try {
        console.log(`🔗 Navigating to ${url}...`);

        let success = false;
        for (let i = 0; i < 30; i++) {
            try {
                // Using explicit index.html in the URL to avoid 404s during bundle resolution
                const response = await page.goto(url, {waitUntil: 'networkidle', timeout: 15000});
                if (response && response.status() === 200) {
                    success = true;
                    break;
                }
                console.log(`...waiting (status: ${response ? response.status() : 'none'})`);
            } catch (e) {
                console.log(`...waiting for server (attempt ${i+1}/30)`);
                await new Promise(r => setTimeout(r, 2000));
            }
        }

        if (!success) {
            throw new Error(`Failed to load ${url} after 30 attempts.`);
        }

        console.log('⏳ Stabilizing bundle...');
        await new Promise(r => setTimeout(r, 5000));

        console.log('🎬 Rendering sequence...');
        await page.waitForFunction(() => window.finished === true, {timeout: 0, polling: 500});
        console.log('🏁 Rendering sequence complete.');

    } catch (e) {
        console.error('❌ Render Failed:', e.message);
        await page.screenshot({path: 'render-error-preview.png'});
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

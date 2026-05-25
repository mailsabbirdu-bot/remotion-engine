import {chromium} from 'playwright';
import {spawn, execSync} from 'child_process';
import path from 'path';
import fs from 'fs';
import dns from 'dns';

// Ensure Node.js prefers IPv4 to avoid connection issues with 127.0.0.1/localhost
if (dns.setDefaultResultOrder) {
    dns.setDefaultResultOrder('ipv4first');
}

async function render() {
    const port = 3000;
    const url = `http://127.0.0.1:${port}/?render=true&ui=false`;

    console.log('🏗️ Building project for production...');
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

    vite.stderr.on('data', (data) => {
        // console.log(`Vite Log: ${data}`);
    });

    console.log('🌐 Launching Headless Browser...');
    const browser = await chromium.launch({
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
            '--autoplay-policy=no-user-gesture-required'
        ]
    });

    const page = await browser.newPage();
    page.setDefaultTimeout(0);

    // Proxy browser logs
    page.on('console', msg => {
        console.log(`[BROWSER]: ${msg.text()}`);
    });

    page.on('pageerror', err => {
        console.error('❌ [BROWSER ERROR]:', err.message);
    });

    const outRoot = path.join(process.cwd(), 'out');
    if (fs.existsSync(outRoot)) fs.rmSync(outRoot, {recursive: true});
    fs.mkdirSync(outRoot);

    // EXPOSE BRIDGE FUNCTIONS
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

        // Robust navigation retry loop
        let success = false;
        for (let i = 0; i < 20; i++) {
            try {
                await page.goto(url, {waitUntil: 'networkidle', timeout: 10000});
                success = true;
                break;
            } catch (e) {
                console.log(`...waiting for server to respond (attempt ${i+1}/20)`);
                await new Promise(r => setTimeout(r, 2000));
            }
        }

        if (!success) {
            throw new Error(`Failed to connect to Vite server at ${url} after 20 attempts.`);
        }

        console.log('⏳ Stabilizing bundle...');
        await new Promise(r => setTimeout(r, 3000));

        console.log('🎬 Rendering sequence...');
        await page.waitForFunction(() => window.finished === true, {timeout: 0, polling: 500});
        console.log('🏁 All sequences complete.');

    } catch (e) {
        console.error('❌ Render Failed:', e.message);
        await page.screenshot({path: 'render-error-final.png'});
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

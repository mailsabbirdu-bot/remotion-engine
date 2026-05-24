import {chromium} from 'playwright';
import {spawn} from 'child_process';
import path from 'path';
import fs from 'fs';
import http from 'http';

async function waitForServer(url, timeout = 30000) {
    const start = Date.now();
    while (Date.now() - start < timeout) {
        try {
            await new Promise((resolve, reject) => {
                http.get(url, (res) => resolve(res.statusCode === 200))
                    .on('error', reject);
            });
            return true;
        } catch (e) {
            await new Promise(r => setTimeout(resolve, 1000));
        }
    }
    return false;
}

async function render() {
    const port = 3000;
    const url = `http://localhost:${port}/?render=true`;

    console.log('🚀 Starting Vite server...');
    const vite = spawn('npx', ['vite', '--port', port.toString(), '--host', '0.0.0.0'], {
        cwd: process.cwd(),
        shell: true,
        stdio: 'inherit'
    });

    console.log('⏳ Waiting for Vite to be ready...');
    // Simple delay as fallback, better check would be ideal
    await new Promise(r => setTimeout(r, 15000));

    console.log('🌐 Opening browser...');
    const browser = await chromium.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage({
        viewport: {width: 1920, height: 1080}
    });

    // Create output dir
    const outDir = path.join(process.cwd(), 'out');
    if (fs.existsSync(outDir)) fs.rmSync(outDir, {recursive: true});
    fs.mkdirSync(outDir);

    console.log('🎬 Rendering frames...');

    await page.exposeFunction('saveFrame', (frameNumber, dataUrl) => {
        const base64Data = dataUrl.replace(/^data:image\/png;base64,/, "");
        const fileName = `${frameNumber.toString().padStart(6, '0')}.png`;
        fs.writeFileSync(path.join(outDir, fileName), base64Data, 'base64');
    });

    try {
        await page.goto(url, {waitUntil: 'networkidle', timeout: 60000});
        // Wait for completion signal
        await page.waitForFunction(() => window.finished === true, {timeout: 600000});
        console.log('✅ Render complete!');
    } catch (e) {
        console.error('❌ Render failed:', e.message);
    } finally {
        await browser.close();
        vite.kill();
        process.exit(0);
    }
}

render().catch(err => {
    console.error(err);
    process.exit(1);
});

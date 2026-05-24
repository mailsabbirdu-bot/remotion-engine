import {chromium} from 'playwright';
import {spawn} from 'child_process';
import path from 'path';
import fs from 'fs';
import http from 'http';

async function render() {
    const port = 3000;
    const url = `http://127.0.0.1:${port}/?render=true`;

    console.log('🚀 Starting Vite server...');
    const vite = spawn('npx', ['vite', '--port', port.toString(), '--strictPort'], {
        cwd: process.cwd(),
        shell: true,
        stdio: 'inherit'
    });

    console.log('⏳ Waiting for Vite to be ready...');
    await new Promise(r => setTimeout(r, 10000));

    console.log('🌐 Opening browser...');
    const browser = await chromium.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage({
        viewport: {width: 1920, height: 1080}
    });

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
        // Reduced timeout and added retries
        let success = false;
        for(let i=0; i<5; i++) {
            try {
                await page.goto(url, {waitUntil: 'networkidle', timeout: 30000});
                success = true;
                break;
            } catch (e) {
                console.log(`Retry ${i+1} connecting to Vite...`);
                await new Promise(r => setTimeout(r, 2000));
            }
        }

        if (!success) throw new Error('Could not connect to Vite server');

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

import {chromium} from 'playwright';
import {spawn} from 'child_process';
import path from 'path';
import fs from 'fs';

async function render() {
    const port = 3000;
    const url = `http://127.0.0.1:${port}/?render=true`;

    console.log('🚀 Starting Vite server...');
    const vite = spawn('npm', ['run', 'start', '--', '--port', port.toString(), '--host', '127.0.0.1', '--strictPort'], {
        cwd: process.cwd(),
        shell: true
    });

    vite.stdout.on('data', (data) => {
        process.stdout.write(`Vite: ${data}`);
    });

    vite.stderr.on('data', (data) => {
        process.stderr.write(`Vite Error: ${data}`);
    });

    console.log('⏳ Waiting for Vite to be ready...');
    // Poll for the Vite server to be up
    let viteReady = false;
    for (let i = 0; i < 30; i++) {
        try {
            const res = await fetch(`http://127.0.0.1:${port}`);
            if (res.ok) {
                viteReady = true;
                break;
            }
        } catch (e) {}
        await new Promise(r => setTimeout(r, 1000));
    }
    if (!viteReady) {
        console.warn('⚠️ Vite server did not respond in time, proceeding anyway...');
    } else {
        console.log('✅ Vite server is ready!');
    }

    console.log('🌐 Opening browser...');
    const browser = await chromium.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage({
        viewport: {width: 1920, height: 1080}
    });

    page.on('console', msg => {
        console.log(`BROWSER [${msg.type()}]: ${msg.text()}`);
    });

    page.on('pageerror', err => {
        console.error('BROWSER ERROR:', err.message);
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
        console.log(`🔗 Navigating to ${url}...`);
        await page.goto(url, {waitUntil: 'networkidle', timeout: 90000});

        console.log('⏳ Waiting for completion signal from Motion Canvas...');
        // Increased timeout to 20 minutes for large projects
        await page.waitForFunction(() => window.finished === true, {timeout: 1200000});
        console.log('✅ Render complete!');
    } catch (e) {
        console.error('❌ Render failed:', e.message);
        await page.screenshot({path: 'error-screenshot.png'});
        console.log('📸 Error screenshot saved to error-screenshot.png');
    } finally {
        await browser.close();
        vite.kill();
        await new Promise(r => setTimeout(r, 2000));
        process.exit(0);
    }
}

render().catch(err => {
    console.error('💥 Fatal Error:', err);
    process.exit(1);
});

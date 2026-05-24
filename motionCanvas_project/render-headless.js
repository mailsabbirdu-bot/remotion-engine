import {chromium} from 'playwright';
import {spawn} from 'child_process';
import path from 'path';
import fs from 'fs';

async function render() {
    console.log('🚀 Starting Vite server...');
    const vite = spawn('npx', ['vite', '--port', '3000'], {
        cwd: process.cwd(),
        shell: true
    });

    vite.stdout.on('data', (data) => console.log(`Vite: ${data}`));

    // Wait for vite to start
    await new Promise(resolve => setTimeout(resolve, 8000));

    console.log('🌐 Opening browser...');
    const browser = await chromium.launch({headless: true});
    const page = await browser.newPage({
        viewport: {width: 1920, height: 1080}
    });

    // Create output dir
    const outDir = path.join(process.cwd(), 'out');
    if (!fs.existsSync(outDir)) fs.mkdirSync(outDir);

    console.log('🎬 Rendering frames...');

    // Listen for frame capture requests from the browser
    await page.exposeFunction('saveFrame', (frameNumber, dataUrl) => {
        const base64Data = dataUrl.replace(/^data:image\/png;base64,/, "");
        const fileName = `${frameNumber.toString().padStart(6, '0')}.png`;
        fs.writeFileSync(path.join(outDir, fileName), base64Data, 'base64');
    });

    await page.goto('http://localhost:3000/?render=true');

    // Wait for completion signal - Fixed SyntaxError (removed TypeScript 'as' keyword)
    await page.waitForFunction(() => window.finished === true, {timeout: 600000});

    console.log('✅ Render complete!');
    await browser.close();
    vite.kill();
    process.exit(0);
}

render().catch(err => {
    console.error(err);
    process.exit(1);
});

import {chromium} from 'playwright';
import {spawn, execSync} from 'child_process';
import path from 'path';
import fs from 'fs';

async function render() {
    const port = 3000;
    const url = `http://127.0.0.1:${port}/?render=true&ui=false`;

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
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--autoplay-policy=no-user-gesture-required',
            '--disable-web-security'
        ]
    });

    const context = await browser.newContext({
        viewport: {width: 1920, height: 1080},
        deviceScaleFactor: 1,
        screen: {width: 1920, height: 1080}
    });

    const page = await context.newPage();
    page.setDefaultTimeout(0);

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

    // Expose capture function - make it wait for completion
    await page.exposeFunction('saveFrame', async (frameNumber) => {
        const fileName = `${frameNumber.toString().padStart(6, '0')}.png`;
        const filePath = path.join(outDir, fileName);

        const canvas = await page.$('canvas');
        if (canvas) {
            await canvas.screenshot({path: filePath, omitBackground: false});
        } else {
            await page.screenshot({path: filePath});
        }
    });

    try {
        console.log(`🔗 Navigating to ${url}...`);
        await page.goto(url, {waitUntil: 'load', timeout: 120000});

        try {
            await page.waitForLoadState('networkidle', {timeout: 15000});
        } catch (e) {
            console.log('⚠️ Networkidle timeout, proceeding with render...');
        }

        console.log('⏳ Waiting for completion signal from Motion Canvas...');
        await page.waitForFunction(() => window.finished === true, {timeout: 3600000, polling: 1000});
        console.log('✅ Render complete!');

        // --- AUDIO MUXING LOGIC ---
        console.log('🎵 Processing audio tracks from background videos...');
        const configPath = path.join(process.cwd(), 'motion_canvas.json');
        const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

        const audioSegments = [];
        const tempDir = path.join(process.cwd(), 'temp_audio');
        if (fs.existsSync(tempDir)) fs.rmSync(tempDir, {recursive: true});
        fs.mkdirSync(tempDir);

        for (let i = 0; i < config.scenes.length; i++) {
            const scene = config.scenes[i];
            if (scene.background && scene.background.type === 'video') {
                const videoPath = path.join(process.cwd(), 'public', scene.background.src);
                if (fs.existsSync(videoPath)) {
                    const segmentPath = path.join(tempDir, `seg_${i}.wav`);
                    console.log(`  🔊 Extracting audio from ${scene.background.src} (${scene.duration}s)`);
                    try {
                        // Extract audio segment matching scene duration
                        execSync(`ffmpeg -y -ss 0 -t ${scene.duration} -i "${videoPath}" -vn -acodec pcm_s16le -ar 44100 -ac 2 "${segmentPath}"`, { stdio: 'ignore' });
                        audioSegments.push(segmentPath);
                    } catch (err) {
                        console.warn(`  ⚠️ Failed to extract audio for scene ${i}: ${err.message}`);
                    }
                }
            } else {
                // Generate silence for scenes without video background
                const segmentPath = path.join(tempDir, `seg_${i}.wav`);
                console.log(`  🔇 Generating silence for scene ${i} (${scene.duration}s)`);
                execSync(`ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=stereo -t ${scene.duration} -acodec pcm_s16le "${segmentPath}"`, { stdio: 'ignore' });
                audioSegments.push(segmentPath);
            }
        }

        if (audioSegments.length > 0) {
            console.log('  🔀 Concatenating audio segments...');
            const listPath = path.join(tempDir, 'list.txt');
            const listContent = audioSegments.map(s => `file '${s}'`).join('\n');
            fs.writeFileSync(listPath, listContent);

            execSync(`ffmpeg -y -f concat -safe 0 -i "${listPath}" -c copy master_audio.wav`, { stdio: 'ignore' });
            console.log('✅ Master audio generated!');
        }

        // --- FINAL ENCODING ---
        console.log('🎞️ Encoding final video with audio...');
        const frameCount = fs.readdirSync(outDir).filter(f => f.endsWith('.png')).length;
        if (frameCount > 0) {
            let ffmpegCmd = `ffmpeg -y -framerate 30 -i out/%06d.png`;
            if (fs.existsSync('master_audio.wav')) {
                ffmpegCmd += ` -i master_audio.wav -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest video.mp4`;
            } else {
                ffmpegCmd += ` -c:v libx264 -crf 18 -pix_fmt yuv420p video.mp4`;
            }

            console.log(`Running: ${ffmpegCmd}`);
            execSync(ffmpegCmd, { stdio: 'inherit' });
            console.log('🚀 SUCCESS! video.mp4 is ready.');
        } else {
            console.error('❌ No frames found for encoding.');
        }

    } catch (e) {
        console.error('❌ Render failed:', e.message);
        await page.screenshot({path: 'error-screenshot.png'});
        console.log('📸 Error screenshot saved to error-screenshot.png');
    } finally {
        await browser.close();
        vite.kill();
        // Cleanup temp files
        if (fs.existsSync('temp_audio')) fs.rmSync('temp_audio', {recursive: true});
        // if (fs.existsSync('master_audio.wav')) fs.unlinkSync('master_audio.wav');

        await new Promise(r => setTimeout(r, 2000));
        process.exit(0);
    }
}

render().catch(err => {
    console.error('💥 Fatal Error:', err);
    process.exit(1);
});

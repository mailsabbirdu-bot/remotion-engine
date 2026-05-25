import {makeProject, bootstrap} from '@motion-canvas/core';
import main from './scenes/main?scene';
import configData from '../master_motion.json';
import {MotionCanvasConfig} from './types';

const config = configData as MotionCanvasConfig;

console.log('🚀 [MAIN] Defining MoCanvas project...');

const project = makeProject({
  scenes: [main],
  size: {x: config.width || 1920, y: config.height || 1080},
});

// Avoid double bootstrapping which causes the "logger" undefined error
if (!(window as any).projectBootstrapped) {
    console.log('✅ [MAIN] First load. Bootstrapping...');
    (window as any).projectBootstrapped = true;
    bootstrap(project);
} else {
    console.log('⚠️ [MAIN] Project already bootstrapped. Skipping.');
}

export default project;

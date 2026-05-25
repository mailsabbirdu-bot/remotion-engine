import {makeProject, bootstrap} from '@motion-canvas/core';
import main from './scenes/main?scene';
import configData from '../master_motion.json';
import {MotionCanvasConfig} from './types';

const config = configData as MotionCanvasConfig;

console.log('🚀 [PROJECT] Defining MoCanvas project...');

const project = makeProject({
  scenes: [main],
  size: {x: config.width || 1920, y: config.height || 1080},
});

// Avoid double bootstrapping which causes the "logger" undefined error in production
if (!(window as any).projectBootstrapped) {
    console.log('✅ [PROJECT] First load. Bootstrapping...');
    (window as any).projectBootstrapped = true;
    bootstrap(project);
} else {
    console.log('⚠️ [PROJECT] Project already bootstrapped. Skipping.');
}

export default project;

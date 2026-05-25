import {makeProject} from '@motion-canvas/core';
import main from './scenes/main?scene';
import configData from '../master_motion.json';
import {MotionCanvasConfig} from './types';

const config = configData as MotionCanvasConfig;

console.log('🚀 [INDEX] Initializing Motion Canvas project...');

export default makeProject({
  scenes: [main],
  size: {x: config.width || 1920, y: config.height || 1080},
});

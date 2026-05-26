import {makeProject} from '@motion-canvas/core';
import main from './scenes/main?scene';
import configData from '../master_revideo.json';
import {MotionCanvasConfig} from './types';

const config = configData as MotionCanvasConfig;

console.log('🚀 [PROJECT] Defining Revideo project...');

export default makeProject({
  scenes: [main],
  size: {x: config.width || 1920, y: config.height || 1080},
});

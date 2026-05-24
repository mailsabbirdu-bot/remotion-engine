import {makeProject} from '@motion-canvas/core';
import main from './scenes/main?scene';
import configData from '../motion_canvas.json';
import {MotionCanvasConfig} from './types';

const config = configData as MotionCanvasConfig;

const project = makeProject({
  scenes: [main],
  size: {x: config.width || 1920, y: config.height || 1080},
  audio: config.audio,
});

export default project;

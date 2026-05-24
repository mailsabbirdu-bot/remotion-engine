import {makeProject} from '@motion-canvas/core';
import main from './scenes/main?scene';
import config from '../motion_canvas.json';

export default makeProject({
  scenes: [main],
  size: {x: config.width || 1920, y: config.height || 1080},
});

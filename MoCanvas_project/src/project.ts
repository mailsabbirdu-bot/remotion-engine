import {makeProject} from '@motion-canvas/core';
import main from './scenes/main?scene';

export default makeProject({
  scenes: [main],
  size: {x: 1920, y: 1080},
});

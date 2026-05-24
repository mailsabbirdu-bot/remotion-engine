import {makeProject} from '@motion-canvas/core';
import main from './scenes/main?scene';

const project = makeProject({
  scenes: [main],
});

// Detect render mode
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('render') === 'true') {
    // In render mode, we'll try to use the project's logger or hooks
    // to capture frames. For this implementation, the main scene
    // handles signaling.
}

export default project;

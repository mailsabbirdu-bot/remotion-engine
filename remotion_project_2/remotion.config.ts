import { Config } from 'remotion';
import fs from 'fs';

const DRIVE_JSON_PATH = '/content/drive/MyDrive/Counterism_Studio_V4/master_remotion.json';

if (fs.existsSync(DRIVE_JSON_PATH)) {
  try {
    const rawData = fs.readFileSync(DRIVE_JSON_PATH, 'utf-8');
    const data = JSON.parse(rawData);
    Config.setProps({
      data: data
    });
    console.log(`[REMOTION_CONFIG] Successfully loaded master_remotion.json from Google Drive: ${DRIVE_JSON_PATH}`);
  } catch (error) {
    console.error(`[REMOTION_CONFIG] Error reading/parsing master_remotion.json from Google Drive:`, error);
  }
} else {
  console.warn(`[REMOTION_CONFIG] Google Drive path not found: ${DRIVE_JSON_PATH}. Falling back to internal data.`);
}

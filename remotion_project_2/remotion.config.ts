import { Config } from '@remotion/cli/config';
import fs from 'fs';

const DEFAULT_DRIVE_PATH = '/content/drive/MyDrive/Counterism_Studio_V4/master_remotion.json';
const configPath = process.env.REMOTION_DRIVE_JSON || DEFAULT_DRIVE_PATH;

if (fs.existsSync(configPath)) {
  try {
    const rawData = fs.readFileSync(configPath, 'utf-8');
    const data = JSON.parse(rawData);
    Config.setProps({
      data: data
    });
    console.log(`[REMOTION_CONFIG] Successfully loaded configuration from: ${configPath}`);
  } catch (error) {
    console.error(`[REMOTION_CONFIG] Error reading/parsing configuration from ${configPath}:`, error);
  }
} else {
  console.warn(`[REMOTION_CONFIG] Configuration path not found: ${configPath}. Falling back to internal data.`);
}

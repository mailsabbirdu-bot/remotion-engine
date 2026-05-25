export interface StyleProps {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  fontSize?: number;
  color?: string;
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  opacity?: number;
  scale?: number;
  rotation?: number;
  fontFamily?: string;
  fontWeight?: number;
  padding?: number;
  borderRadius?: number;
  letterSpacing?: number;
  lineHeight?: number;
  shadowColor?: string;
  shadowBlur?: number;
}

export interface AnimationProps {
  type: 'fade' | 'slide-up' | 'slide-down' | 'slide-left' | 'slide-right' | 'zoom' | 'blur' | 'typewriter';
  duration: number;
  delay?: number;
  easing?: string;
}

export interface Layer {
  id: string;
  type: 'text' | 'textbox' | 'image' | 'video' | 'shape' | 'chart' | 'graph';
  content?: string;
  start?: number; // start time in seconds
  duration?: number; // duration in seconds
  style?: StyleProps;
  animationIn?: AnimationProps;
  animationOut?: AnimationProps;
  data?: any;
  chartType?: 'bar' | 'line' | 'pie';
}

export interface Scene {
  id: string;
  duration: number;
  background?: {
    type: 'video' | 'image' | 'color';
    src: string;
    opacity?: number;
    audio?: string;
  };
  layers: Layer[];
}

export interface MotionCanvasConfig {
  width: number;
  height: number;
  fps: number;
  scenes: Scene[];
}

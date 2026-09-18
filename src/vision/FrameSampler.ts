export interface SampledFrame {
  canvas: HTMLCanvasElement;
  timestamp: number;
  width: number;
  height: number;
}

export interface FrameSamplerOptions {
  targetFps?: number;
  width?: number;
  height?: number;
  onFrame: (frame: SampledFrame) => void;
}

export class FrameSampler {
  private video: HTMLVideoElement;
  private canvas: HTMLCanvasElement;
  private context: CanvasRenderingContext2D;
  private targetInterval: number;
  private onFrame: (frame: SampledFrame) => void;

  private running = false;
  private animationFrameId: number | null = null;
  private lastSampleTime = 0;

  constructor(
    video: HTMLVideoElement,
    options: FrameSamplerOptions,
  ) {
    this.video = video;

    this.canvas = document.createElement("canvas");

    this.canvas.width = options.width ?? 640;
    this.canvas.height = options.height ?? 360;

    const context = this.canvas.getContext("2d");

    if (!context) {
      throw new Error("Unable to create frame processing context.");
    }

    this.context = context;

    const targetFps = options.targetFps ?? 15;

    this.targetInterval = 1000 / targetFps;
    this.onFrame = options.onFrame;
  }

  start() {
    if (this.running) {
      return;
    }

    this.running = true;
    this.lastSampleTime = performance.now();

    this.loop();
  }

  stop() {
    this.running = false;

    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
  }

  private loop = () => {
    if (!this.running) {
      return;
    }

    const now = performance.now();

    if (
      now - this.lastSampleTime >=
      this.targetInterval
    ) {
      this.lastSampleTime = now;

      if (
        this.video.readyState >=
        HTMLMediaElement.HAVE_CURRENT_DATA
      ) {
        this.context.drawImage(
          this.video,
          0,
          0,
          this.canvas.width,
          this.canvas.height,
        );

        this.onFrame({
          canvas: this.canvas,
          timestamp: now,
          width: this.canvas.width,
          height: this.canvas.height,
        });
      }
    }

    this.animationFrameId =
      requestAnimationFrame(this.loop);
  };
}
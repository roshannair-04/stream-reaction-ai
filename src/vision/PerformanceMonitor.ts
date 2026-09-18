export interface PerformanceStats {
  cameraFps: number;
  processingFps: number;
  processingLatencyMs: number;
}

export class PerformanceMonitor {
  private cameraFrames = 0;
  private processedFrames = 0;

  private lastCameraTimestamp = performance.now();
  private lastProcessingTimestamp = performance.now();

  private cameraFps = 0;
  private processingFps = 0;
  private processingLatencyMs = 0;

  recordCameraFrame() {
    this.cameraFrames++;

    const now = performance.now();
    const elapsed = now - this.lastCameraTimestamp;

    if (elapsed >= 1000) {
      this.cameraFps =
        (this.cameraFrames * 1000) / elapsed;

      this.cameraFrames = 0;
      this.lastCameraTimestamp = now;
    }
  }

  recordProcessingFrame(
    processingTimeMs: number,
  ) {
    this.processedFrames++;

    this.processingLatencyMs = processingTimeMs;

    const now = performance.now();
    const elapsed =
      now - this.lastProcessingTimestamp;

    if (elapsed >= 1000) {
      this.processingFps =
        (this.processedFrames * 1000) / elapsed;

      this.processedFrames = 0;
      this.lastProcessingTimestamp = now;
    }
  }

  getStats(): PerformanceStats {
    return {
      cameraFps: Math.round(this.cameraFps),
      processingFps: Math.round(this.processingFps),
      processingLatencyMs:
        Math.round(this.processingLatencyMs * 10) / 10,
    };
  }
}
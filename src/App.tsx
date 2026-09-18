import { useEffect, useRef, useState } from "react";
import { FrameSampler } from "./vision/FrameSampler";
import { PerformanceMonitor } from "./vision/PerformanceMonitor";
import "./App.css";

function App() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const samplerRef = useRef<FrameSampler | null>(null);
  const performanceRef = useRef(new PerformanceMonitor());

  const [cameraFps, setCameraFps] = useState(0);
  const [processingFps, setProcessingFps] = useState(0);
  const [processingLatency, setProcessingLatency] = useState(0);
  const [cameraActive, setCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);

  async function startCamera() {
    setCameraError(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: "user",
        },
        audio: false,
      });

      streamRef.current = stream;
      setCameraActive(true);
    } catch (error) {
      console.error("Camera error:", error);

      setCameraError(
        "Unable to access the camera. Please check your macOS camera permissions."
      );

      setCameraActive(false);
    }
  }

  useEffect(() => {
    if (!cameraActive || !videoRef.current || !streamRef.current) {
      return;
    }

    videoRef.current.srcObject = streamRef.current;

    videoRef.current
      .play()
      .catch((error) => {
        console.error("Video playback error:", error);
        setCameraError("Camera opened, but video playback failed.");
      });
  }, [cameraActive]);

  function stopCamera() {
    streamRef.current?.getTracks().forEach((track) => track.stop());

    streamRef.current = null;

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setCameraActive(false);
  }

  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  useEffect(() => {
    if (!cameraActive || !videoRef.current) {
      return;
    }

    const video = videoRef.current;

    let running = true;
    let callbackId: number | null = null;

    const measureFrame = (
      _now: number,
      _metadata: VideoFrameCallbackMetadata,
    ) => {
      if (!running) {
        return;
      }

      performanceRef.current.recordCameraFrame();

      callbackId =
        video.requestVideoFrameCallback(measureFrame);
    };

    if ("requestVideoFrameCallback" in video) {
      callbackId =
        video.requestVideoFrameCallback(measureFrame);
    }

    return () => {
      running = false;

      if (
        callbackId !== null &&
        "cancelVideoFrameCallback" in video
      ) {
        video.cancelVideoFrameCallback(callbackId);
      }
    };
  }, [cameraActive]);

  useEffect(() => {
    if (!cameraActive || !videoRef.current) {
      return;
    }

    const video = videoRef.current;

    const sampler = new FrameSampler(video, {
      targetFps: 15,
      width: 640,
      height: 360,

      onFrame: (frame) => {
        const start = performance.now();

        // This is deliberately empty for now.
        //
        // Later:
        //
        // frame.canvas
        //      ↓
        // VisionProvider
        //      ↓
        // landmarks
        //      ↓
        // gesture detection
        void frame;

        const processingTime =
          performance.now() - start;

        performanceRef.current.recordProcessingFrame(
          processingTime,
        );
      },
    });

    samplerRef.current = sampler;
    sampler.start();

    return () => {
      sampler.stop();
      samplerRef.current = null;
    };
  }, [cameraActive]);

  useEffect(() => {
    if (!cameraActive) {
      return;
    }

    const interval = window.setInterval(() => {
      const stats =
        performanceRef.current.getStats();

      setCameraFps(stats.cameraFps);
      setProcessingFps(stats.processingFps);
      setProcessingLatency(
        stats.processingLatencyMs,
      );
    }, 500);

    return () => {
      window.clearInterval(interval);
    };
  }, [cameraActive]);

  return (
    <main className="app">
      <header className="topbar">
        <div>
          <div className="brand">STREAM REACTION AI</div>
          <div className="subtitle">Your stream reacts to you.</div>
        </div>

        <div className={`status ${cameraActive ? "online" : ""}`}>
          <span className="status-dot" />
          {cameraActive ? "CAMERA ACTIVE" : "CAMERA OFF"}
        </div>
      </header>

      <section className="workspace">
        <div className="camera-panel">
          <div className="panel-header">
            <span>CAMERA FEED</span>
            <span className="resolution">
              {cameraActive ? "LIVE" : "WAITING"}
            </span>
          </div>

          <div className="video-container">
            {cameraActive ? (
              <video
                ref={videoRef}
                className="video"
                autoPlay
                playsInline
                muted
              />
            ) : (
              <div className="camera-placeholder">
                <div className="camera-icon">◉</div>
                <h2>Camera not active</h2>
                <p>
                  Start your camera to begin detecting your reactions.
                </p>
              </div>
            )}
          </div>

          {cameraError && (
            <div className="error-message">
              {cameraError}
            </div>
          )}

          <div className="camera-controls">
            {!cameraActive ? (
              <button className="primary-button" onClick={startCamera}>
                Start Camera
              </button>
            ) : (
              <button className="secondary-button" onClick={stopCamera}>
                Stop Camera
              </button>
            )}
          </div>
        </div>

        <aside className="detection-panel">
          <div className="panel-header">
            <span>DETECTION</span>
            <span className="resolution">M1</span>
          </div>

          <div className="detection-state">
            <div className="state-label">CURRENT EVENT</div>

            <div className="event-name">
              {cameraActive ? "Waiting..." : "—"}
            </div>

            <div className="state-description">
              {cameraActive
                ? "Vision system is ready."
                : "Start the camera to begin."}
            </div>
          </div>

          <div className="detection-divider" />

          <div className="detection-row">
            <span>Vision</span>
            <span>{cameraActive ? "READY" : "OFF"}</span>
          </div>

          <div className="detection-row">
            <span>Camera FPS</span>
            <span>{cameraActive ? `${cameraFps} FPS` : "—"}</span>
          </div>

          <div className="detection-row">
            <span>Processing FPS</span>
            <span>
              {cameraActive ? `${processingFps} FPS` : "—"}
            </span>
          </div>

          <div className="detection-row">
            <span>Processing</span>
            <span>
              {cameraActive
                ? `${processingLatency} ms`
                : "—"}
            </span>
          </div>

          <div className="detection-row">
            <span>Events</span>
            <span>0</span>
          </div>

          <div className="detection-row">
            <span>Reactions</span>
            <span>0</span>
          </div>
        </aside>
      </section>
    </main>
  );
}

export default App;

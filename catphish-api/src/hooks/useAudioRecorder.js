/**
 * useAudioRecorder — captures microphone audio and returns a WAV base64 string.
 *
 * Usage:
 *   const { isRecording, startRecording, stopRecording, audioBase64, error } = useAudioRecorder();
 */

import { useState, useRef, useCallback } from 'react';

/**
 * Convert an AudioBuffer to a WAV Blob (16-bit PCM, mono, 16 kHz).
 */
function audioBufferToWav(buffer) {
  const numChannels = 1;
  const sampleRate = 16000;

  // Resample to 16 kHz mono
  const offlineCtx = new OfflineAudioContext(numChannels, buffer.duration * sampleRate, sampleRate);
  const source = offlineCtx.createBufferSource();
  source.buffer = buffer;
  source.connect(offlineCtx.destination);
  source.start(0);
  return offlineCtx.startRendering().then((rendered) => {
    const samples = rendered.getChannelData(0);
    const dataLength = samples.length * 2; // 16-bit = 2 bytes per sample
    const headerLength = 44;
    const totalLength = headerLength + dataLength;
    const arrayBuffer = new ArrayBuffer(totalLength);
    const view = new DataView(arrayBuffer);

    // WAV header
    writeString(view, 0, 'RIFF');
    view.setUint32(4, totalLength - 8, true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true); // chunk size
    view.setUint16(20, 1, true);  // PCM
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * numChannels * 2, true); // byte rate
    view.setUint16(32, numChannels * 2, true); // block align
    view.setUint16(34, 16, true); // bits per sample
    writeString(view, 36, 'data');
    view.setUint32(40, dataLength, true);

    // PCM samples
    let offset = 44;
    for (let i = 0; i < samples.length; i++, offset += 2) {
      const s = Math.max(-1, Math.min(1, samples[i]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }

    return new Blob([arrayBuffer], { type: 'audio/wav' });
  });
}

function writeString(view, offset, str) {
  for (let i = 0; i < str.length; i++) {
    view.setUint8(offset + i, str.charCodeAt(i));
  }
}

/**
 * Convert Blob to base64 string (without data-URI prefix).
 */
function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const dataUrl = reader.result; // "data:audio/wav;base64,XXXX"
      const base64 = dataUrl.split(',')[1];
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

export default function useAudioRecorder() {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBase64, setAudioBase64] = useState(null);
  const [error, setError] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);

  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const streamRef = useRef(null);
  const timerRef = useRef(null);

  const startRecording = useCallback(async () => {
    setError(null);
    setAudioBase64(null);
    setRecordingTime(0);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });
      streamRef.current = stream;
      chunksRef.current = [];

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
          ? 'audio/webm;codecs=opus'
          : 'audio/webm',
      });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        // Build blob from chunks
        const blob = new Blob(chunksRef.current, { type: mediaRecorder.mimeType });

        try {
          // Decode to AudioBuffer then re-encode as WAV
          const arrayBuf = await blob.arrayBuffer();
          const audioCtx = new AudioContext({ sampleRate: 48000 });
          const decoded = await audioCtx.decodeAudioData(arrayBuf);
          audioCtx.close();

          const wavBlob = await audioBufferToWav(decoded);
          const base64 = await blobToBase64(wavBlob);
          setAudioBase64(base64);
        } catch (err) {
          console.error('Failed to convert audio to WAV:', err);
          // Fallback: just base64 the raw webm
          const base64 = await blobToBase64(blob);
          setAudioBase64(base64);
        }
      };

      mediaRecorder.start(250); // collect in 250ms chunks
      setIsRecording(true);

      // Timer
      timerRef.current = setInterval(() => {
        setRecordingTime((t) => t + 1);
      }, 1000);
    } catch (err) {
      console.error('Microphone access error:', err);
      setError('Microphone access denied. Please allow microphone access and try again.');
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    setIsRecording(false);
  }, []);

  const reset = useCallback(() => {
    setAudioBase64(null);
    setError(null);
    setRecordingTime(0);
  }, []);

  return { isRecording, audioBase64, error, recordingTime, startRecording, stopRecording, reset };
}

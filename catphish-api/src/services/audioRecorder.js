/**
 * Audio recording utilities for Catphish
 * Handles microphone recording and WAV conversion
 */

/**
 * Request microphone permission
 * @returns {Promise<MediaStream>} Audio stream
 */
export async function requestMicrophonePermission() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ 
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 16000,
      } 
    });
    console.log('✅ Microphone permission granted');
    return stream;
  } catch (error) {
    console.error('❌ Microphone permission denied:', error);
    throw new Error('Microphone permission denied. Please allow microphone access.');
  }
}

/**
 * Record audio from microphone
 * @param {MediaStream} stream - Audio stream from getUserMedia
 * @param {number} maxDurationMs - Maximum recording duration in milliseconds
 * @returns {Promise<Blob>} Recorded audio as Blob
 */
export function recordAudio(stream, maxDurationMs = 5000) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    
    // Try to find a supported mimeType
    let mimeType = 'audio/webm;codecs=opus';
    const supportedTypes = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/ogg;codecs=opus',
      'audio/mp4',
    ];
    
    for (const type of supportedTypes) {
      if (MediaRecorder.isTypeSupported(type)) {
        mimeType = type;
        break;
      }
    }
    
    console.log('Using mimeType:', mimeType);
    
    const mediaRecorder = new MediaRecorder(stream, { mimeType });

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    };

    mediaRecorder.onstop = () => {
      const blob = new Blob(chunks, { type: mimeType });
      console.log('✅ Recording stopped, blob size:', blob.size);
      resolve(blob);
    };

    mediaRecorder.onerror = (error) => {
      console.error('❌ MediaRecorder error:', error);
      reject(error);
    };

    mediaRecorder.start();
    console.log('🎤 Recording started...');

    // Auto-stop after max duration
    setTimeout(() => {
      if (mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
      }
    }, maxDurationMs);
  });
}

/**
 * Convert audio blob to WAV format
 * @param {Blob} audioBlob - Audio blob (any format)
 * @returns {Promise<Blob>} WAV audio blob
 */
export async function convertToWav(audioBlob) {
  // Create audio context
  const audioContext = new (window.AudioContext || window.webkitAudioContext)({
    sampleRate: 16000, // 16kHz for voice
  });

  // Read the blob as array buffer
  const arrayBuffer = await audioBlob.arrayBuffer();
  
  // Decode audio data
  const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
  
  // Convert to WAV
  const wavBlob = audioBufferToWav(audioBuffer);
  
  console.log('✅ Converted to WAV, size:', wavBlob.size);
  
  return wavBlob;
}

/**
 * Convert AudioBuffer to WAV blob
 * @param {AudioBuffer} audioBuffer - Web Audio API AudioBuffer
 * @returns {Blob} WAV blob
 */
function audioBufferToWav(audioBuffer) {
  const numChannels = audioBuffer.numberOfChannels;
  const sampleRate = audioBuffer.sampleRate;
  const format = 1; // PCM
  const bitDepth = 16;

  // Interleave channels if stereo, otherwise use mono
  let samples;
  if (numChannels === 2) {
    const left = audioBuffer.getChannelData(0);
    const right = audioBuffer.getChannelData(1);
    samples = interleave(left, right);
  } else {
    samples = audioBuffer.getChannelData(0);
  }

  const dataLength = samples.length * (bitDepth / 8);
  const buffer = new ArrayBuffer(44 + dataLength);
  const view = new DataView(buffer);

  // Write WAV header
  writeString(view, 0, 'RIFF');
  view.setUint32(4, 36 + dataLength, true);
  writeString(view, 8, 'WAVE');
  writeString(view, 12, 'fmt ');
  view.setUint32(16, 16, true); // Subchunk1Size
  view.setUint16(20, format, true);
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * numChannels * (bitDepth / 8), true); // ByteRate
  view.setUint16(32, numChannels * (bitDepth / 8), true); // BlockAlign
  view.setUint16(34, bitDepth, true);
  writeString(view, 36, 'data');
  view.setUint32(40, dataLength, true);

  // Write audio data
  floatTo16BitPCM(view, 44, samples);

  return new Blob([view], { type: 'audio/wav' });
}

/**
 * Interleave left and right audio channels
 */
function interleave(left, right) {
  const length = left.length + right.length;
  const result = new Float32Array(length);

  let inputIndex = 0;
  for (let i = 0; i < length;) {
    result[i++] = left[inputIndex];
    result[i++] = right[inputIndex];
    inputIndex++;
  }
  return result;
}

/**
 * Write string to DataView
 */
function writeString(view, offset, string) {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
}

/**
 * Convert float samples to 16-bit PCM
 */
function floatTo16BitPCM(view, offset, samples) {
  for (let i = 0; i < samples.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
}

/**
 * Convert blob to base64
 * @param {Blob} blob - Blob to convert
 * @returns {Promise<string>} Base64 string
 */
export function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      // Remove data URL prefix (e.g., "data:audio/wav;base64,")
      const base64 = reader.result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

/**
 * Stop all tracks in a media stream
 * @param {MediaStream} stream - Stream to stop
 */
export function stopStream(stream) {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    console.log('🛑 Stream stopped');
  }
}

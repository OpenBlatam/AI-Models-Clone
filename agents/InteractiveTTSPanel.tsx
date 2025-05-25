// components/InteractiveTTSPanel.tsx
import React, { useState, useEffect, useRef } from 'react';
import { Room, RoomEvent, RemoteParticipant } from 'livekit-client';
import styles from './InteractiveTTSPanel.module.css'; // Crearemos este archivo

// Iconos SVG simples (puedes reemplazarlos con una librería como lucide-react)
const SpeakerIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
    <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
  </svg>
);
const LoaderIcon = () => ( // Un spinner simple
  <svg className={styles.spinner} viewBox="0 0 50 50">
    <circle className={styles.path} cx="25" cy="25" r="20" fill="none" strokeWidth="5"></circle>
  </svg>
);

// Configuración de LiveKit (deberían estar en variables de entorno)
const LIVEKIT_URL = process.env.NEXT_PUBLIC_LIVEKIT_URL || 'ws://localhost:7880'; // Reemplaza con tu URL de LiveKit
const TEMP_TOKEN = process.env.NEXT_PUBLIC_TEMP_LIVEKIT_TOKEN || 'tu_token_temporal_aqui'; // REEMPLAZA ESTO

const InteractiveTTSPanel: React.FC = () => {
  const [text, setText] = useState<string>('');
  const [isLoadingTTS, setIsLoadingTTS] = useState<boolean>(false);
  const [ttsError, setTtsError] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  const [room, setRoom] = useState<Room | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [participants, setParticipants] = useState<RemoteParticipant[]>([]);
  const remoteMediaContainerRef = useRef<HTMLDivElement>(null);


  // Efecto para conectar/desconectar de LiveKit
  useEffect(() => {
    if (!LIVEKIT_URL || !TEMP_TOKEN || TEMP_TOKEN === 'tu_token_temporal_aqui') {
      console.warn("LiveKit URL or temporary token not set properly for demo.");
      return;
    }

    const newRoom = new Room({
      adaptiveStream: true,
      dynacast: true,
    });

    newRoom
      .on(RoomEvent.ParticipantConnected, (participant: RemoteParticipant) => {
        setParticipants((prev) => [...prev.filter(p => p.sid !== participant.sid), participant]);
      })
      .on(RoomEvent.ParticipantDisconnected, (participant: RemoteParticipant) => {
        setParticipants((prev) => prev.filter(p => p.sid !== participant.sid));
      })
      .on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
        if ((track.kind === 'audio' || track.kind === 'video') && remoteMediaContainerRef.current) {
          const element = track.attach();
          remoteMediaContainerRef.current.appendChild(element);
        }
      })
      .on(RoomEvent.TrackUnsubscribed, (track) => {
         track.detach().forEach(element => element.remove());
      })
      .on(RoomEvent.Disconnected, () => {
        setIsConnected(false);
        setParticipants([]);
      });

    const connectToRoom = async () => {
      try {
        await newRoom.connect(LIVEKIT_URL!, TEMP_TOKEN!);
        setIsConnected(true);
        setParticipants(Array.from(newRoom.participants.values()));
        setRoom(newRoom);
      } catch (error) {
        console.error('Failed to connect to LiveKit room:', error);
      }
    };

    connectToRoom();

    return () => {
      newRoom.disconnect();
    };
  }, []);


  const handleSynthesizeAndPlay = async () => {
    if (!text.trim()) {
      setTtsError('Por favor, introduce algún texto.');
      return;
    }
    setIsLoadingTTS(true);
    setTtsError(null);

    try {
      const response = await fetch('/api/tts-elevenlabs', { // Asume que esta API route existe
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Error HTTP: ${response.status}`);
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);

      if (audioRef.current) {
        audioRef.current.src = url;
        audioRef.current.play();
        audioRef.current.onended = () => {
          URL.revokeObjectURL(url); // Limpiar el object URL después de reproducir
        };
      }
    } catch (err: any) {
      console.error('Error al sintetizar voz:', err);
      setTtsError(err.message || 'Fallo al sintetizar la voz.');
    } finally {
      setIsLoadingTTS(false);
    }
  };

  return (
    <div className={styles.panelContainer}>
      <div className={styles.ttsSection}>
        <h2 className={styles.sectionTitle}>Voz IA con ElevenLabs</h2>
        <textarea
          className={styles.textArea}
          rows={5}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Escribe el texto que quieres convertir a voz..."
          disabled={isLoadingTTS}
        />
        <button
          className={styles.actionButton}
          onClick={handleSynthesizeAndPlay}
          disabled={isLoadingTTS}
        >
          {isLoadingTTS ? <LoaderIcon /> : <SpeakerIcon />}
          {isLoadingTTS ? 'Generando Audio...' : 'Escuchar con IA'}
        </button>
        {ttsError && <p className={styles.errorMessage}>{ttsError}</p>}
        <audio ref={audioRef} style={{ display: 'none' }} /> {/* Audio element for playback */}
      </div>

      <div className={styles.livekitSection}>
        <h2 className={styles.sectionTitle}>Sala en Vivo con LiveKit</h2>
        <div className={styles.status}>
          Estado: {isConnected ? <span className={styles.connected}>Conectado</span> : <span className={styles.disconnected}>Desconectado</span>}
          {isConnected && room && <span className={styles.roomName}> ({room.name})</span>}
        </div>
        <div className={styles.participantsList}>
          <strong>Participantes ({room?.participants.size || 0}):</strong>
          <ul>
            {participants.map(p => <li key={p.sid}>{p.identity}</li>)}
          </ul>
        </div>
        <div id="remote-media-container" ref={remoteMediaContainerRef} className={styles.remoteMedia}>
          {/* Las pistas de audio/video remotas se añadirán aquí */}
        </div>
      </div>
    </div>
  );
};

export default InteractiveTTSPanel;
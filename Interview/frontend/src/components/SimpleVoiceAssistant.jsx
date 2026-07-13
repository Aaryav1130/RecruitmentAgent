import {
    useVoiceAssistant,
    useLocalParticipant,
    VideoTrack,
    useParticipants,
    useTracks,
    useTranscriptions
} from "@livekit/components-react";
import { Track } from "livekit-client";
import { useEffect, useState, useMemo } from "react";
import "./SimpleVoiceAssistant.css";

const SimpleVoiceAssistant = ({ onDisconnect }) => {
    const { state, audioTrack, agentTranscription } = useVoiceAssistant();
    const localParticipant = useLocalParticipant();
    const participants = useParticipants();
    const transcriptions = useTranscriptions();
    const [isMuted, setIsMuted] = useState(false);
    const [isCameraOff, setIsCameraOff] = useState(false);
    const [showChat, setShowChat] = useState(false);

    // Sync microphone and camera state with participant
    useEffect(() => {
        if (localParticipant.localParticipant) {
            setIsMuted(!localParticipant.localParticipant.isMicrophoneEnabled);
            setIsCameraOff(!localParticipant.localParticipant.isCameraEnabled);
        }
    }, [localParticipant.localParticipant?.isMicrophoneEnabled, localParticipant.localParticipant?.isCameraEnabled]);

    // Find remote participants (agent)
    const remoteParticipants = useMemo(() => {
        const localIdentity = localParticipant.localParticipant?.identity;
        return participants.filter(p => p.identity !== localIdentity && p.identity !== localParticipant.localParticipant?.identity);
    }, [participants, localParticipant]);

    // Get all video tracks from all sources
    const allTracks = useTracks(
        [
            Track.Source.Camera,
            Track.Source.ScreenShare,
            Track.Source.Unknown
        ],
        {
            onlySubscribed: false,
        }
    );

    // Find the video track from the remote participant (agent/avatar)
    const avatarTrackRef = useMemo(() => {
        if (remoteParticipants.length === 0) {
            return null;
        }

        // Try to find video track from remote participants
        for (const participant of remoteParticipants) {
            // Check video track publications
            for (const publication of participant.videoTrackPublications.values()) {
                if (publication.track && publication.track.kind === Track.Kind.Video) {
                    // Find the corresponding trackRef
                    const trackRef = allTracks.find(
                        t => t.publication === publication || 
                        (t.participant?.identity === participant.identity && 
                         t.publication?.kind === Track.Kind.Video &&
                         t.publication?.source === Track.Source.Camera)
                    );
                    if (trackRef) return trackRef;
                }
            }
        }

        // Fallback: find any remote video track
        for (const trackRef of allTracks) {
            if (trackRef.participant &&
                remoteParticipants.some(p => p.identity === trackRef.participant.identity) &&
                trackRef.publication?.kind === Track.Kind.Video) {
                return trackRef;
            }
        }

        return null;
    }, [allTracks, remoteParticipants]);

    // Get local video track
    const localVideoTrackRef = useMemo(() => {
        if (!localParticipant.localParticipant) return null;
        
        // First try to find from track publications
        for (const publication of localParticipant.localParticipant.videoTrackPublications.values()) {
            if (publication.track && publication.track.kind === Track.Kind.Video) {
                const trackRef = allTracks.find(
                    t => t.publication === publication || 
                    (t.participant?.identity === localParticipant.localParticipant?.identity &&
                     t.publication?.kind === Track.Kind.Video &&
                     t.publication?.source === Track.Source.Camera)
                );
                if (trackRef) return trackRef;
            }
        }

        // Fallback: find any local video track
        return allTracks.find(trackRef =>
            trackRef.participant?.identity === localParticipant.localParticipant?.identity &&
            trackRef.publication?.kind === Track.Kind.Video &&
            trackRef.publication?.source === Track.Source.Camera
        );
    }, [allTracks, localParticipant]);

    // Toggle microphone
    const toggleMicrophone = async () => {
        if (localParticipant.localParticipant) {
            const micEnabled = localParticipant.localParticipant.isMicrophoneEnabled;
            const newMicState = !micEnabled;
            await localParticipant.localParticipant.setMicrophoneEnabled(newMicState);
            setIsMuted(!newMicState);
        }
    };

    // Toggle camera
    const toggleCamera = async () => {
        if (localParticipant.localParticipant) {
            const camEnabled = localParticipant.localParticipant.isCameraEnabled;
            const newCamState = !camEnabled;
            await localParticipant.localParticipant.setCameraEnabled(newCamState);
            setIsCameraOff(!newCamState);
        }
    };

    // // End call
    // const handleEndCall = () => {
    //     if (onDisconnect) {
    //         onDisconnect();
    //     }
    // };
    const handleEndCall = () => {
    if (chatMessages.length > 0) {
        // Send final chat messages to backend
        fetch("http://localhost:5001/process-chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(chatMessages),
        })
        .then(res => res.json())
        .then(data => console.log("Chat saved:", data))
        .catch(err => console.error("Failed to send chat:", err));
        }

    if (onDisconnect) {
        onDisconnect();
        }
    setTimeout(() => {
        window.close();  // Only works if tab was opened via JS
    }, 1000); // 1 seconds
    };


    // Format transcriptions for chat display
    const chatMessages = useMemo(() => {
        const messages = [];
        
        // Add transcriptions from useTranscriptions hook
        if (transcriptions && transcriptions.length > 0) {
            transcriptions.forEach(transcription => {
                messages.push({
                    text: transcription.text,
                    isUser: transcription.participant?.identity === localParticipant.localParticipant?.identity,
                    timestamp: new Date(transcription.timestamp || Date.now()).toLocaleTimeString()
                });
            });
        }
        
        // Add agent transcription from useVoiceAssistant if available
        if (agentTranscription) {
            messages.push({
                text: agentTranscription,
                isUser: false,
                timestamp: new Date().toLocaleTimeString()
            });
        }
        
        return messages;
    }, [transcriptions, agentTranscription, localParticipant]);


    return (
        <div className="interview-container">
            {/* Main Video Area */}
            <div className="video-area">
                {/* Avatar Video - Large Display */}
                <div className="avatar-display">
                    {avatarTrackRef ? (
                        <VideoTrack trackRef={avatarTrackRef} className="avatar-video" />
                    ) : (
                        <div className="avatar-placeholder">
                            <div className="loading-spinner"></div>
                            <p>Waiting for interviewer to join...</p>
                        </div>
                    )}
                </div>

                {/* Local Video - Small Picture-in-Picture */}
                {localVideoTrackRef && !isCameraOff && (
                    <div className="local-video-pip">
                        <VideoTrack trackRef={localVideoTrackRef} className="local-video" />
                    </div>
                )}
                {isCameraOff && (
                    <div className="local-video-pip camera-off">
                        <div className="camera-off-indicator">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M1 1L23 23M15 15V19L12 22H4L1 19V5L5 9M9 1H20L23 4V14M9 9L1 1" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                        </div>
                    </div>
                )}
            </div>

            {/* Control Bar */}
            <div className="interview-controls">
                <button
                    className={`control-btn ${isMuted ? 'active' : ''}`}
                    onClick={toggleMicrophone}
                    title={isMuted ? "Unmute" : "Mute"}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        {isMuted ? (
                            <path d="M12 1C10.34 1 9 2.34 9 4V11C9 12.66 10.34 14 12 14C13.66 14 15 12.66 15 11V4C15 2.34 13.66 1 12 1ZM19 11C19 14.53 16.39 17.44 13 17.93V21H11V17.93C7.61 17.44 5 14.53 5 11H7C7 13.76 9.24 16 12 16C14.76 16 17 13.76 17 11H19ZM1 1L23 23L1 1Z" fill="currentColor"/>
                        ) : (
                            <path d="M12 2C10.34 2 9 3.34 9 5V11C9 12.66 10.34 14 12 14C13.66 14 15 12.66 15 11V5C15 3.34 13.66 2 12 2ZM19 11C19 14.53 16.39 17.44 13 17.93V21H11V17.93C7.61 17.44 5 14.53 5 11H7C7 13.76 9.24 16 12 16C14.76 16 17 13.76 17 11H19Z" fill="currentColor"/>
                        )}
                    </svg>
                    <span>{isMuted ? "Unmute" : "Mute"}</span>
                </button>

                <button
                    className={`control-btn ${isCameraOff ? 'active' : ''}`}
                    onClick={toggleCamera}
                    title={isCameraOff ? "Turn on camera" : "Turn off camera"}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M23 19C23 19.5304 22.7893 20.0391 22.4142 20.4142C22.0391 20.7893 21.5304 21 21 21H3C2.46957 21 1.96086 20.7893 1.58579 20.4142C1.21071 20.0391 1 19.5304 1 19V8C1 7.46957 1.21071 6.96086 1.58579 6.58579C1.96086 6.21071 2.46957 6 3 6H7L9 4H15L17 6H21C21.5304 6 22.0391 6.21071 22.4142 6.58579C22.7893 6.96086 23 7.46957 23 8V19Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <circle cx="12" cy="13" r="4" stroke="currentColor" strokeWidth="2"/>
                    </svg>
                    <span>{isCameraOff ? "Camera On" : "Camera Off"}</span>
                </button>

                <button
                    className={`control-btn chat-btn ${showChat ? 'active' : ''}`}
                    onClick={() => setShowChat(!showChat)}
                    title="Toggle conversation history"
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    <span>Chat</span>
                </button>

                <button
                    className="control-btn end-call-btn"
                    onClick={handleEndCall}
                    title="End interview"
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M3 21L21 3M3 3L21 21" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    <span>End Call</span>
                </button>
            </div>

            {/* Chat Panel - Toggleable */}
            {showChat && (
                <div className="chat-panel">
                    <div className="chat-header">
                        <h3>Conversation History</h3>
                        <button onClick={() => setShowChat(false)} className="close-chat-btn">×</button>
                    </div>
                    <div className="chat-messages">
                        {chatMessages.length > 0 ? (
                            chatMessages.map((msg, idx) => (
                                <div key={idx} className={`chat-message ${msg.isUser ? 'user' : 'agent'}`}>
                                    <div className="message-header">
                                        <strong>{msg.isUser ? "You" : "Interviewer"}</strong>
                                        <span className="message-time">{msg.timestamp}</span>
                                    </div>
                                    <div className="message-content">{msg.text}</div>
                                </div>
                            ))
                        ) : (
                            <div className="no-messages">No messages yet. Start speaking to see transcriptions here.</div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default SimpleVoiceAssistant;

import { useState, useCallback } from "react";
import { LiveKitRoom, RoomAudioRenderer, PreJoin } from "@livekit/components-react";
import "@livekit/components-styles";
import SimpleVoiceAssistant from "./SimpleVoiceAssistant";

const LiveKitModal = ({ setShowSupport }) => {
    const [isSubmittingName, setIsSubmittingName] = useState(true);
    const [name, setName] = useState("");
    const [token, setToken] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [preJoinOptions, setPreJoinOptions] = useState(null);

    const getToken = useCallback(async (userName) => {
        setIsLoading(true);
        try {
            const response = await fetch(
                `/api/getToken?name=${encodeURIComponent(userName)}`
            );
            if (!response.ok) {
                const errorText = await response.text();
                console.error("Backend error:", errorText);
                alert("Failed to connect to the backend server. Please ensure the Flask Token Server (Terminal 2) is running and your LiveKit API keys are correct in the .env file.");
                setIsLoading(false);
                return;
            }
            const tokenData = await response.text();
            
            // Check if tokenData is a valid JWT (should not be HTML)
            if (tokenData.includes("<!DOCTYPE") || tokenData.includes("<html")) {
                alert("Received invalid token from server. The backend might have crashed or returned an error page.");
                setIsLoading(false);
                return;
            }
            
            setToken(tokenData);
            setIsSubmittingName(false);
            setIsLoading(false);
        } catch (error) {
            console.error("Error fetching token:", error);
            alert("Error fetching token. Is the Vite proxy running correctly?");
            setIsLoading(false);
        }
    }, []);

    const handleNameSubmit = (e) => {
        e.preventDefault();
        if (name.trim()) {
            getToken(name);
        }
    };

    const handlePreJoinSubmit = (values) => {
        // Store the user's media device preferences
        setPreJoinOptions(values);
        setIsConnected(true);
    };

    const handleDisconnect = () => {
        setShowSupport(false);
        setIsSubmittingName(true);
        setIsConnected(false);
        setIsLoading(false);
        setToken(null);
        setName("");
        setPreJoinOptions(null);
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content interview-modal">
                <div className="support-room">
                    {isSubmittingName && !isLoading ? (
                        <form onSubmit={handleNameSubmit} className="name-form">
                            <h2>Welcome to Your Interview</h2>
                            <div className="form-warning">
                                <strong>🚨Mandatory:</strong> Please ensure you are in a quiet environment and remove all background noise. 
                                Any disturbance may interrupt the interview call and lead to rejection.
                            </div>

                            <input
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="Your full name"
                                required
                                className="name-input"
                            />
                            <div className="form-buttons">
                                <button type="submit" className="primary-btn">Continue</button>
                                <button
                                    type="button"
                                    className="cancel-button"
                                    onClick={() => setShowSupport(false)}
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    ) : isLoading ? (
                        <div className="loading-screen">
                            <div className="spinner"></div>
                            <p>Connecting to interview room...</p>
                        </div>
                    ) : token && !isConnected ? (
                        // PreJoin is independent and outside LiveKitRoom
                        <PreJoin
                            onError={(err) => console.error("PreJoin error:", err)}
                            onSubmit={handlePreJoinSubmit}
                            onLeave={handleDisconnect}
                        />
                    ) : token && isConnected ? (
                        <LiveKitRoom
                            serverUrl={import.meta.env.VITE_LIVEKIT_URL}
                            token={token}
                            connect={true}
                            video={preJoinOptions?.videoEnabled !== false}
                            audio={preJoinOptions?.audioEnabled !== false}
                            options={{
                                adaptiveStream: true,
                                dynacast: true,
                                ...(preJoinOptions?.deviceId && {
                                    publishDefaults: {
                                        videoResolution: preJoinOptions.videoResolution,
                                        videoSimulcastLayers: preJoinOptions.videoSimulcastLayers,
                                    },
                                }),
                            }}
                            onDisconnected={handleDisconnect}
                        >
                            <RoomAudioRenderer />
                            <SimpleVoiceAssistant onDisconnect={handleDisconnect} />
                        </LiveKitRoom>
                    ) : null}
                </div>
            </div>
        </div>
    );
};

export default LiveKitModal;

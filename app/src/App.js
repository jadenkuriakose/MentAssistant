import React, { useState, useEffect } from "react";
import "./App.css";

const App = () => {
    const [messages, setMessages] = useState([]);
    const [isListening, setIsListening] = useState(false);
    const [recognition, setRecognition] = useState(null);
    const [voices, setVoices] = useState([]);
    const [selectedVoice, setSelectedVoice] = useState(null);

    useEffect(() => {
        const synth = window.speechSynthesis;

        const updateVoices = () => {
            const availableVoices = synth.getVoices();

            const filteredVoices = availableVoices.filter((voice) =>
                voice.lang.startsWith("en-") &&
                (
                    voice.name.includes("Samantha") ||
                    voice.name.includes("Karen") ||
                    voice.name.includes("Daniel") ||
                    voice.name.includes("Kate") ||
                    voice.name.includes("Google") ||
                    voice.name.includes("Microsoft")
                )
            );

            setVoices(filteredVoices);

            const defaultVoice =
                filteredVoices.find((voice) => voice.name.includes("Google UK English Female")) ||
                filteredVoices.find((voice) => voice.name.includes("Samantha")) ||
                filteredVoices[0];
            setSelectedVoice(defaultVoice);
        };

        if (synth.onvoiceschanged !== undefined) {
            synth.onvoiceschanged = updateVoices;
        } else {
            updateVoices();
        }
    }, []);

    const startListening = () => {
        if (!window.SpeechRecognition && !window.webkitSpeechRecognition) {
            alert("Your browser does not support the Web Speech API.");
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognitionInstance = new SpeechRecognition();
        recognitionInstance.continuous = true;

        recognitionInstance.onresult = (event) => {
            const transcript = event.results[event.resultIndex][0].transcript.trim();
            handleUserMessage(transcript);
        };

        recognitionInstance.start();
        setRecognition(recognitionInstance);
        setIsListening(true);
    };

    const stopListening = () => {
        if (recognition) {
            recognition.stop();
        }
        setIsListening(false);
    };

    const handleUserMessage = (text) => {
        const newMessages = [...messages, { role: "user", content: text }];
        setMessages(newMessages);

        fetch("http://127.0.0.1:8080/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: text, session_id: "session1" }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.response) {
                    const botMessage = { role: "bot", content: data.response };
                    setMessages((prevMessages) => [...prevMessages, botMessage]);
                    speakBotResponse(data.response);
                } else {
                    const errorMessage = { role: "bot", content: "An error occurred while processing your request." };
                    setMessages((prevMessages) => [...prevMessages, errorMessage]);
                }
            });
    };

    const speakBotResponse = (response) => {
        if (!selectedVoice) {
            alert("No voice selected! Please select a voice from the dropdown.");
            return;
        }

        const synth = window.speechSynthesis;
        const utterance = new SpeechSynthesisUtterance(response);


        synth.cancel();


        utterance.voice = selectedVoice;
        utterance.pitch = 1.2;
        utterance.rate = 0.9;

        synth.speak(utterance);
    };

    return (
        <div className="app">
            <div className="header">
                <h1>MentAssistant</h1>
            </div>
            <div className="chat-box">
                {messages.map((message, index) => (
                    <div key={index} className={message.role}>
                        {message.content}
                    </div>
                ))}
            </div>
            <div className="controls">
                <button onClick={startListening} disabled={isListening} className="button">
                    Start Listening
                </button>
                <button onClick={stopListening} disabled={!isListening} className="button">
                    Stop Listening
                </button>

                <div className="voice-selector">
                    <label htmlFor="voiceSelect">Choose a voice:</label>
                    <select
                        id="voiceSelect"
                        value={selectedVoice ? selectedVoice.name : ""}
                        onChange={(e) => {
                            const newVoice = voices.find((voice) => voice.name === e.target.value);
                            setSelectedVoice(newVoice);
                        }}
                    >
                        {voices.map((voice, index) => (
                            <option key={index} value={voice.name}>
                                {voice.name}
                            </option>
                        ))}
                    </select>
                </div>
            </div>
        </div>
    );
};

export default App;

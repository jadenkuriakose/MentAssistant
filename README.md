# MentAssistant

**MentAssistant** is a voice-enabled chatbot application that combines speech recognition and text-to-speech functionalities to create an interactive, hands-free user experience. Users can speak to the bot, and the application converts speech into text, sends it to a backend for processing, and reads the bot's responses aloud. The app supports multiple English voices for text-to-speech output, allowing users to select a preferred voice. Additionally, the chat history is displayed for visual reference, providing a seamless conversation experience.

The application uses **React** for the frontend, which handles the user interface and voice interaction. The **Flask** backend processes user input using a language model via the **Groq API**. The application also leverages the **Web Speech API** for speech recognition and speech synthesis. For enhanced conversation quality, **TextBlob** is used to analyze sentiment, assess potential risks in user input, and adjust the length of the bot's responses to ensure they are both contextually appropriate and concise. This combination of technologies provides an intuitive, voice-driven interaction for users while maintaining flexibility and responsiveness in its design.

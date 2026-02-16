import React, {useState, useEffect, useRef} from 'react'
import axios from 'axios'
import {Send, Trash2, MessageSquare} from 'lucide-react'
import './App.css'

const API_BASE_URL = process.env.NODE_ENV === 'production'
    ? '/api'
    : 'http://localhost:8000'

function App() {
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState('')
    const [sessionId, setSessionId] = useState(null)
    const [loading, setLoading] = useState(false)
    const messagesEndRef = useRef(null)

    useEffect(() => {
        createNewSession()
    }, [])

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({behavior: 'smooth'})
    }, [messages])

    const createNewSession = async () => {
        try {
            const response = await axios.post(`${API_BASE_URL}/session/new`)
            setSessionId(response.data.session_id)
            setMessages([{
                type: 'system',
                content: 'Вітаю! Я — ваш юридичний асистент з Кримінального кодексу України. Задайте мені будь-яке питання.'
            }])
        } catch (error) {
            console.error('Error creating session:', error)
        }
    }

    const sendMessage = async (e) => {
        e.preventDefault()
        if (!input.trim() || loading) return

        const userMessage = input.trim()
        setInput('')
        setMessages(prev => [...prev, {type: 'user', content: userMessage}])
        setLoading(true)

        try {
            const response = await fetch(`${API_BASE_URL}/query/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: userMessage,
                    session_id: sessionId
                }),
            })

            const reader = response.body.getReader()
            const decoder = new TextDecoder("utf-8")

            setMessages(prev => [...prev, {type: 'assistant', content: ""}])
            setLoading(false)

            while (true) {
                const {done, value} = await reader.read()
                if (done) break

                const chunk = decoder.decode(value, {stream: true})

                setMessages(prev => {
                    const newMessages = [...prev]
                    const lastIndex = newMessages.length - 1
                    newMessages[lastIndex] = {
                        ...newMessages[lastIndex],
                        content: newMessages[lastIndex].content + chunk
                    }
                    return newMessages
                })
            }

        } catch (error) {
            console.error('Streaming error:', error)
            setMessages(prev => [...prev, {
                type: 'error',
                content: 'Вибачте, сталася помилка. Спробуйте ще раз.'
            }])
        } finally {
            setLoading(false)
        }
    }

    const clearChat = async () => {
        if (!sessionId) return

        try {
            await axios.post(`${API_BASE_URL}/session/${sessionId}/clear`)
            setMessages([{
                type: 'system',
                content: 'Історія розмови очищена. Можете задати нове питання.'
            }])
        } catch (error) {
            console.error('Error clearing chat:', error)
        }
    }

    return (
        <div className="App">
            <header className="header">
                <div className="header-content">
                    <MessageSquare size={32} className="header-icon"/>
                    <div>
                        <h1>Кримінальний кодекс України</h1>
                        <p>Юридичний асистент на базі AI</p>
                    </div>
                </div>
                <button onClick={clearChat} className="clear-btn" title="Очистити історію">
                    <Trash2 size={20}/>
                </button>
            </header>

            <div className="chat-container">
                <div className="messages">
                    {messages.map((msg, index) => (
                        <div key={index} className={`message ${msg.type}`}>
                            <div className="message-content">
                                {msg.content}
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="message assistant">
                            <div className="message-content thinking">
                                ...
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef}/>
                </div>

                <form onSubmit={sendMessage} className="input-form">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Задайте питання про Кримінальний кодекс..."
                        disabled={loading}
                        className="input-field"
                    />
                    <button
                        type="submit"
                        disabled={loading || !input.trim()}
                        className="send-btn"
                    >
                        <Send size={20}/>
                    </button>
                </form>
            </div>
        </div>
    )
}

export default App